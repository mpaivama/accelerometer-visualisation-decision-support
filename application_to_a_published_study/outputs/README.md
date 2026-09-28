# Underlying data for the application to a published study

This directory contains the reconstructed and derived data files supporting the
application of the LABDA visualisation decision-support toolkit to the published
NHANES 2011-2014 study.

- `published_study_application_participant_metrics.csv` contains reconstructed participant-level
  weekday and weekend-day MIMS-unit metrics and participant characteristics for
  the analytical sample.
- `published_study_application_summary_estimates.csv` contains derived overall and subgroup
  estimates, uncertainty intervals, and sample counts used in the application
  visualisations.
- `published_study_application_exclusion_counts.csv` reports participant counts retained and
  excluded at each reconstruction stage.
- `published_study_application_file_inventory.csv` records the source NHANES files, variables,
  and record counts used in the reconstruction.
- `published_study_application_dataset_audit.md` documents the implemented reconstruction rules,
  validity criteria, analytical sample, and consistency checks.

The original source data were obtained from the publicly available US National
Health and Nutrition Examination Survey. Source files, provenance, processing
decisions, and reproduction instructions are documented in the parent
`application_to_a_published_study/` directory. Raw NHANES XPT files are not redistributed here.

## Licence

To the extent that the authors hold rights in these reconstructed and derived
data files, they are made available under the Creative Commons Zero 1.0
Universal public-domain dedication (CC0 1.0):
https://creativecommons.org/publicdomain/zero/1.0/

This dedication does not alter any terms or conditions that apply to the
original NHANES source data.
