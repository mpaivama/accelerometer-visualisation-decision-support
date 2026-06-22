# Case Study Dataset Reproduction Rules

This document summarises the rules used to reconstruct the NHANES 2011-2014
case-study dataset for the visualisation toolkit. The purpose of this
reconstruction is to generate direct accelerometer-derived metrics for example
visualisations, not to reproduce model results.

Reference paper: To QG, Stanton R, Schoeppe S, Doering T, Vandelanotte C.
*Differences in physical activity between weekdays and weekend days among U.S.
children and adults: Cross-sectional analysis of NHANES 2011-2014 data.*

## Data Files Used

The reconstruction used publicly available NHANES files from the 2011-2012 and
2013-2014 cycles:

| Component | 2011-2012 file | 2013-2014 file | Use in reconstruction |
|:--|:--|:--|:--|
| Demographics | `DEMO_G.xpt` | `DEMO_H.xpt` | Age, sex, race/ethnicity, pregnancy status, education, marital status, income-to-poverty ratio, survey weights, strata, and PSU. |
| Body measures | `BMX_G.xpt` | `BMX_H.xpt` | Adult BMI and child/adolescent BMI category. |
| Physical activity monitor header | `PAXHD_G.xpt` | `PAXHD_H.xpt` | PAM data availability and wrist placement. |
| Physical activity monitor day | `PAXDAY_G.xpt` | `PAXDAY_H.xpt` | Day-level MIMS-units, valid minutes, sleep wear minutes, non-wear minutes, day of wear, and day of week. |
| Physical functioning | `PFQ_G.xpt` | `PFQ_H.xpt` | Special equipment needed to walk. |

Minute-level, hour-level, and raw 80 Hz accelerometer files were not used,
because the paper's visualised metrics can be reconstructed from the released
day-level MIMS summaries.

## Rules Extracted From The Paper

The following rules were taken from the paper's description of the analysis and
translated into reproducible dataset-construction steps.

1. Use NHANES 2011-2014 accelerometer data.

2. Use Monitor-Independent Movement Summary units (MIMS-units) as the
   accelerometer-derived physical activity metric.

3. Work with daily physical activity summaries and compare weekdays with
   weekend days.

4. Exclude the first and ninth accelerometer wear days, because these are
   partial wear days in the NHANES protocol.

5. Define a valid day using the following criteria:
   - at least 1,380 valid minutes in the day;
   - fewer than 72 non-wear minutes;
   - fewer than 17 hours, or 1,020 minutes, of sleep wear time.

6. Include participants with at least 3 valid weekdays and at least 1 valid
   weekend day.

7. Exclude pregnant participants.

8. Exclude participants who need special equipment to walk.

9. Exclude participants whose accelerometer was placed on the dominant wrist or
   whose wrist placement was unknown.

10. Generate participant-level metrics separately for weekday and weekend-day
    physical activity.

11. Calculate weekday-minus-weekend differences in MIMS-units.

12. Calculate percentage difference relative to weekday MIMS-units.

13. Use NHANES survey design information when producing weighted summary
    estimates.

## Operationalised And Extrapolated Rules

Some paper rules required explicit implementation choices because the paper
described the concept but not every code-level detail. These choices are listed
here for transparency.

### Age And Sample Definition

The public 2011-2014 `PAXDAY` files include accelerometer records for
participants aged 6 years or older. The reconstruction therefore starts with
participants aged >=6 years.

For subgroup summaries, participants were classified as:

| Group | Operational definition |
|:--|:--|
| Children/adolescents | age 6-19 years |
| Adults | age >=20 years |

This follows NHANES variable availability: adult education, marital status, and
adult BMI categories are defined for adults, while `BMDBMIC` provides BMI
categories for children/adolescents.

### Accelerometer Metric

The day-level MIMS metric was operationalised using:

| Concept | NHANES variable |
|:--|:--|
| Daily MIMS-units | `PAXMTSD` |
| Day of wear | `PAXDAYD` |
| Day of week | `PAXDAYWD` |
| Valid minutes | `PAXVMD` |
| Sleep wear minutes | `PAXSWMD` |
| Non-wear minutes | `PAXNWMD` |

`PAXMTSD` was used as released in `PAXDAY`; no additional MIMS calculation was
performed from minute-level or raw accelerometer files.

### Complete Candidate Days

The paper indicates that the first and ninth wear days should be excluded. This
was implemented as:

```text
Candidate full days = PAXDAYD values 2 through 8
```

### Weekday And Weekend Classification

The NHANES `PAXDAYWD` codebook defines:

```text
1 = Sunday
2 = Monday
3 = Tuesday
4 = Wednesday
5 = Thursday
6 = Friday
7 = Saturday
```

The reconstruction used:

```text
Weekend day = Sunday or Saturday
Weekday = Monday through Friday
```

### Valid-Day Rule

The valid-day rule was implemented at day level as:

```text
PAXDAYD in 2..8
AND PAXVMD >= 1380
AND PAXNWMD < 72
AND PAXSWMD < 1020
```

Participants were retained in the analytic dataset if they had:

```text
n valid weekdays >= 3
AND n valid weekend days >= 1
```

