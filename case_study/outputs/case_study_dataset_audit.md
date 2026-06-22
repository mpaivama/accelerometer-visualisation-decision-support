# Case Study Dataset Audit

This report checks whether the uploaded NHANES files are sufficient to reconstruct the accelerometer-derived metrics needed for the worked case study.

## Short Answer

The uploaded files are sufficient to reconstruct the direct accelerometer metrics needed for the visualisation case study: participant-level mean weekday MIMS-units, mean weekend-day MIMS-units, weekday-minus-weekend differences, and percentage differences from weekday activity.

Exact replication of every published estimate may still require checking the paper's precise subgroup recoding and inferential procedure. The current script uses NHANES MEC four-year weights and an approximate Taylor-linearised confidence interval for visualisation estimates.

## Files Checked

| cycle            | file         |   rows |   columns_n |   unique_participants |
|:-----------------|:-------------|-------:|------------:|----------------------:|
| NHANES 2011-2012 | DEMO_G.xpt   |   9756 |          48 |                  9756 |
| NHANES 2011-2012 | BMX_G.xpt    |   9338 |          26 |                  9338 |
| NHANES 2011-2012 | PAXHD_G.xpt  |   7821 |           9 |                  7821 |
| NHANES 2011-2012 | PAXDAY_G.xpt |  61168 |          15 |                  6917 |
| NHANES 2011-2012 | PFQ_G.xpt    |   8350 |          35 |                  8350 |
| NHANES 2013-2014 | DEMO_H.xpt   |  10175 |          47 |                 10175 |
| NHANES 2013-2014 | BMX_H.xpt    |   9813 |          26 |                  9813 |
| NHANES 2013-2014 | PAXHD_H.xpt  |   8913 |           9 |                  8913 |
| NHANES 2013-2014 | PAXDAY_H.xpt |  69018 |          15 |                  7776 |
| NHANES 2013-2014 | PFQ_H.xpt    |   9230 |          36 |                  9230 |

## Key Variables Available

- `PAXMTSD`: day-level MIMS triaxial value.
- `PAXDAYD`: wear day number; days 2-8 are treated as complete candidate days.
- `PAXDAYWD`: day of week; Sunday and Saturday are weekend days.
- `PAXVMD`: valid minutes in the day.
- `PAXNWMD`: valid non-wear minutes in the day.
- `PAXSWMD`: valid sleep wear minutes in the day.
- `PAXHAND`: non-dominant wrist placement.
- `PFQ054`: need special equipment to walk.
- `RIDEXPRG`: pregnancy status at exam.
- `WTMEC2YR`, `SDMVSTRA`, `SDMVPSU`: NHANES weighting and design variables.
- `BMXBMI`, `BMDBMIC`: adult BMI and child/adolescent BMI category variables.

## Rules Implemented

- Include participants aged 6 years or older.
- Include participants with PAM summary data available (`PAXSTS == 1`).
- Keep non-dominant wrist placement only (`PAXHAND == 1`).
- Exclude participants known to be pregnant at exam (`RIDEXPRG == 1`).
- Exclude participants reporting special equipment needed to walk (`PFQ054 == 1`).
- Candidate full days are wear days 2-8.
- Valid days require at least 1380 valid minutes, fewer than 72 non-wear minutes, and fewer than 1020 sleep wear minutes.
- The analytic participant dataset requires at least 3 valid weekdays and at least 1 valid weekend day.
- Four-year MEC weights are calculated as `WTMEC2YR / 2`.

## Participant Exclusions

| step                                                          |   n_before |   n_after |   n_excluded |
|:--------------------------------------------------------------|-----------:|----------:|-------------:|
| Age >= 6 years                                                |      19931 |     16733 |         3198 |
| PAM summary data available (PAXSTS == 1)                      |      16733 |     14175 |         2558 |
| PAM worn on non-dominant hand (PAXHAND == 1)                  |      14175 |     14048 |          127 |
| Not known pregnant at exam (exclude RIDEXPRG == 1)            |      14048 |     13943 |          105 |
| Does not need special equipment to walk (exclude PFQ054 == 1) |      13943 |     13012 |          931 |
| Positive MEC exam weight                                      |      13012 |     13012 |            0 |

