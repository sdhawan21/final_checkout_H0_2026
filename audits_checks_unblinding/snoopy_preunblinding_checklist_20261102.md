# SNooPy pre-unblinding checklist

Updated 2026-11-02. Scope: saved lightcurve fits through max_model H0 inference,
especially Foundation BVRest, with gen2/gen3 and other restband choices treated
explicitly. This is a source review and checklist, not certification of every
current saved fit or a new cosmology run. No production code or chains changed.
The October 30 audit is preserved as historical evidence, not a current failure list.

## Confirmed in the current source

- `snpy_h0_from_fits.py` reads `host_galaxies/final_host_masses.csv` and uses
  shared name normalisation. Missing masses below -90 are excluded, rather than
  automatically classified as low mass.
- `snpy_selection_quality.py` recomputes flux-space chi-square on fitted bands,
  intersecting data masks with model-validity masks. It includes template
  variance and uses N_valid minus the number of free parameters for dof.
- The quality gate is upper-tail only: reduced chi-square <= 1 + 3 sqrt(2/dof).
  Accepted floor candidates are ranked by closeness to unity. The explicit
  floor path also goes through this quality gate in the current selector;
  the October 30 warning that it bypasses the gate is no longer current.
- Foundation BVRest/BrRest candidates are checked against their saved
  g_Found/r_Found restband mapping, not accepted solely by filename.
- The runner has explicit gen2/gen3 directory selection and generation-tagged
  output names. Directory selection does not certify saved object metadata.
- The runner fingerprints the host file, selection code, selected row values
  and fit-file contents when validating cached chains. This is stronger than
  the old object-ID-only check, but not complete fitting-runtime provenance.
- Five focused tests passed using `python -m unittest test_snpy_selection_quality`
  in the inference directory, with PYTHONNOUSERSITE=1 in snpy_env.

## Necessary before freezing

### 1. Freeze the actual analysis configuration

- [ ] Record the chosen model, generation, Foundation restband mode, fitted bands,
  floor grid/policy, redshift limits, prepeak rule, sBV/colour cuts, PV model,
  intrinsic-scatter model and host prescription.
- [ ] Specify BVRest explicitly if that is the intended result. Current runner
  defaults are max_model, gen2, NoForceRest, all surveys and prepeak enabled.
  A bare invocation is not the nominated BVRest run.
- [ ] Decide the role of NoForceRest and BrRest before unblinding. They are
  alternative rest-frame/template assumptions, not independent measurements
  that must automatically receive equal weight. Do not pick a mode by agreement
  with SALT or by the smallest Hubble scatter.

### 2. Verify every selected saved fit against its inputs

- [ ] Export a ledger of SN, survey, original photometry, selected .snpy file,
  generation, floor, model, fitted observer bands, saved restbands, Tmax, sBV,
  peak magnitudes, covariance, masks, valid-observation counts and quality status.
- [ ] Check the generation in the saved fit/template metadata, not only its path.
  Confirm no mixture of pre-fix/post-fix photometry or passband definitions.
- [ ] Verify SN2021J retains its intended B/V assignment in the actual saved fit
  and after any model reset; verify SN2020nlb uses the adopted NLB passbands and
  updated photometry. Resolve SN2021rhu aliases without double counting.
- [ ] Trace SN1990N/SN1991T and the CfA3/CfA4 phase/instrument subsets to their
  photometric systems. Reconcile all applicable natural/standard, AB/Vega/BD17
  conversions and cross-calibration offsets exactly once.
- [ ] Freeze the installed passband curves, zeropoints, magnitude references,
  SNooPy version and template files. Resolve duplicate registry names to the
  intended functions. Re-loading under today's registry does not prove which
  registry was used to fit an old file.
- [ ] Plot all final calibrators and flagged Hubble-flow fits, including residuals,
  masks and fitted/model-valid phases. Audit timing, early coverage, sparse bands,
  late-time failures and structured colour residuals, not just total chi-square.

### 3. Validate fit quality and reported parameter uncertainties

- [ ] Re-run the saved-fit census with the current fitted-observation definition
  and every available floor. Do not carry forward the October 30 list of failed
  objects or sample counts without recomputation.
- [ ] Confirm prepeak uses only fitted, unmasked, model-valid observations and
  the intended Tmax reference, with the required two-band coverage.
- [ ] Independently check several chi-square calculations against the actual
  fitting residuals, especially masked points and gen2/gen3 differences.
- [ ] Verify whether the installed SNooPy optimiser scales its parameter covariance
  by its stored reduced chi-square. Correcting the selection dof does not by itself
  correct saved parameter errors. If materially inconsistent, address the fitting
  covariance and refit affected objects rather than blindly rescaling afterward.
- [ ] Check positive/finite uncertainties and covariance eigenvalues and confirm
  max_model propagation includes correlations among peak magnitudes and sBV.