### Wrist Placement

The paper describes excluding dominant-wrist and unknown-placement records. This
was implemented with the NHANES header variable:

```text
Keep PAXHAND == 1
Exclude PAXHAND == 2 or PAXHAND == 9
```

`PAXHAND == 1` indicates that the monitor was worn on the non-dominant hand.
No additional exclusion was applied based on `PAXORENT` wrist surface
orientation, because the paper's exclusion criterion referred to dominant or
unknown wrist placement rather than dorsal/palmar surface orientation.

### Pregnancy Exclusion

Pregnancy was operationalised using `RIDEXPRG`:

```text
Exclude RIDEXPRG == 1
Keep RIDEXPRG == 2, RIDEXPRG == 3, or missing
```

`RIDEXPRG` is only defined for females aged 20-44 years at the MEC exam.
Missing values are therefore expected for males, children/adolescents, and
females outside that age range. These missing values were retained.

### Special Equipment To Walk

The paper describes excluding people who need special equipment to walk. This
was operationalised using `PFQ054`:

```text
Exclude PFQ054 == 1
Keep PFQ054 == 2 or missing
```

`PFQ054` asks whether the participant has difficulty walking without using
special equipment. It was selected instead of `PFQ090`, because `PFQ090`
captures broader healthcare equipment use and is less specific to walking.

Missing `PFQ054` values were retained because this item is asked only of adults
aged 20 years or older; missing values are expected for children/adolescents.

### Weighting

For the combined 2011-2014 dataset, four-year MEC weights were calculated as:

```text
WTMEC4YR = WTMEC2YR / 2
```

The output dataset also retains `SDMVSTRA` and `SDMVPSU` so survey-design-based
summary estimates can be calculated.

The current preparation script creates preliminary weighted estimates and
approximate confidence intervals for visualisation development. Exact
replication of published inferential estimates may require reproducing the
paper's full weighting, post-stratification, and variance-estimation approach.

### BMI And Sociodemographic Categories

The case-study output includes subgroup variables needed for visualisation
examples. These were recoded from NHANES variables as follows:

| Subgroup | Operational source |
|:--|:--|
| Sex | `RIAGENDR` |
| Age group | `RIDAGEYR` |
| Race/ethnicity | `RIDRETH3` |
| Income-to-poverty category | `INDFMPIR` |
| Adult education | `DMDEDUC2`, adults only |
| Adult marital status | `DMDMARTL`, adults only |
| Adult BMI category | `BMXBMI`, adults only |
| Child/adolescent BMI category | `BMDBMIC`, children/adolescents only |

Some category boundaries may need to be adjusted if exact agreement with the
published paper tables is required. For the visualisation case study, these
variables are used to demonstrate figure structures rather than to reproduce
every table value exactly.

## Derived Metrics In The Reproduced Dataset

For each retained participant, the script calculates:

| Metric | Definition |
|:--|:--|
| `mean_mims_weekday` | Mean `PAXMTSD` across valid weekdays. |
| `mean_mims_weekend` | Mean `PAXMTSD` across valid weekend days. |
| `weekday_minus_weekend_mims` | `mean_mims_weekday - mean_mims_weekend`. |
| `pct_difference_from_weekday` | `weekday_minus_weekend_mims / mean_mims_weekday * 100`. |
| `n_valid_days_weekday` | Number of valid weekdays contributing to the participant metric. |
| `n_valid_days_weekend` | Number of valid weekend days contributing to the participant metric. |

## Current Dataset Counts

Using the rules above, the current script generated:

| Output count | n |
|:--|--:|
| Analytic participants | 10,131 |
| Adults aged >=20 years | 6,611 |
| Children/adolescents aged 6-19 years | 3,520 |
| Valid day records after participant exclusions | 71,412 |
| Valid day records contributing to analytic participants | 66,625 |

## Reproducible Outputs

The reproduction script is saved as:

```text
Case study/scripts/prepare_case_study_dataset.py
```

The main generated files are:

```text
Case study/outputs/case_study_participant_metrics.csv
Case study/outputs/case_study_analytic_valid_day_metrics.csv
Case study/outputs/case_study_summary_estimates.csv
Case study/outputs/case_study_exclusion_counts.csv
Case study/outputs/case_study_dataset_audit.md
```

## Known Limits Of The Current Reconstruction

This reconstruction is intended to support transparent generation of example
visualisations for accelerometer-derived metrics. It is not yet a full
statistical replication package for the published paper.

The main remaining checks are:

1. Compare analytic sample counts with the paper tables.
2. Confirm exact subgroup category boundaries used in the paper.
3. Confirm whether the paper applied additional post-stratification beyond
   standard NHANES four-year MEC weights.
4. Decide whether final visualisations should use the preliminary summary
   estimates generated here or estimates from a full survey-analysis
   replication.

## Source Documentation

- NHANES 2011-2012 data page: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2011
- NHANES 2013-2014 data page: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013
- PAXDAY codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PAXDAY_G.htm
- PAXHD codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PAXHD_G.htm
- PFQ codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PFQ_G.htm
- BMX codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BMX_G.htm
- DEMO codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/DEMO_G.htm
