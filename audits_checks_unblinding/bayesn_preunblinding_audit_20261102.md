# BayeSN pre-unblinding audit

Updated: 2 November 2026. Scope: light curves -> BayeSN posterior chains ->
selection/Chauvenet -> H0 -> systematic budget. This document consolidates
previous tests and a fresh inspection of current local defaults; it is NOT
a new certification of every fit or of the remote server's outputs.

**Release criterion:** correct, reproducible inference with understood
limitations. Neither agreement with SALT2, matching its sample size, nor a
particular Hubble scatter is a release criterion. Continue to report only
absolute H0 differences while blinded.

Unchecked items require evidence or an explicit documented decision. Prefer
recording a command, output path, source hashes, date and reviewer for each.

## Completed implementation work, not yet production sign-off

- [x] H0 chain lookup now requires `<SN>_0.0_chains.npy`, with matching-stem
  sidecars and no unsuffixed legacy fallback. This selects zero floor only;
  it does not prove that these chains use the latest calibration or free Tmax.
- [x] H0 defaults updated to `host_galaxies/final_host_masses.csv` and
  `redshifts_peculiarvelocities/zcorr_query.csv`. CSV reading, duplicate host
  identities and missing-mass sentinels were tested. Flow uncertainty is on
  by default. Missing PV rows are logged rather than replaced with old values.
- [x] Native/matched comparisons, object-influence diagnostics, a frozen-
  posterior floor sensitivity test, and a four-object Minuit/HMC pilot exist.
  They are diagnostic evidence, not validation of a final production release.

## Necessary before unblinding

### 1. Freeze the scientific and quality-selection policy

- [ ] Write down the intended model/version, BVR/rest-wavelength range,
  extinction assumptions, sigma0=1e-5 convention, Tmax treatment, floor,
  data masks, AV/theta limits, survey list, redshift limits and host step.
  Keep fitted intrinsic scatter in the H0 likelihood separate from
  photometric noise and correlated SED residual variability.
- [ ] Resolve the GOF policy BEFORE the final batch/H0 run. The current
  default is `goodness_of_fit_cut=True`, with 0.01 <= PPC p <= 0.99 and
  median discrepancy/N <= 3. The audited November 1 native posterior had
  GOF disabled. Do not compare those configurations as if only fits changed.
- [ ] Decide whether too-small discrepancies are warnings or exclusions;
  document the rationale. A PPC interval is not a calibrated frequentist
  acceptance interval. Do not interpret discrepancy/N as ordinary reduced
  chi-square with an obvious N-p count for BayeSN's latent/prior model.
- [ ] If introducing a marginal-covariance likelihood, validate its mean,
  covariance propagation and normalization, refit consistently, and calibrate
  its selection statistic with simulations. Do not add population model
  covariance on top of predictions already conditioned on fitted epsilon.
  This is a method change, not a drop-in post-processing cut.
- [ ] Document scientific baseline exclusions separately from sampler,
  coverage, GOF and Hubble-residual exclusions. The last audited native run
  included SN2007on because `base_calib_exclusions=None`. Decide its treatment
  from data/model applicability, not its contribution to the SALT2 difference.
- [ ] Use consistent rules for calibrators and HF unless an independent
  observational reason warrants a difference. Do not narrow AV just to
  reproduce SALT2's colour cut or reduce the H0 discrepancy.

### 2. Audit actual photometry and calibration inputs

- [ ] For each instrument/era and special calibrator, record original filter,
  mapped alias, throughput and reference-spectrum hashes, AB/Vega/BD17
  convention, zeropoint, and every applied correction. Cover Foundation,
  CSP V variants, CfA3 4Shooter/KeplerCam and both CfA4 eras. Check whether
  observations are natural or standard system, not just their band labels.
- [ ] Verify correction signs, units and no double natural/standard or
  cross-calibration correction; test equivalent flux/zeropoint representations
  with synthetic photometry. Trace SN2021J, SN2020nlb and SN2021rhu individually.
- [ ] Verify heliocentric z for LC phase/K corrections, MW E(B-V), SF11
  scaling/extinction law, time conventions, bad points and duplicate epochs.
- [ ] Reconcile SN2017cbv's raw-light-curve hash mismatch with its zero-floor
  manifest. Its saved discrepancy was reproduced, but that does not replace
  a provenance explanation. If fitted numerical inputs changed, refit.
- [ ] Check correct SN/host identity, distances and duplicated entries on both
  rungs. Verify SN2021rhu is included once and that its newly available mass
  is present in the catalog actually read by the final BayeSN run.

### 3. Finish representative light-curve validation before batching

- [ ] Use a panel spanning both rungs, every instrument family, low/high AV,
  sparse/dense cadence, early/late discovery and problematic/control objects.
  Include SN2001el, SN2005df, SN2011fe and SN2017cbv, plus representative
  Foundation/CSP/CfA HF examples. Select by data properties, not H0 residual.
