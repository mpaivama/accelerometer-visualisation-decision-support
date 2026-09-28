# Application to a Published Study Visualisation Reproducibility

This folder contains the reproducible materials used to apply the toolkit to a
published NHANES 2011-2014 study.

Reference paper:

To QG, Stanton R, Schoeppe S, Doering T, Vandelanotte C. *Differences in
physical activity between weekdays and weekend days among U.S. children and
adults: Cross-sectional analysis of NHANES 2011-2014 data.* Preventive Medicine
Reports. 2022;28:101892.

The article citation and publisher DOI are provided in `references/`.

## What Is Included

```text
prepare_published_study_application_dataset.py
    Reconstructs participant-level weekday/weekend MIMS metrics from NHANES XPT
    files.

create_published_study_application_visualisations.py
    Generates the nine checklist-informed published-study application figures.

PUBLISHED_STUDY_APPLICATION_DATASET_REPRODUCTION_RULES.md
    Transparent record of rules extracted from the paper and rules extrapolated
    for dataset reconstruction.

PUBLISHED_STUDY_APPLICATION_VISUALISATION_CODE_GUIDE.md
    Guide to the plotting script, including which parts are specific to the
    published-study application
    and how the examples link to decision-tree recommendations.

references/
    Citation and publisher link for the published NHANES study.

outputs/published_study_application_summary_estimates.csv
outputs/published_study_application_participant_metrics.csv
    Compact reproduced outputs needed to regenerate the figures without
    redownloading the raw NHANES files.

outputs/published_study_application_dataset_audit.md
outputs/published_study_application_exclusion_counts.csv
outputs/published_study_application_file_inventory.csv
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
python3 application_to_a_published_study/create_published_study_application_visualisations.py
```

This reads:

- `application_to_a_published_study/outputs/published_study_application_summary_estimates.csv`
- `application_to_a_published_study/outputs/published_study_application_participant_metrics.csv`

and writes updated figures to:

```text
application_to_a_published_study/figures/
```

## Rebuild The Dataset From Public NHANES Files

Download these ten files from the NHANES 2011-2012 and 2013-2014 public data
pages:

```text
application_to_a_published_study/
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
python3 application_to_a_published_study/prepare_published_study_application_dataset.py
python3 application_to_a_published_study/create_published_study_application_visualisations.py
```

The preparation script writes additional day-level intermediate CSV files. Those
larger intermediates are ignored by Git because they can be regenerated.

## Toolkit Role

This folder is an implementation example, not a general plotting library. It
shows how selected decision-tree recommendations can be translated into
checklist-informed visualisations using a real accelerometer study.

Recommendations that are not directly implemented in the application to the
published study are still
linked to related examples through the recommendation-to-example registry in
`decision_tree.py`.
