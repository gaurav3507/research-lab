# STATUS UPDATE 22 Sep 2026

Lane status: PARKED.

Data reality (probe_01): the open e-RA release is aggregated to one row per
(plot, sub_plot, year). There are no per-quadrat records. n per environment is at
most 10 (10 survey years for 1991-2000; 3 for 2010-2012).

Gate operating regime: the imported screen arithmetic (03_screen.py) is calibrated
at NMIN 200 samples per environment. With n per environment <= 10 this lane is far
outside that regime.

Decision: PARKED pending an e-RA request for the per-quadrat records. Kill the lane
if those records are unavailable, or if they provide under 50 rows per sub-plot.

probe_02 step-0 results: OUT-OF-REGIME, NOT A HARNESS VERDICT. Two reasons:
  1. The pseudo-environment size used was 4 (the smallest real treatment sub-plot n
     in yearly samples), far below the calibrated NMIN of 200.
  2. The "fire" threshold of 1.1 in probe_02_step0.py is a script-local cutoff; it is
     not present in 03_screen.py, whose step-0 reports a reference band (expect
     mean_ratio ~ 1.00) rather than applying a hard 1.1 pass/fail cutoff.
The results in results/probe_02/ are kept, not deleted, but must be read as a dry run
of the plumbing, not as a pass/fail on the data.

---

# Lane: park-grass-crl
# Stage 1 block + data-feasibility checklist

Repo: github.com/gaurav3507/research-lab (home PC)
Lane folder: lanes/park-grass-crl/
Status: STAGE 1 WRITTEN, NOVELTY SWEEP NOT RUN, NO DATA DOWNLOADED
Date: 22 Sep 2026

Nothing below is a result. Every number marked (verify) is from memory or a web page
and must be confirmed against the downloaded file before it goes anywhere.

---

## Stage 0: violated expectation

Expectation: multi-environment CRL needs genomics-scale data (hundreds of
perturbations, thousands of cells each), and mechanism vs measurement cannot be
separated on real data because no real dataset labels both kinds of shift.

Observation: the Park Grass experiment (Rothamsted, since 1856) has (a) known-target,
dose-graded fertilizer and lime treatments applied to fixed sub-plots for decades,
(b) a 68-species proportional-biomass panel per quadrat, and (c) documented CHANGES
IN SURVEY METHOD over time (hand-separated hay samples 1862 to 1976; 6 scissor-cut
quadrats per plot with oven-dried species mass 1991 to 2000; a separate survey
2010 to 2012). Same plots, same treatments, different measurement protocol. Both
shift types are archived in one dataset, which no Perturb-seq or fMRI set gives.

No CRL or multi-environment causal-discovery paper has touched it (quick search only;
twelve-angle sweep pending).

---

## Stage 1: hypothesis

**H1 (detectability).** The GRD precondition gate, applied to CLR-transformed species
composition with unmanured plots as control basis, will certify a non-trivial number of
treatment sub-plots as detectable mechanism shifts, BECAUSE the treatments (N form and
dose, P, K, lime level) act on a small number of latent soil-state variables (nitrogen
availability, phosphorus availability, pH, competitive dominance) that the 68-species
panel mixes, and the effect sizes are famously large (unmanured plots ~25 to 33 species,
ammonium-sulphate unlimed plots 1 to 2 species).

**H2 (attribution).** Contrasts BETWEEN survey protocols on the SAME sub-plot and
treatment (1991 to 2000 quadrat protocol vs 2010 to 2012 protocol) will fire the
detectability screen but land DETECTABLE_BUT_UNATTRIBUTED under the subspace test,
while contrasts between treatments WITHIN a protocol will land MECHANISM_SUPPORTED
(non-rejection), BECAUSE a protocol change re-weights how each species is sampled and
measured (a per-species gain, rotating col(A)) without changing the plant community
itself, whereas fertilizer changes the community under a fixed sampling map.

**Mundane alternative (M1).** Composition variation across plots is one-dimensional:
everything is soil pH. Then effective dimensionality will read 1 to 2, every treatment
contrast will project onto a single direction, and the gate's "detectable" verdicts
are just a pH gradient re-read. This is not a failure of the data, it is a boring
answer, and it must be reported if it is what comes out.

**Mundane alternative (M2).** Protocol contrasts fire because of 10+ years of real
community drift between 1991 to 2000 and 2010 to 2012 (climate, N deposition decline),
not because of the protocol. Then H2 is confounded by time. Control for this using
plots whose treatment did not change AND using the within-protocol year-to-year drift
as the null for "how much does a community move in a decade under fixed treatment".

