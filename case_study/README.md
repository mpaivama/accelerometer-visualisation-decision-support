# Worked Case Study Visualisation Reproducibility

This folder contains the reproducible materials for the NHANES 2011-2014 worked
case study used to demonstrate the toolkit.

Reference paper:

To QG, Stanton R, Schoeppe S, Doering T, Vandelanotte C. *Differences in
physical activity between weekdays and weekend days among U.S. children and
adults: Cross-sectional analysis of NHANES 2011-2014 data.* Preventive Medicine
Reports. 2022;28:101892.

The published article PDF is included in `references/`. The PDF metadata
identifies the paper as open access under the Creative Commons Attribution 4.0
International licence.

## What Is Included

```text
prepare_case_study_dataset.py
    Reconstructs participant-level weekday/weekend MIMS metrics from NHANES XPT
    files.

create_case_study_visualisations.py
    Generates the nine checklist-informed case-study figures.

CASE_STUDY_DATASET_REPRODUCTION_RULES.md
    Transparent record of rules extracted from the paper and rules extrapolated
    for dataset reconstruction.

CASE_STUDY_VISUALISATION_CODE_GUIDE.md
    Guide to the plotting script, including which parts are case-study-specific
    and how the examples link to decision-tree recommendations.

references/
    Published NHANES case-study paper and citation/licence note.

outputs/case_study_summary_estimates.csv
outputs/case_study_participant_metrics.csv
    Compact reproduced outputs needed to regenerate the figures without
    redownloading the raw NHANES files.

outputs/case_study_dataset_audit.md
outputs/case_study_exclusion_counts.csv
outputs/case_study_file_inventory.csv
    Audit files documenting the reconstruction.

figures/
    Generated figures in PNG, PDF, and SVG, plus figure notes, captions, alt
    text, and checklist-informed design choices.
```

Raw NHANES `.xpt` files are not committed to Git. They are public data files
available from CDC/NCHS and can be downloaded when regenerating the dataset from
source.

## Regenerate The Figures From Included Outputs

From the repository root:

```bash
python3 case_study/create_case_study_visualisations.py
```

This reads:

- `case_study/outputs/case_study_summary_estimates.csv`
- `case_study/outputs/case_study_participant_metrics.csv`

and writes updated figures to:

```text
case_study/figures/
```

## Rebuild The Dataset From Public NHANES Files

Download these ten files from the NHANES 2011-2012 and 2013-2014 public data
pages:

```text
case_study/
    NHANES 2011-2012/
        DEMO_G.xpt
        BMX_G.xpt
        PAXHD_G.xpt
        PAXDAY_G.xpt
        PFQ_G.xpt
    NHANES 2013-2014/
        DEMO_H.xpt
        BMX_H.xpt
        PAXHD_H.xpt
        PAXDAY_H.xpt
        PFQ_H.xpt
```

Then run:

```bash
python3 case_study/prepare_case_study_dataset.py
python3 case_study/create_case_study_visualisations.py
```

The preparation script writes additional day-level intermediate CSV files. Those
larger intermediates are ignored by Git because they can be regenerated.

## Toolkit Role

This folder is an implementation example, not a general plotting library. It
shows how selected decision-tree recommendations can be translated into
checklist-informed visualisations using a real accelerometer study.

Recommendations that are not directly implemented in the case study are still
linked to related examples through the recommendation-to-example registry in
`decision_tree.py`.
