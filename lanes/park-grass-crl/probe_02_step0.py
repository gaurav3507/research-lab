"""probe_02_step0.py -- step-0 false-fire gate for park-grass-crl (1991-2000).

Screen arithmetic is IMPORTED from meridian-causalbench causalbench/scripts/
03_screen.py via importlib (fit_pca, project, coefs, offdiag, N_PAIRS), the same
pattern as 40_screen_norman.py. Only the step-0 outer loop is duplicated here.

IMPORTANT DATA CAVEAT: the open e-RA release has no per-quadrat rows; the finest
within-sub-plot replication unit is the yearly (plot, split_plot, sub_plot, year)
percent-biomass row (at most 10 per sub-plot for 1991-2000). STAGE1's step-0 gate
shuffles quadrats within unmanured sub-plots; with no quadrats, the yearly row is
used as the quadrat proxy. This is a substitution, stated in the output.

Preprocessing follows STAGE1 "Preprocessing decisions":
  - control basis = unmanured (Nil) sub-plots, unlimed (d);
  - drop species with zero mass across the control basis;
  - multiplicative replacement, pseudocount = half the minimum non-zero proportion
    (recorded); centred log-ratio (CLR);
  - PCA basis fit on control only, d_proj = 5.

Two step-0 configurations are scored:
  A. homogeneous null: pseudo-environments drawn only from unmanured UNLIMED (d)
     samples (the true basis). If fewer than 4 environments can be formed at the
     required size, this is reported as environment starvation (ABORT).
  B. pooled-unmanured: pseudo-environments drawn from all unmanured (Nil) sub-plots
     (a/b/c/d). This has more samples but mixes lime levels, so its null is not
     perfectly homogeneous; reported with that caveat.

For each configuration: pseudo-environment size = smallest real treatment sub-plot n
(yearly samples); 200 shuffles; seeds 0-4; a shuffle "fires" if mean_ratio_pairs
> 1.1 (outside meridian's step-0 pass band). False-fire rate is reported per seed
and pooled. Writes results/probe_02/step0.json.
"""
import os
import sys
import json
import shutil
import importlib.util

import numpy as np
import pandas as pd

LANE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(LANE, "data", "raw")
RESULTS = os.path.join(LANE, "results")
PROBE_DIR = os.path.join(RESULTS, "probe_02")
SCREEN_03 = r"C:\Users\HOME\meridian-causalbench\causalbench\scripts\03_screen.py"

D_PROJ = 5
N_SHUFFLES = 200
SEEDS = [0, 1, 2, 3, 4]
FIRE_THRESHOLD = 1.1  # meridian step-0 pass band is 0.9..1.1

METADATA = [
    "site", "plot_id", "plot", "split_plot", "sub_plot", "sample_year",
    "treatments", "n_factor_level", "n_rate", "p_factor_level", "p_rate",
    "k_factor_level", "k_rate", "mg_factor_level", "mg_rate", "na_factor_level",
    "na_rate", "si_factor_level", "si_rate", "liming_factor_level", "liming_rate",
    "fym_factor_level", "fym_rate", "fm_factor_level", "fm_n_rate",
    "pm_factor_level", "pm_n_rate",
]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCREEN = load_module(SCREEN_03, "_screen03")
fit_pca = SCREEN.fit_pca
project = SCREEN.project
coefs = SCREEN.coefs
offdiag = SCREEN.offdiag
N_PAIRS = SCREEN.N_PAIRS


def load_species():
    import glob
    path = glob.glob(os.path.join(RAW, "1991-2000", "*.xlsx"))[0]
    df = pd.read_excel(path, sheet_name="species_data")
    df.columns = [str(c).strip() for c in df.columns]
    for c in ["plot", "split_plot", "sub_plot", "treatments", "liming_factor_level"]:
        df[c] = df[c].astype(str).str.strip().replace({"nan": ""})
    species = [c for c in df.columns if c not in METADATA and c != "note_id"]
    X = df[species].apply(pd.to_numeric, errors="coerce").fillna(0.0).to_numpy(float)
    return df, species, X