**Consequence if H1 and H2 hold.** First real, non-genomic, non-neuro dataset on which
the GRD gate produces a full three-way verdict with the ground truth known from the
archive. It grounds Contribution 3 (attribution impossibility + subspace test) on a real
double dissociation that the Perturb-seq panel could not supply (real-D attribution was
degenerate there). It also delivers Obj 3 "real-world benchmark" with a modality outside
the whole CRL literature.

**Consequence if H1 holds but H2 fails.** Park Grass becomes a fourth panel entry
(clean mechanism detectability, like HCP), useful but not a headline.

**Kill criteria (any one kills the lane as a headline; the first two kill it entirely).**
1. Fewer than 8 sub-plots with n >= 100 samples (environment starvation).
   Note (22 Sep 2026): the original wording counted environments, not samples. It read
   "Fewer than 8 treatment sub-plots survive NMIN quadrat-samples per environment after
   quality filtering (environment starvation; the gate will just count environments)."
   Corrected to count sub-plots by sample count (n >= 100).
2. Step-0 gate on shuffled quadrats within unmanured plots fires above 10 percent
   (harness broken or compositional artefact).
3. Effective dimensionality (dims_above_2x, size-matched null) is 1 across all
   treatment contrasts (M1 wins; write it up as a paragraph, not a lane).
4. Protocol contrasts and treatment contrasts are indistinguishable on BOTH the
   detectability screen AND the subspace/confound-alignment readouts, after the
   decade-drift null from M2 is subtracted (H2 has no discriminating power here).

---

## Pre-registered prediction table (fill the "observed" column, never edit "predicted")

| Contrast | Predicted detect (BH) | Predicted dims_above_2x | Predicted verdict | Observed |
|---|---|---|---|---|
| Unmanured a vs unmanured b/c/d (lime only) | detect | 1 to 2 | MECHANISM_SUPPORTED | |
| N1/N2/N3 ammonium sulphate, unlimed, vs unmanured | detect at all doses, monotone in dose | 2 to 4 | MECHANISM_SUPPORTED | |
| PK only vs unmanured | detect | 1 to 2 | MECHANISM_SUPPORTED | |
| Same sub-plot, 1991 to 2000 vs 2010 to 2012 | detect | 1 to 3 | DETECTABLE_BUT_UNATTRIBUTED | |
| Same sub-plot, odd years vs even years (within protocol, drift null) | no detect | 0 to 1 | NO_DETECTABLE_SHIFT | |
| Shuffled quadrats within one sub-plot (step-0) | no detect (< 5 percent) | 0 | NO_DETECTABLE_SHIFT | |

Dose monotonicity (row 2) is the strongest single prediction: if the mean-shift ratio
does not increase N1 < N2 < N3, the screen is not reading the intervention.

---

## Data-feasibility checklist

Legend: [V] verified from e-RA pages on 22 Sep 2026; [A] assumed, verify on download.

### Access
- [V] e-RA datasets used here are Open Access, CC-BY 4.0, direct download, no data
  agreement needed for the open sets. Citation strings are mandatory and printed on
  each dataset page.
- [A] Pre-1991 botanical data (PARKCOMP 1862 to 1976, hand-separated hay) may require an
  e-RA registration / data request rather than open download. Do not depend on it for
  the first pass.

### Primary datasets
1. [V] "Park Grass Species, Fertilizer and Lime Treatments 1991-2000",
   doi 10.23637/rpg5-species_1991-2000-01. One xlsx, 68 species, proportional biomass
   per quadrat, 6 quadrats (50 x 25 cm) per plot per year, cut before first hay cut in
   early June, oven-dried, sorted to species. Fertilizer and lime treatments included.
   Species list carries scientific/common name and group (forb/grass/legume).
2. [V] "Park Grass Species, Fertilizer and Lime Treatments 2010-2012",
   doi 10.23637/rpg5-species_2010-2012-01. xlsx plus frictionless CSV. 68 species incl.
   tree saplings. Survey by J. Storkey; SELECTED treatment plots only, not all.
   Sub-plot percent individual species. This is the second measurement protocol.
3. [V] "Park Grass Changes in Mean Species Numbers 1864-2011" (01-OAPGspecies): species
   COUNTS only, not composition. Useful for a sanity plot, not for the gate.
