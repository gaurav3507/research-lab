# park-grass-crl

Lane: park-grass-crl
Status: PARKED (22 Sep 2026). The open e-RA release is aggregated to one row per
(plot, sub_plot, year), n per environment <= 10, so the lane is outside the NMIN 200
gate regime; parked pending an e-RA request for per-quadrat records.

The Stage 1 block and data-feasibility checklist live in STAGE1.md in this folder.

## Data sources (e-RA DOIs)

Both datasets come from the electronic Rothamsted Archive (e-RA). The citation
strings below are mandatory and must be reproduced wherever these data are used.

Dataset 1
DOI: 10.23637/rpg5-species_1991-2000-01
Citation: Perryman, S., Ostler, R., Storkey, J., Crawley, M. (2021). Dataset: Park Grass Species, Fertilizer and Lime Treatments 1991-2000 Electronic Rothamsted Archive, Rothamsted Research, Harpenden, UK

Dataset 2
DOI: 10.23637/rpg5-species_2010-2012-01
Citation: Perryman, S., Storkey, J. (2022). Dataset: Park Grass Species, Fertilizer and Lime Treatments 2010-2012 Electronic Rothamsted Archive, Rothamsted Research, Harpenden, UK

Mandatory acknowledgement (both datasets): Rothamsted Research (data originator)
and the Lawes Agricultural Trust, supported by UKRI-BBSRC award BBS/E/RH/23NB0007
(2023-2028), as part of the Rothamsted Long-Term Experiments National Bioscience
Research Infrastructure (RLTE-NBRI). Dataset 1 additionally acknowledges BBSRC
awards BBS/E/C/00005189 (2012-2017) and BBS/E/C/000J0300 (2017-2022).

## Imported screen arithmetic

The screen arithmetic primitives (fit_pca, project, coefs, offdiag, N_PAIRS) are
imported from meridian-causalbench causalbench/scripts/03_screen.py via importlib,
the same pattern as causalbench/scripts/40_screen_norman.py, not vendored here, so
the numbers stay byte-identical with the E3 panel. The step-0 gate outer loop is
duplicated in probe_02_step0.py, just as 40_screen_norman.py duplicates it in its
screen_run. Note: at the recorded commit there is no precision_readout.py; the
precision readout (coefs, offdiag) and the step-0 metric (mean_ratio_pairs) both
live in 03_screen.py.

meridian-causalbench clone: sibling of research-lab (not inside it).
meridian-causalbench commit hash (screen arithmetic imported from): 202d5971f46a7333fff7be8563d5f0371475e1b5

## Data

Raw data is git-ignored; only data/MANIFEST.md is tracked. No data has been
downloaded yet.