def clr_transform(P, pseudocount):
    """Multiplicative replacement of zeros then centred log-ratio, row-wise."""
    R = P.copy().astype(float)
    out = np.empty_like(R)
    for i in range(R.shape[0]):
        row = R[i]
        s = row.sum()
        if s <= 0:
            out[i] = 0.0
            continue
        p = row / s
        zero = p == 0
        nz = ~zero
        rep = p.copy()
        rep[zero] = pseudocount
        rep[nz] = p[nz] * (1.0 - pseudocount * zero.sum())
        rep[rep <= 0] = pseudocount
        logr = np.log(rep)
        out[i] = logr - logr.mean()
    return out


def score_step0(Z, m, rng):
    """One shuffle: carve Z rows into envs of size m, return mean_ratio_pairs and
    coef_ratio_pairs (precision readout), mirroring 03_screen.py step-0 math."""
    n = Z.shape[0]
    k = n // m
    if k < 4:
        return None
    idx = rng.permutation(n)
    envs = [idx[i * m:(i + 1) * m] for i in range(k)]
    half = m // 2

    within_m, within_c = [], []
    for e in envs:
        Za, Zb = Z[e[:half]], Z[e[half:m]]
        within_m.append(np.linalg.norm(Za.mean(0) - Zb.mean(0)))
        within_c.append(np.abs(offdiag(coefs(Za)) - offdiag(coefs(Zb))))

    pair_m, pair_c = [], []
    n_pairs = min(N_PAIRS, k * (k - 1) // 2)
    for _ in range(n_pairs):
        i, j = rng.choice(k, 2, replace=False)
        Za = Z[rng.choice(envs[i], half, replace=False)]
        Zb = Z[rng.choice(envs[j], half, replace=False)]
        pair_m.append(np.linalg.norm(Za.mean(0) - Zb.mean(0)))
        pair_c.append(np.abs(offdiag(coefs(Za)) - offdiag(coefs(Zb))))

    wm = np.median(within_m)
    wc = np.median(np.concatenate(within_c))
    return dict(mean_ratio_pairs=float(np.median(pair_m) / wm) if wm else float("nan"),
                coef_ratio_pairs=float(np.median(np.concatenate(pair_c)) / wc)
                if wc else float("nan"),
                n_envs=k)


def run_config(name, Z_pool, m):
    if m < 2:
        return dict(config=name, aborted="smallest_real_n < 2", pool_n=int(Z_pool.shape[0]),
                    env_size=int(m))
    k = Z_pool.shape[0] // m
    if k < 4:
        return dict(config=name, aborted="fewer than 4 pseudo-environments at env "
                    "size %d (environment starvation)" % m,
                    pool_n=int(Z_pool.shape[0]), env_size=int(m), n_envs=int(k))
    per_seed = []
    total_fire = 0
    total = 0
    all_mrp = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        fires = 0
        mrps = []
        for _ in range(N_SHUFFLES):
            s = score_step0(Z_pool, m, rng)
            mrps.append(s["mean_ratio_pairs"])
            if s["mean_ratio_pairs"] > FIRE_THRESHOLD:
                fires += 1
        per_seed.append(dict(seed=seed, shuffles=N_SHUFFLES, fires=fires,
                             false_fire_rate=fires / N_SHUFFLES,
                             mean_ratio_pairs_median=float(np.median(mrps))))
        total_fire += fires
        total += N_SHUFFLES
        all_mrp.extend(mrps)
    return dict(config=name, pool_n=int(Z_pool.shape[0]), env_size=int(m),
                n_envs=int(k), per_seed=per_seed,
                pooled_false_fire_rate=total_fire / total,
                pooled_shuffles=total,
                mean_ratio_pairs_median_overall=float(np.median(all_mrp)))


def main():
    shutil.rmtree(PROBE_DIR, ignore_errors=True)
    os.makedirs(PROBE_DIR, exist_ok=True)

    df, species, X = load_species()
    nil = df["treatments"].str.lower() == "nil"
    unlimed = df["liming_factor_level"].str.lower() == "d"

    basis_mask = (nil & unlimed).to_numpy()
    pool_mask = nil.to_numpy()

    # smallest real (non-Nil) treatment sub-plot n, in yearly samples
    real = df[~nil]
    real_sizes = real.groupby(["plot", "split_plot", "sub_plot"]).size()
    smallest_real_n = int(real_sizes.min())
    n_real_subplots = int(real_sizes.shape[0])
    n_ge_threshold = int((real_sizes >= smallest_real_n).sum())
    n_ge_10 = int((real_sizes >= 10).sum())

    # live species: nonzero mass across the control basis
    basis_sum = X[basis_mask].sum(0)
    live = basis_sum > 0
    n_live = int(live.sum())

    Xlive = X[:, live]
    # proportions for pseudocount: over the pooled unmanured working matrix
    Ppool = Xlive[pool_mask]
    rowsums = Ppool.sum(1, keepdims=True)
    prop = np.divide(Ppool, rowsums, out=np.zeros_like(Ppool), where=rowsums > 0)
    nonzero = prop[prop > 0]
    pseudocount = float(0.5 * nonzero.min()) if nonzero.size else 0.0

    # CLR on the full live matrix, then split into basis / pool
    clr_all = clr_transform(Xlive, pseudocount)
    mu, W = fit_pca(clr_all[basis_mask], D_PROJ)
    Z_all = project(clr_all, mu, W, set())
    Z_basis = Z_all[basis_mask]
    Z_pool = Z_all[pool_mask]

    cfgA = run_config("A_unmanured_unlimed_d_homogeneous", Z_basis, smallest_real_n)
    cfgB = run_config("B_pooled_unmanured_all_lime", Z_pool, smallest_real_n)

    primary = cfgB  # the computable configuration
    if "pooled_false_fire_rate" in primary:
        kill2 = primary["pooled_false_fire_rate"] > 0.10
        kill2_val = primary["pooled_false_fire_rate"]
    else:
        kill2 = None
        kill2_val = primary.get("aborted")

    result = dict(
        protocol="1991-2000",
        sample_unit="(plot, split_plot, sub_plot, year) row; per-quadrat data absent, "
                    "yearly row used as quadrat proxy",
        d_proj=D_PROJ,
        pseudocount=pseudocount,
        n_live_species=n_live,
        n_species_total=len(species),
        control_basis_n=int(basis_mask.sum()),
        unmanured_pool_n=int(pool_mask.sum()),
        smallest_real_treatment_subplot_n=smallest_real_n,
        n_real_treatment_subplots=n_real_subplots,
        real_subplot_n_min_median_max=[int(real_sizes.min()),
                                       float(real_sizes.median()),
                                       int(real_sizes.max())],
        n_real_subplots_ge_smallest_threshold=n_ge_threshold,
        n_real_subplots_ge_10=n_ge_10,
        config_A_homogeneous=cfgA,
        config_B_pooled=cfgB,
        kill_criterion_1=dict(
            definition="fewer than 8 treatment sub-plots with n >= smallest-env "
                       "threshold (= smallest real treatment sub-plot n)",
            n_subplots_meeting=n_ge_threshold,
            met=bool(n_ge_threshold < 8),
            note="literal count is not the binding limit; every sub-plot has at most "
                 "%d yearly samples because per-quadrat data are not published, which "
                 "is the real starvation" % int(real_sizes.max())),
        kill_criterion_2=dict(
            definition="pooled step-0 false-fire rate above 10 percent",
            pooled_false_fire_rate=kill2_val,
            met=kill2,
            config_A_status=cfgA.get("aborted", "ran")),
    )

    out = os.path.join(PROBE_DIR, "step0.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2)

    print("pseudocount:", pseudocount)
    print("live species:", n_live, "/", len(species))
    print("control basis n (Nil, unlimed d):", int(basis_mask.sum()))
    print("unmanured pool n (Nil, all lime):", int(pool_mask.sum()))
    print("smallest real treatment sub-plot n:", smallest_real_n,
          " real sub-plots:", n_real_subplots,
          " (n>=threshold:", n_ge_threshold, ", n>=10:", n_ge_10, ")")
    print("CONFIG A (homogeneous, unlimed d):", cfgA.get("aborted", "ran"))
    if "per_seed" in cfgA:
        for s in cfgA["per_seed"]:
            print("   seed", s["seed"], "false-fire", s["false_fire_rate"])
        print("   pooled false-fire:", cfgA["pooled_false_fire_rate"])
    print("CONFIG B (pooled unmanured):", cfgB.get("aborted", "ran"))
    if "per_seed" in cfgB:
        for s in cfgB["per_seed"]:
            print("   seed", s["seed"], "false-fire", s["false_fire_rate"])
        print("   pooled false-fire:", cfgB["pooled_false_fire_rate"])
    print("kill 1 met:", result["kill_criterion_1"]["met"])
    print("kill 2 met:", result["kill_criterion_2"]["met"])
    print("written:", out)


if __name__ == "__main__":
    main()