4. [A] Treatment plan / plot map from the e-RA Park Grass page: main plots (~20) x lime
   sub-plots a/b/c/d (target pH 7 / 6 / 5 / unlimed since 1965). Verify plot IDs,
   which plots are unmanured (plot 3 and plot 12 by memory), and N doses
   (N1/N2/N3 ~ 48/96/144 kg N/ha by memory). Do not hardcode until read from the file.
   RESOLVED 22 Sep 2026 (probe_01, read from the file): unmanured (Nil) plots =
   {2, 3, 12} (not just 3 and 12); lime sub-plot letters are a/b/c/d PLUS an extra
   level "s"; N1/N2/N3 = 48/96/144 confirmed; ~19 main plots confirmed.
5. [A] Rothamsted meteorological series (rainfall, temperature since 1853) is in e-RA
   and can serve as a year-level covariate for the M2 drift null.

### Sample-size arithmetic (the thing that decides kill criterion 1)
- 1991 to 2000: 10 years x 6 quadrats = 60 samples per sub-plot per protocol. [V]
- Number of sub-plots surveyed 1991 to 2000: [A] believed to be all ~100 sub-plots;
  verify from the file (count distinct plot x sub-plot).
- 2010 to 2012: 3 years x (quadrats per plot unknown) on SELECTED plots only. [A]
  This is the binding constraint for H2. If per-sub-plot n is under ~20 here, the
  protocol contrast is underpowered and H2 must be reported as such (same wording
  discipline as CausalBench per-perturbation batch: "underpowered", not "no effect").
- Observed dimension 68 (compositional). After CLR and dropping species absent in the
  control basis, expect ~40 to 60 live columns. d_proj = 5 to start, sweep 5/8/10.

### Preprocessing decisions to fix BEFORE running (write into the script header)
- Compositional data: proportional biomass sums to 1 per quadrat, so raw covariance is
  singular. Use centred log-ratio with a pseudocount (multiplicative replacement,
  half the minimum non-zero proportion). Record the pseudocount in the results JSON.
- Zeros: many species are structurally absent on acid plots. Do not drop species by
  plot; drop only species with zero mass across the ENTIRE control basis.
- Control basis: unmanured sub-plots, unlimed (d) as reference pool, per Perturb-seq
  convention (basis fit on control only). Lime sub-plots a/b/c of the unmanured plot
  are the "lime-only" contrast, not part of the basis.
- Environment = (plot, sub-plot, protocol). Never pool protocols in one environment.
- Year is NOT an environment for H1. It is the drift null for H2.
- Nulls: size-matched, disjoint-split geometry from TASK 1b when n_env <= N/2, else
  two-resample fallback; state which fired. BH-FDR across all sub-plot tests.
- Step-0 gate: shuffle quadrats within unmanured sub-plots into pseudo-environments
  of the same size as the smallest real environment; mean_ratio_pairs primary.

### Reuse from meridian-causalbench (do not rewrite arithmetic)
- fit_pca / project / precision_readout / subspace readout / BH helper: import via
  the same importlib pattern as 40_screen_norman.py so numbers stay byte-identical
  with the E3 panel. research-lab must reference the meridian-causalbench commit hash
  used, in the lane README, not vendor a copy.

### Reviewer objections to pre-empt (write the sentence now)
- "Plots are not randomised and are spatially adjacent": true, Park Grass predates
  randomisation. State it. The gate does not need randomisation to report
  detectability; it needs it to call the shift causal. Spatial autocorrelation goes in
  limitations, and the odd/even year null partly controls it.
- "Species composition is the outcome, not a mixture of latents": the claim is that
  68 abundances are a mixing of a few soil-state latents. M1 (it is all pH) is the
  honest test of that claim and is pre-registered.
- "Survey protocol change is confounded with a decade of drift": M2, pre-registered,
  with the within-protocol drift null.

### Compute
- Everything here is numpy/scipy at 68 x ~6000 rows. Home PC is sufficient; no A100.
- Python env: new venv in the lane folder, pinned numpy/scipy/pandas/openpyxl.

---

## First probe (one Claude Code handoff, report only the results block)
1. Download datasets 1 and 2, save under lanes/park-grass-crl/data/raw/ with the DOI
   and download date in a MANIFEST.md; add data/ to .gitignore except MANIFEST.md.
2. Print: distinct (plot, sub-plot) per protocol; quadrat count per sub-plot per year;
   species count; fraction of zeros; the treatment table as read from the file.
3. Run the step-0 shuffled-quadrat gate on unmanured sub-plots. Report the false-fire
   rate. Nothing else runs until this is under 5 percent.
4. Return: the counts from step 2, the step-0 rate, and whether kill criterion 1 is met.
