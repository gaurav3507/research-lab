"""Download the two Park Grass e-RA datasets into data/raw/ and write MANIFEST.md.

Windows-safe: uses requests for downloads and Python zipfile for extraction, no
curl or shell string handling. Raw data is gitignored; MANIFEST.md is tracked.

Datasets (e-RA, electronic Rothamsted Archive):
  DOI 10.23637/rpg5-species_1991-2000-01  (protocol 1, 1991-2000)
  DOI 10.23637/rpg5-species_2010-2012-01  (protocol 2, 2010-2012)

Dataset 1 offers a direct xlsx plus a frictionless zip of CSVs. Dataset 2 offers a
frictionless zip that contains both the xlsx and the CSVs (its bare xlsx URL 404s
to HTML), so its xlsx is taken from the zip. The two datasets ship CSVs with
identical names, so each dataset is written to its own subfolder under data/raw/.
"""
import os
import sys
import shutil
import hashlib
import zipfile
import datetime

import requests

LANE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(LANE, "data", "raw")
MANIFEST = os.path.join(LANE, "data", "MANIFEST.md")
HEAD = {"User-Agent": "research-lab park-grass-crl feasibility probe"}

BASE1 = "https://www.era.rothamsted.ac.uk/metadata/rpg5/OAPGspecies9100/"
BASE2 = "https://www.era.rothamsted.ac.uk/metadata/rpg5/OAPGspecies0012/"

DOI1 = "10.23637/rpg5-species_1991-2000-01"
DOI2 = "10.23637/rpg5-species_2010-2012-01"
SUBDIR = {DOI1: "1991-2000", DOI2: "2010-2012"}

# (doi, url, kind, required)
TARGETS = [
    (DOI1, BASE1 + "rpg5_species_1991-2000_01.xlsx", "xlsx", True),
    (DOI1, BASE1 + "01-OAPGspecies9100.zip", "zip", False),
    (DOI2, BASE2 + "01-OAPGspecies0012.zip", "zip", True),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_utc():
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")


def download(url, dest):
    r = requests.get(url, headers=HEAD, timeout=180, stream=True)
    if r.status_code != 200:
        return None, r.status_code, r.headers.get("Content-Type", "")
    with open(dest, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
    return dest, r.status_code, r.headers.get("Content-Type", "")


def is_pkzip(path):
    with open(path, "rb") as f:
        return f.read(2) == b"PK"


def record(records, doi, url, path, source):
    rel = os.path.relpath(path, RAW).replace(os.sep, "/")
    records.append(dict(doi=doi, url=url, filename=rel,
                        sha256=sha256_of(path), size=os.path.getsize(path),
                        downloaded=now_utc(), source=source))


def main():
    shutil.rmtree(RAW, ignore_errors=True)
    os.makedirs(RAW, exist_ok=True)
    records = []
    have_xlsx = {DOI1: False, DOI2: False}

    for doi, url, kind, required in TARGETS:
        sub = os.path.join(RAW, SUBDIR[doi])
        os.makedirs(sub, exist_ok=True)
        fname = url.rsplit("/", 1)[-1]
        dest = os.path.join(sub, fname)
        got, status, ctype = download(url, dest)
        if got is None:
            if required:
                print(f"ERROR required file failed: {url} HTTP {status}")
                sys.exit(2)
            print(f"[skip optional] {fname} HTTP {status}")
            continue
        if kind in ("xlsx", "zip") and not is_pkzip(dest):
            print(f"ERROR {fname} is not a PKZIP container (content-type={ctype})")
            os.remove(dest)
            if required:
                sys.exit(3)
            continue
        record(records, doi, url, dest, "direct download")
        if kind == "xlsx":
            have_xlsx[doi] = True
        print(f"[ok] {SUBDIR[doi]}/{fname} {os.path.getsize(dest)} bytes")

        if kind == "zip":
            with zipfile.ZipFile(dest) as z:
                for member in z.namelist():
                    low = member.lower()
                    is_csv = low.endswith(".csv")
                    is_xlsx = low.endswith(".xlsx")
                    if not (is_csv or (is_xlsx and not have_xlsx[doi])):
                        continue
                    out_name = os.path.basename(member)
                    if not out_name:
                        continue
                    out_path = os.path.join(sub, out_name)
                    with z.open(member) as src, open(out_path, "wb") as dst:
                        dst.write(src.read())
                    record(records, doi, url + " (member: " + member + ")",
                           out_path, "extracted from " + fname)
                    if is_xlsx:
                        have_xlsx[doi] = True
                    tag = "xlsx" if is_xlsx else "csv"
                    print(f"     [{tag}] {SUBDIR[doi]}/{out_name} "
                          f"{os.path.getsize(out_path)} bytes")

    for doi, ok in have_xlsx.items():
        if not ok:
            print(f"ERROR no xlsx obtained for DOI {doi}")
            sys.exit(4)

    by_doi = {}
    for rec in records:
        by_doi.setdefault(rec["doi"], []).append(rec)

    lines = ["# park-grass-crl data MANIFEST", ""]
    lines.append("Written by fetch_data.py. Raw data under data/raw/ is gitignored; "
                 "this manifest is the only tracked file in data/. Each dataset is in "
                 "its own subfolder because the two ship CSVs with identical names.")
    lines.append("")
    for doi, recs in by_doi.items():
        lines.append("## DOI " + doi)
        lines.append("")
        for rec in recs:
            lines.append("- file: " + rec["filename"])
            lines.append("  - resolved URL: " + rec["url"])
            lines.append("  - SHA-256: " + rec["sha256"])
            lines.append("  - size: " + str(rec["size"]) + " bytes")
            lines.append("  - downloaded (UTC): " + rec["downloaded"])
            lines.append("  - source: " + rec["source"])
        lines.append("")
    with open(MANIFEST, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    print("MANIFEST written:", MANIFEST)


if __name__ == "__main__":
    main()