- [ ] Verify free Tmax is truly fitted where intended: manifest, parameter
  draws and compiled model must agree. The current fitter defaults to free
  Tmax, but the recent benchmark chains were fixed-Tmax fits. A new default
  does not update old files. Check phase-window boundaries and sensitivity
  to perturbed initial peak times.
- [ ] Make pre-peak and minimum-coverage selection use model-valid, actually
  fitted filters/observations. Audit initial-phase masks versus posterior
  Tmax: data retained at the initial peak may leave model support later.
- [ ] Resolve the zero-floor GOF failures using residuals by phase and band,
  calibration provenance and actual refits, not only inflated-error diagnostics.
  Prioritize SN1981B, SN1994D and SN2007on, which were not rescued by the
  frozen-posterior 2% floor test. Examine SN1998aq's small-discrepancy failure
  separately from excessive-residual cases.
- [ ] If adopting floors, specify them in fractional-flux or magnitude units
  explicitly and justify the policy independently. Test actual 0/1/2% refits;
  the existing census reused old draws and is not evidence of refit acceptance.
  A per-point independent floor does not represent coherent band zeropoint
  errors. Do not tune each object's floor solely until it passes.
- [ ] Check fitted mu, delM, AV, theta, epsilon and Tmax shapes/units and
  serialization. Verify the very broad distance prior is not effectively
  importing the TRGB or redshift distance into the measured LC distance.
  Perturb starting distance/prior centering as a pilot test.

### 4. Establish numerical reliability

- [ ] Require finite, available convergence diagnostics for every retained
  object. Current H0 defaults allow missing fit/GOF diagnostic sidecars;
  use explicit production requirements and audit missing/nonfinite values.
- [ ] Freeze convergence thresholds and retry rules. The fitter's aggregate
  criterion and H0's Rhat<1.02, ESS>=400, divergence-fraction<=0.01 policy
  are not identical. Prefer no unresolved divergences; inspect their locations,
  energy/BFMI, treedepth and tail ESS rather than treating one percentage as
  universal permission to ignore them.
- [ ] Check independent-seed/longer-run stability on the panel, especially
  distance/extinction degeneracy and AV near zero. Set required MCSE for
  distance estimates and posterior tails. Warmup/sample counts alone are
  not acceptance criteria; current fitter defaults are 1000/1000.
- [ ] Keep HMC for the final release unless a replacement is separately
  validated. The Minuit pilot found absolute distance differences of about
  0.050 mag for SN2005df and 0.029 mag for SN2017cbv, despite valid minima.
  Joint MAP + HESSE is not a marginalized posterior; nominal covariance flags
  do not validate uncertainty coverage. The built-in `opt` mode is L-BFGS
  and changes sigma0, so it is not automatically a controlled HMC comparison.
- [ ] Assess the Gaussian distance-summary approximation used by H0 for
  skewed/boundary cases; demonstrate negligible impact or propagate posterior
  information more faithfully in a labelled sensitivity test.

### 5. Validate sample-level inference and H0 consumption

- [ ] Run final selection and H0 anew using the updated mass/PV files; changing
  defaults cannot update saved posteriors. Explicitly specify all intended
  surveys, chain roots, exclusions and quality switches. Missing PV rows
  (e.g. SN2011iv/CSP in the inspected table) must appear in the exclusion ledger.
- [ ] Recheck the current final host catalog for completeness, sentinel
  handling and identical step convention in the intended SALT comparison.
  Hash the catalog after collaborator updates and regenerate affected runs.
- [ ] Check zHD selection, distance-redshift relation, flow-error propagation
  and residual velocity dispersion are consistent. Retain LC zhel separately.
- [ ] Verify Chauvenet pulls include the intended measurement, external
  distance/PV and intrinsic-scatter terms. Freeze standard versus empirical
  pull scaling, separate-rung rejection, iteration policy and exclusion lists.
  Keep pre-clipping and post-clipping samples and results traceable.
- [ ] Compare native and matched samples on BOTH rungs; for controlled model
  comparisons also align masses, distances, redshifts and error treatment.
  Matching is diagnostic, not a requirement that production samples agree.
- [ ] Recompute object/host/survey influence with the FINAL chains. Determine
  whether remaining differences are a few objects or a differential bulk
  effect. Do not use influence alone to justify rejecting an object.
- [ ] Check sufficient nested-sampling precision for reported absolute shifts,
  repeat sensitive cases with independent seeds, and distinguish Monte Carlo
  differences from scientific-input changes.
- [ ] Update every systematics table/plot/manifest with the frozen BayeSN
  posterior. Document whether it enters the budget, native/matched convention
  and compression statistic. Do not mix older BayeSN results into the release.

