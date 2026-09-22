"""probe_01_counts.py -- structure and counts for the two Park Grass protocols.

Reads the two e-RA xlsx files (species_data sheet) and reports, per protocol:
  sheet names; distinct (plot, sub_plot) count; rows per (plot, sub_plot, year)
  as the quadrat-count proxy (min/median/max); species count; fraction of zero
  entries; the treatment table as read; unmanured plot ids as the file names them.
Then it flags each STAGE1 [A] assumption it can test as CONFIRMED or CONTRADICTED.

Windows-safe: pandas/openpyxl only. Prints a summary and writes
results/probe_01_counts.json.
"""
import os
import glob
import json
import statistics

import pandas as pd

LANE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(LANE, "data", "raw")
RESULTS = os.path.join(LANE, "results")

METADATA = [
    "site", "plot_id", "plot", "split_plot", "sub_plot", "sample_year",
    "treatments", "n_factor_level", "n_rate", "p_factor_level", "p_rate",
    "k_factor_level", "k_rate", "mg_factor_level", "mg_rate", "na_factor_level",
    "na_rate", "si_factor_level", "si_rate", "liming_factor_level", "liming_rate",
    "fym_factor_level", "fym_rate", "fm_factor_level", "fm_n_rate",
    "pm_factor_level", "pm_n_rate",
]
NUTRIENT_RATES = ["n_rate", "p_rate", "k_rate", "mg_rate", "na_rate", "si_rate",
                  "fym_rate", "fm_n_rate", "pm_n_rate"]
TARGET_PH = {"a": "7", "b": "6", "c": "5", "d": "unlimed"}  # design constant, not in file

PROTOCOLS = {
    "1991-2000": os.path.join(RAW, "1991-2000"),
    "2010-2012": os.path.join(RAW, "2010-2012"),
}


def find_xlsx(folder):
    hits = glob.glob(os.path.join(folder, "*.xlsx"))
    if not hits:
        raise FileNotFoundError("no xlsx in " + folder)
    return hits[0]


def species_cols(cols):
    return [c for c in cols if c not in METADATA and c != "note_id"]


def to_num(df, cols):
    return df[cols].apply(pd.to_numeric, errors="coerce")


def analyse(label, folder):
    path = find_xlsx(folder)
    xl = pd.ExcelFile(path)
    sheets = list(xl.sheet_names)
    df = pd.read_excel(path, sheet_name="species_data")
    df.columns = [str(c).strip() for c in df.columns]

    # clean whitespace on string key/treatment columns
    str_cols = ["plot", "split_plot", "sub_plot", "treatments", "liming_factor_level",
                "n_factor_level", "p_factor_level", "k_factor_level", "plot_id"]
    for c in str_cols:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip().replace({"nan": ""})

    sp = species_cols(df.columns)
    spnum = to_num(df, sp)

    # distinct sub-plots (cleaned keys)
    key_cols = ["plot", "split_plot", "sub_plot"]
    df["_split"] = df["split_plot"]
    distinct_ps = df.drop_duplicates(subset=["plot", "sub_plot"]).shape[0]
    distinct_pss = df.drop_duplicates(subset=key_cols).shape[0]

    # rows per (plot, split_plot, sub_plot, year) = quadrat-count proxy
    grp = df.groupby(["plot", "_split", "sub_plot", "sample_year"]).size()
    rows_per = grp.tolist()
    quad = dict(min=int(min(rows_per)), median=float(statistics.median(rows_per)),
                max=int(max(rows_per)),
                note="rows per (plot,sub_plot,year); the open release gives one "
                     "aggregated percent-biomass row per sub-plot-year, so per-quadrat "
                     "data are NOT present")

    # zero fraction over the species matrix
    total = int(spnum.size)
    n_zero = int((spnum == 0).sum().sum())
    n_nan = int(spnum.isna().sum().sum())
    zero_frac = n_zero / total if total else None

    years = sorted(int(y) for y in df["sample_year"].dropna().unique())

    # unmanured plots: the 'Nil' treatment label (never fertilised or manured)
    df["_nil"] = df["treatments"].str.lower() == "nil"
    unmanured_plots = sorted(df.loc[df["_nil"], "plot"].unique(),
                             key=lambda s: (len(s), s))
    # for transparency, also the looser "all current nutrient rates zero" set
    ratesnum = to_num(df, NUTRIENT_RATES).fillna(0)
    zero_rate_plots = sorted(df.loc[(ratesnum == 0).all(axis=1), "plot"].unique(),
                             key=lambda s: (len(s), s))
    nil_treatments = sorted(df.loc[df["_nil"], "treatments"].unique())

    # treatment table as read: distinct whole-plot nutrient combos
    tt_cols = ["plot", "treatments", "n_factor_level", "n_rate", "p_factor_level",
               "p_rate", "k_factor_level", "k_rate"]
    tt = (df[tt_cols].astype(str).drop_duplicates()
          .sort_values("plot").to_dict("records"))
    lime_letters = sorted(df["liming_factor_level"].astype(str).dropna().unique())

    # N dose map as read
    n_dose = (df[["n_factor_level", "n_rate"]].astype(str).drop_duplicates()
              .sort_values("n_factor_level").to_dict("records"))

    return dict(
        protocol=label,
        xlsx=os.path.basename(path),
        sheet_names=sheets,
        distinct_plot_subplot=int(distinct_ps),
        distinct_plot_split_subplot=int(distinct_pss),
        n_rows=int(df.shape[0]),
        years=years,
        n_years=len(years),
        quadrats_per_subplot_year=quad,
        species_count=len(sp),
        zero_entries=n_zero,
        nan_entries=n_nan,
        total_species_entries=total,
        zero_fraction=zero_frac,
        unmanured_plots=unmanured_plots,
        unmanured_treatment_labels=nil_treatments,
        zero_current_rate_plots=zero_rate_plots,
        lime_subplot_letters=lime_letters,
        n_dose_levels=n_dose,
        treatment_table=tt,
        target_ph_design_constant=TARGET_PH,
    )