- [ ] Treat 1 + 3 sqrt(2/dof) as the adopted approximate gate, not an exactly
  calibrated probability when templates, estimated covariance or floor selection
  affect its distribution. Low chi-square is a diagnostic, not automatic proof
  of a bad distance or grounds for tuning the template generation.

### 4. Confirm the ladder inputs and likelihood

- [ ] Compare selected masses object by object against the frozen SALT catalogue,
  including SN2021rhu. Record missing masses and exclusions explicitly.
- [ ] Match TRGB distances, errors, distance offset and repeated-host treatment
  to the adopted SALT analysis. Document any ignored covariance between SNe
  sharing a host distance; do not count repeated hosts as independent distances.
- [ ] Verify the effective PV table/function, frame conventions, unique SN joins,
  z used for selection, distance calculation and velocity uncertainties. Trace
  the helper actually imported by the runner; a setting named Manticore does
  not guarantee the same table/version as SALT.
- [ ] Check max_model magnitude/colour definitions and coefficient ordering,
  host-step sign/threshold and covariance cross terms. EBV_model requires a
  separate validation; do not transfer a max_model sign-off to it automatically.
- [ ] Confirm the sBV range and colour cut are implemented as intended for both
  rungs, without inadvertently substituting a differently defined colour or EBV.

### 5. Regenerate and freeze the final selected inference

- [ ] Run in a fresh output directory after input fixes; preserve unclipped and
  clipped posteriors, selected IDs, rejected IDs, pulls, thresholds and reasons.
- [ ] Verify which residual variance enters Chauvenet pulls, whether intrinsic
  scatter is included, whether rejection is joint or rung-specific, and whether
  parameters are refitted between rejection passes. Document the actual policy.
- [ ] Confirm current cache fingerprint agreement. A code fix alone does not
  demonstrate that production chains were recomputed with that fix.
- [ ] Inspect prior boundaries, covariance/degeneracies and nested-sampling
  convergence. Repeat an independent seed and establish that sampling variation
  is small relative to the reported absolute SALT/SNooPy difference.
- [ ] Freeze full input/runtime checksums and reproduce in the clean directory.
  Ensure the figure/table/systematics scripts point to these exact chains and
  derive sample counts from their selected membership, not unrelated interim files.

## Recommended for interpreting the SALT difference

- [ ] Repeat the native and paired matched comparison after the final freeze,
  with identical external masses, distances and PV inputs. Retain a common
  membership without fresh method-specific clipping for the controlled test.
- [ ] Separate calibrator-rung and Hubble-flow contributions; inspect individual
  distance residual differences, not just H0 and total scatter.
- [ ] Perform paired calibrator/host leave-one-out and survey-omission checks.
  A remaining matched difference need not indicate a bug, and is not a reason
  to remove otherwise valid objects.
- [ ] For Foundation, examine K-corrections and inferred B/V magnitudes versus
  redshift, colour and restband choice. g/r observations do not directly measure
  rest B/V in every object; forced BV can introduce model-dependent extrapolation.
- [ ] Compare gen2/gen3 on identical photometry, passbands and membership, using
  peak magnitudes, sBV, template errors and inferred uncertainties. Lower chi-square
  from larger template variance is not by itself improved luminosity precision.
- [ ] Check posterior predictive or injection/recovery behaviour for representative
  well-sampled, sparse and red objects. A small scatter is not the success criterion;
  reliable residuals, uncertainty coverage and reproducibility are.

## Good to have, but not critical

- [ ] Expand the targeted recovery tests into an end-to-end simulation suite.
- [ ] Add regression tests for exact saved Foundation mappings, missing host
  masses, alias collisions, survey selection and every floor-selection branch.
- [ ] Produce a browsable fit gallery linked to the selection ledger.
- [ ] Explore continuous/probabilistic environmental or colour standardisation
  only as separately documented analyses, not last-minute changes to the freeze.

## Relevant files and historical evidence

Project-relative paths:

- Fitters: `snoopy_fits/fit_lightcurves.py`, `fit_lightcurves_calib.py`;
  `test_fset_snpy.py` is a single-object test, not the complete production pipeline.
- Inference: `h0_inference/with_realdata/run_snpy_chauvenet_h0.py`,
  `snpy_h0_from_fits.py`, `snpy_selection_quality.py`.
- Tests: `h0_inference/with_realdata/test_snpy_selection_quality.py`.
- Earlier audit: `unblinding/snoopy_preunblinding_audit_20261030.md` and
  `snpy_saved_fit_audit_20261030.csv`.
- Existing census helper: `unblinding/audit_snpy_saved_fits.py`. Its input/output
  locations are historical; inspect and retarget them before rerunning. Its old
  positive checks are evidence for that saved selection only, not today's sample.

Sign-off should mean: every necessary item has evidence or an explicitly accepted,
documented limitation. It does not require SNooPy to reproduce SALT's H0 or scatter.
Continue reporting only absolute H0 differences while the analysis is blinded.