### 6. Reproducibility and final gate

- [ ] Use a fresh, immutable production directory. Archive exact CLI/config,
  input/chain/sidecar hashes, model/Stan code, package versions, throughput
  files and reference spectra, including external dependencies.
- [ ] Make resume/cache reuse depend on content/configuration, not just file
  existence or path. Current cache configuration checks are not comprehensive
  content-hash protection against overwriting a file at the same path.
- [ ] If a nonzero floor is adopted, update the H0 chain selector explicitly:
  it currently accepts ONLY `_0.0_chains.npy`. Keep no implicit fallback;
  log the exact chain and floor used for every retained SN.
- [ ] Produce per-object plots, convergence metrics, diagnostic distributions,
  selection/cut-flow and failure ledgers. Preserve raw Stan CSVs. Cross-check
  unique identities and final counts against H0 inputs and tables.
- [ ] Reproduce from a clean environment/directory. Obtain a second review of
  calibration mappings, masks, accepted quality policy and final sample.
- [ ] Freeze dated code/data/configuration and a written list of remaining
  limitations before the real offset is revealed. Any unresolved failure
  affecting retained distances blocks that BayeSN result's production claim.
  If BayeSN remains exploratory, explicitly freeze that status and its role
  in the paper/budget before unblinding rather than tuning it afterwards.

## Recommended validation

- [ ] Repeated simulate-and-refit experiments at realistic cadence/errors to
  measure distance bias, interval coverage and false rejection under the
  adopted GOF rule. Essential if presenting a NEW GOF statistic as calibrated.
- [ ] Test coherent per-band offsets separately from independent noise floors.
- [ ] Leave-one-band-out and controlled wavelength-coverage tests; degrade
  well-observed objects to Foundation-like coverage to assess prior sensitivity.
- [ ] Compare to literature optical-only distances with common photometry,
  training model, bands, priors and zero-point convention. NIR scatter is not
  a target for this optical-only sample.
- [ ] Inspect residuals and distance differences versus AV, theta, colour,
  redshift, host mass, survey, cadence and fitted Tmax displacement.
- [ ] Recompute borderline PPC values with more posterior draws or analytical
  integration of replicate noise; distinguish numerical classification noise
  from physical mismatch. Retain discrepancy arrays for reproducibility.
- [ ] Quantify correlations among SNe sharing a host/distance or calibration
  system and test the impact of covariance assumptions on uncertainties.

## Good to have, not critical to this release

- [ ] Larger blinded synthetic recovery suite and automatic regression tests.
- [ ] Same-hardware HMC/Minuit/Laplace timing study and approximation coverage
  tests. Existing Minuit timing excludes preparation and is not a measured
  HMC speedup factor.
- [ ] Automated summary dashboard combining provenance, plots, diagnostics
  and cut-flow. This improves review but does not replace the checks above.

## Which changes require refitting?

| Change | Required action |
| --- | --- |
| Photometry, filters/ZPs, MW treatment, model/prior, floor, Tmax or fitted data mask | Refit affected LCs, redo quality selection and H0 |
| Inadequate MCMC precision or numerical failure | Retry affected LCs; validate convergence before H0 |
| Extra PPC draws or recoverable plots/diagnostics | Post-process existing valid chains; redo affected selection/H0 |
| External host masses, TRGB distances, PV table or H0 selection | Rerun selection/H0; LC refits only if those inputs also affect the LC model/prior |

## Existing evidence and tools

Paths below are relative to the project root. Historical results must not be
mistaken for certification of newly overwritten chains.

- `fit_scripts/bayesn_fits/PRE_FREEZE_AUDIT_20261031.md`: earlier detailed audit;
  its old host/PV defaults and inventory counts are historical.
- `fit_scripts/bayesn_fits/gof_floor_census/README.md`: 12-calibrator frozen-
  posterior error-floor test, not actual refits.
- `fit_scripts/bayesn_fits/minuit_hmc_benchmark/README.md`: four-object fixed-
  Tmax MAP/HMC pilot and reproducible inputs.
- `h0_inference/with_realdata/chauvenet_native_and_matched/bayesn_zero_floor_audit/`:
  native/matched comparisons, unmatched identities and leave-one-out tests.
- `fit_scripts/bayesn_fits/plot_and_census_calibrators.py` and
  `plot_hubbleflow_fits.py`: plotting helpers; check their own defaults and
  floor-name handling against the frozen H0 selection before relying on counts.

**Suggested order:** freeze intended policy -> resolve photometry/Tmax and
pilot failures -> validate diagnostics/error treatment -> freeze batch ->
production fits -> final selection/H0 and sensitivities -> clean reproduction
and independent sign-off -> unblind.