def verdicts(res):
    """Flag STAGE1 [A] assumptions as CONFIRMED / CONTRADICTED with value found."""
    v = []
    r1 = res["1991-2000"]
    r2 = res["2010-2012"]

    # [A] unmanured plots are plot 3 and plot 12
    found = set(r1["unmanured_plots"])
    guess = {"3", "12"}
    v.append(dict(item="[A] unmanured plots are 3 and 12",
                  verdict="CONFIRMED" if found == guess else "CONTRADICTED",
                  value_found="1991-2000 unmanured plots = " + str(r1["unmanured_plots"])))

    # [A] N doses N1/N2/N3 ~ 48/96/144
    dose = {d["n_factor_level"]: d["n_rate"] for d in r1["n_dose_levels"]}
    ok = dose.get("N1") == "48" and dose.get("N2") == "96" and dose.get("N3") == "144"
    v.append(dict(item="[A] N1/N2/N3 = 48/96/144 kg N/ha",
                  verdict="CONFIRMED" if ok else "CONTRADICTED",
                  value_found="N1=%s N2=%s N3=%s" % (dose.get("N1"), dose.get("N2"),
                                                     dose.get("N3"))))

    # [A] ~20 main plots
    nplots = len(set(str(x["plot"]) for x in r1["treatment_table"]))
    v.append(dict(item="[A] about 20 main plots",
                  verdict="CONFIRMED" if 15 <= nplots <= 25 else "CONTRADICTED",
                  value_found="1991-2000 distinct main plots = " + str(nplots)))

    # [A] lime sub-plots a/b/c/d
    ok = set(r1["lime_subplot_letters"]) >= {"a", "b", "c", "d"}
    v.append(dict(item="[A] lime sub-plots a/b/c/d exist",
                  verdict="CONFIRMED" if ok else "CONTRADICTED",
                  value_found="lime letters = " + str(r1["lime_subplot_letters"])))

    # [A] ~100 sub-plots surveyed 1991-2000 (true env granularity = plot,split,sub)
    n = r1["distinct_plot_split_subplot"]
    v.append(dict(item="[A] about 100 sub-plots surveyed 1991-2000",
                  verdict="CONFIRMED" if 80 <= n <= 120 else "CONTRADICTED",
                  value_found="distinct (plot,split_plot,sub_plot) 1991-2000 = %d "
                  "(distinct (plot,sub_plot) = %d)"
                  % (n, r1["distinct_plot_subplot"])))

    # [A] 2010-2012 is selected plots only, 3 years
    fewer = r2["distinct_plot_subplot"] < r1["distinct_plot_subplot"]
    v.append(dict(item="[A] 2010-2012 covers SELECTED plots only",
                  verdict="CONFIRMED" if fewer else "CONTRADICTED",
                  value_found="distinct (plot,sub_plot): 2010-2012=%d vs 1991-2000=%d"
                  % (r2["distinct_plot_subplot"], r1["distinct_plot_subplot"])))
    v.append(dict(item="[A] 2010-2012 spans about 3 years",
                  verdict="CONFIRMED" if r2["n_years"] <= 4 else "CONTRADICTED",
                  value_found="2010-2012 years = " + str(r2["years"])))

    # [V-in-STAGE1 but test] 6 quadrats / 60 samples per sub-plot per protocol
    q = r1["quadrats_per_subplot_year"]
    contradicted = q["max"] == 1
    v.append(dict(item="[STAGE1 marked V] 6 quadrats -> 60 samples per sub-plot",
                  verdict="CONTRADICTED" if contradicted else "CONFIRMED",
                  value_found="rows per sub-plot-year min/median/max = %d/%s/%d; "
                  "no per-quadrat data in the open release"
                  % (q["min"], q["median"], q["max"])))
    return v


def main():
    os.makedirs(RESULTS, exist_ok=True)
    res = {label: analyse(label, folder) for label, folder in PROTOCOLS.items()}
    res["stage1_A_verdicts"] = verdicts(res)

    out = os.path.join(RESULTS, "probe_01_counts.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(res, f, indent=2)

    for label in PROTOCOLS:
        r = res[label]
        print("=" * 70)
        print("PROTOCOL", label, "(", r["xlsx"], ")")
        print("  sheets:", r["sheet_names"])
        print("  distinct (plot, sub_plot):", r["distinct_plot_subplot"])
        print("  distinct (plot, split_plot, sub_plot):", r["distinct_plot_split_subplot"])
        print("  rows:", r["n_rows"], " years:", r["years"])
        print("  rows per (plot,sub_plot,year) min/median/max:",
              r["quadrats_per_subplot_year"]["min"],
              r["quadrats_per_subplot_year"]["median"],
              r["quadrats_per_subplot_year"]["max"])
        print("  species count:", r["species_count"])
        print("  zero fraction: %.4f (%d of %d; nan=%d)"
              % (r["zero_fraction"], r["zero_entries"], r["total_species_entries"],
                 r["nan_entries"]))
        print("  unmanured plots (as named):", r["unmanured_plots"],
              " labels:", r["unmanured_treatment_labels"])
        print("  lime letters:", r["lime_subplot_letters"])
    print("=" * 70)
    print("STAGE1 [A] verdicts:")
    for v in res["stage1_A_verdicts"]:
        print("  %-11s %s | %s" % (v["verdict"], v["item"], v["value_found"]))
    print("written:", out)


if __name__ == "__main__":
    main()
