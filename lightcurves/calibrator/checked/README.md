# Checked calibrator photometry

This directory contains conservative SNANA-format photometry files regenerated from published tables or clearly identified non-ZTF sources.

Files added in this pass:

- `SN1990N_Lira1998_UBVRI.snana.dat`: Calan/Tololo UBVRI photometry from Lira et al. 1998, Table 5.
- `SN1991T_Lira1998_UBVRI.snana.dat`: Calan/Tololo UBVRI photometry from Lira et al. 1998, Table 6.
- `SN2021rhu_Khetan2023_SwiftOnly.snana.dat`: Swift/UVOT w2/m2/w1/u/v rows only from the SN2021rhu appendix table. ZTF gri rows from the same paper are intentionally omitted.
- `SN2020nlb_Williams2024_nonZTF_optical.snana.dat`: LT/IO:O, NOT/ALFOSC, and 67/91 Schmidt optical photometry from Williams et al. 2024. ZTF is not used.

`MAG` and `MAGERR` are the direct published observables. `FLUXCAL` and `FLUXCALERR` are computed with SNANA-style `MAGREF=27.5` for compatibility with readers that expect flux columns.

The audit file `calibrator_photometry_reference_audit.csv` is a first-pass provenance map for the existing files in `lightcurves/calibrator`. Rows marked `needs_external_verification` should not be treated as paper-checked yet; they simply record that the current SNANA header does not contain enough provenance to verify row-by-row values.