## Valid Day Counts

By cycle:

| cycle            |   day_records |   candidate_full_days |   valid_days |
|:-----------------|--------------:|----------------------:|-------------:|
| NHANES 2011-2012 |         56174 |                 43753 |        35549 |
| NHANES 2013-2014 |         59102 |                 45989 |        35863 |

By day type:

| day_type   |   candidate_full_days |   valid_days |
|:-----------|----------------------:|-------------:|
| weekday    |                 64157 |        51621 |
| weekend    |                 25585 |        19791 |

## Analytic Participant Counts

| sample                    |    n |
|:--------------------------|-----:|
| Adults 20+                | 6611 |
| Children/adolescents 6-19 | 3520 |

| cycle            |    n |
|:-----------------|-----:|
| NHANES 2011-2012 | 5081 |
| NHANES 2013-2014 | 5050 |

## First Overall Estimates

These are preliminary visualisation estimates from the reproduced participant-level metrics. They are not intended as a final inferential reproduction until subgroup recoding and CI handling are checked against the paper.

| sample                    | level                     | metric                           |   estimate |   ci_low |   ci_high |   unweighted_n |
|:--------------------------|:--------------------------|:---------------------------------|-----------:|---------:|----------:|---------------:|
| Children/adolescents 6-19 | Children/adolescents 6-19 | Weekday MIMS-units               |   17563.7  | 17240.5  |  17886.8  |           3520 |
| Children/adolescents 6-19 | Children/adolescents 6-19 | Weekend-day MIMS-units           |   16681.6  | 16337    |  17026.2  |           3520 |
| Children/adolescents 6-19 | Children/adolescents 6-19 | Weekday minus weekend MIMS-units |     882.02 |   712.43 |   1051.61 |           3520 |
| Children/adolescents 6-19 | Children/adolescents 6-19 | Percent difference from weekday  |       4.22 |     3.2  |      5.24 |           3520 |
| Adults 20+                | Adults 20+                | Weekday MIMS-units               |   13893.2  | 13754.6  |  14031.8  |           6611 |
| Adults 20+                | Adults 20+                | Weekend-day MIMS-units           |   13239.6  | 13072.6  |  13406.6  |           6611 |
| Adults 20+                | Adults 20+                | Weekday minus weekend MIMS-units |     653.63 |   545.02 |    762.24 |           6611 |
| Adults 20+                | Adults 20+                | Percent difference from weekday  |       2.9  |     2.1  |      3.69 |           6611 |

## Outputs Created

- `outputs/case_study_file_inventory.csv`
- `outputs/case_study_exclusion_counts.csv`
- `outputs/case_study_valid_day_metrics.csv`: all valid days after participant-level exclusions.
- `outputs/case_study_analytic_valid_day_metrics.csv`: valid days for participants who meet the final 3-weekday/1-weekend rule.
- `outputs/case_study_participant_metrics.csv`
- `outputs/case_study_summary_estimates.csv`
- `outputs/case_study_dataset_audit.md`

## Remaining Checks Before Plotting

- Compare the sample counts and overall estimates against the published paper tables.
- Confirm whether the paper grouped children/adolescents as 6-19 years or used a narrower child age range.
- Confirm exact subgroup categories for education, marital status, income-to-poverty ratio, and BMI.
- Decide whether the case-study figures should use the approximate CIs generated here or values copied from a final survey-analysis reproduction.

## Sources

- NHANES 2011-2012 data page: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2011
- NHANES 2013-2014 data page: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013
- PAXDAY codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PAXDAY_G.htm
- PAXHD codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PAXHD_G.htm
- PFQ codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PFQ_G.htm
- BMX codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BMX_G.htm
- DEMO codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/DEMO_G.htm
