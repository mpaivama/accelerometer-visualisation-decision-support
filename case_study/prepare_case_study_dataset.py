"""Prepare the NHANES 2011-2014 case-study dataset.

This script reconstructs the accelerometer-derived metrics needed for the
visualisation case study. It intentionally focuses on direct accelerometer
metrics, not model outputs.

Expected folder layout when copied to the case-study folder:

Case study/
    NHANES 2011-2012/
        DEMO_G.xpt, BMX_G.xpt, PAXHD_G.xpt, PAXDAY_G.xpt, PFQ_G.xpt
    NHANES 2013-2014/
        DEMO_H.xpt, BMX_H.xpt, PAXHD_H.xpt, PAXDAY_H.xpt, PFQ_H.xpt
    scripts/
        prepare_case_study_dataset.py
    outputs/
        generated files
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


# pandas can read true zeroes from these SAS transport files as tiny positive
# numbers. Treating those as zero is essential for valid-day filters.
ZERO_TOLERANCE = 1e-20

VALID_MINUTES_MIN = 1_380  # 23 hours
NONWEAR_MINUTES_MAX = 72  # <5% of 24 hours
SLEEP_MINUTES_MAX = 1_020  # <17 hours

CYCLES = {
    "NHANES 2011-2012": "G",
    "NHANES 2013-2014": "H",
}

SOURCE_LINKS = [
    "NHANES 2011-2012 data page: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2011",
    "NHANES 2013-2014 data page: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013",
    "PAXDAY codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PAXDAY_G.htm",
    "PAXHD codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PAXHD_G.htm",
    "PFQ codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/PFQ_G.htm",
    "BMX codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/BMX_G.htm",
    "DEMO codebook: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/DEMO_G.htm",
]


@dataclass(frozen=True)
class Paths:
    base: Path
    output: Path


def find_base_dir() -> Path:
    """Return the case-study folder from the script location."""
    script_path = Path(__file__).resolve()
    if script_path.parent.name == "scripts":
        return script_path.parent.parent
    return script_path.parent


def read_xpt(path: Path) -> pd.DataFrame:
    """Read an NHANES XPT file and normalize near-zero numeric values."""
    df = pd.read_sas(path, format="xport", encoding="latin1")
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].mask(df[numeric_cols].abs() < ZERO_TOLERANCE, 0)
    return df


def to_numeric(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def load_cycle(paths: Paths, cycle: str, suffix: str) -> dict[str, pd.DataFrame]:
    folder = paths.base / cycle
    files = {
        "demo": folder / f"DEMO_{suffix}.xpt",
        "bmx": folder / f"BMX_{suffix}.xpt",
        "paxhd": folder / f"PAXHD_{suffix}.xpt",
        "paxday": folder / f"PAXDAY_{suffix}.xpt",
        "pfq": folder / f"PFQ_{suffix}.xpt",
    }
    missing = [str(path) for path in files.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required NHANES files:\n" + "\n".join(missing))

    loaded = {name: read_xpt(path) for name, path in files.items()}
    for df in loaded.values():
        df["cycle"] = cycle
    return loaded


def build_file_inventory(paths: Paths) -> pd.DataFrame:
    rows = []
    for cycle, suffix in CYCLES.items():
        for stem in ["DEMO", "BMX", "PAXHD", "PAXDAY", "PFQ"]:
            path = paths.base / cycle / f"{stem}_{suffix}.xpt"
            df = read_xpt(path)
            rows.append(
                {
                    "cycle": cycle,
                    "file": path.name,
                    "rows": len(df),
                    "columns_n": len(df.columns),
                    "unique_participants": int(df["SEQN"].nunique()) if "SEQN" in df else np.nan,
                    "columns": ", ".join(df.columns),
                }
            )
    return pd.DataFrame(rows)


def load_all(paths: Paths) -> dict[str, pd.DataFrame]:
    combined: dict[str, list[pd.DataFrame]] = {
        "demo": [],
        "bmx": [],
        "paxhd": [],
        "paxday": [],
        "pfq": [],
    }
    for cycle, suffix in CYCLES.items():
        loaded = load_cycle(paths, cycle, suffix)
        for name, df in loaded.items():
            combined[name].append(df)

    out = {name: pd.concat(frames, ignore_index=True) for name, frames in combined.items()}
    out["paxhd"] = to_numeric(out["paxhd"], ["PAXHAND", "PAXORENT", "PAXFDAY", "PAXLDAY"])
    out["paxday"] = to_numeric(out["paxday"], ["PAXDAYD", "PAXDAYWD"])
    return out


def build_person_file(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    demo_cols = [
        "SEQN",
        "cycle",
        "RIDAGEYR",
        "RIAGENDR",
        "RIDRETH3",
        "RIDEXPRG",
        "DMDEDUC2",
        "DMDMARTL",
        "INDFMPIR",
        "WTMEC2YR",
        "SDMVPSU",
        "SDMVSTRA",
    ]
    bmx_cols = ["SEQN", "cycle", "BMXBMI", "BMDBMIC"]
    paxhd_cols = ["SEQN", "cycle", "PAXSTS", "PAXHAND", "PAXORENT"]
    pfq_cols = ["SEQN", "cycle", "PFQ054", "PFQ090"]

    return (
        data["demo"][demo_cols]
        .merge(data["bmx"][bmx_cols], on=["SEQN", "cycle"], how="left")
        .merge(data["paxhd"][paxhd_cols], on=["SEQN", "cycle"], how="left")
        .merge(data["pfq"][pfq_cols], on=["SEQN", "cycle"], how="left")
    )


def apply_participant_exclusions(person: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mask = pd.Series(True, index=person.index)
    rows = []

    def step(label: str, condition: pd.Series) -> None:
        nonlocal mask
        before = int(mask.sum())
        mask &= condition.fillna(False)
        after = int(mask.sum())
        rows.append(
            {
                "step": label,
                "n_before": before,
                "n_after": after,
                "n_excluded": before - after,
            }
        )

    step("Age >= 6 years", person["RIDAGEYR"] >= 6)
    step("PAM summary data available (PAXSTS == 1)", person["PAXSTS"] == 1)
    step("PAM worn on non-dominant hand (PAXHAND == 1)", person["PAXHAND"] == 1)
    step(
        "Not known pregnant at exam (exclude RIDEXPRG == 1)",
        person["RIDEXPRG"].ne(1) | person["RIDEXPRG"].isna(),
    )
    step(
        "Does not need special equipment to walk (exclude PFQ054 == 1)",
        person["PFQ054"].ne(1) | person["PFQ054"].isna(),
    )
    step("Positive MEC exam weight", person["WTMEC2YR"] > 0)

    return person.loc[mask].copy(), pd.DataFrame(rows)


def build_valid_days(paxday: pd.DataFrame, eligible_people: pd.DataFrame) -> pd.DataFrame:
    valid_day = paxday.merge(
        eligible_people[["SEQN", "cycle"]],
        on=["SEQN", "cycle"],
        how="inner",
    )
    valid_day["is_candidate_full_day"] = valid_day["PAXDAYD"].between(2, 8)
    valid_day["is_weekend"] = valid_day["PAXDAYWD"].isin([1, 7])
    valid_day["day_type"] = np.where(valid_day["is_weekend"], "weekend", "weekday")
    valid_day["is_valid_day"] = (
        valid_day["is_candidate_full_day"]
        & (valid_day["PAXVMD"] >= VALID_MINUTES_MIN)
        & (valid_day["PAXNWMD"] < NONWEAR_MINUTES_MAX)
        & (valid_day["PAXSWMD"] < SLEEP_MINUTES_MAX)
    )

    keep_cols = [
        "SEQN",
        "cycle",
        "PAXDAYD",
        "PAXDAYWD",
        "day_type",
        "PAXVMD",
        "PAXMTSD",
        "PAXWWMD",
        "PAXSWMD",
        "PAXNWMD",
        "PAXUMD",
        "PAXQFD",
        "is_candidate_full_day",
        "is_valid_day",
    ]
    return valid_day[keep_cols].copy()


def recode_people(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["WTMEC4YR"] = out["WTMEC2YR"] / 2

    out["sample"] = np.select(
        [out["RIDAGEYR"].between(6, 19), out["RIDAGEYR"] >= 20],
        ["Children/adolescents 6-19", "Adults 20+"],
        default="Other",
    )
    out["sex"] = out["RIAGENDR"].map({1: "Male", 2: "Female"})
    out["race_ethnicity"] = out["RIDRETH3"].map(
        {
            1: "Mexican American",
            2: "Other Hispanic",
            3: "Non-Hispanic White",
            4: "Non-Hispanic Black",
            6: "Non-Hispanic Asian",
            7: "Other/multiracial",
        }
    )
    out["age_group"] = pd.cut(
        out["RIDAGEYR"],
        bins=[5, 11, 19, 39, 59, np.inf],
        labels=["6-11", "12-19", "20-39", "40-59", "60+"],
    ).astype("object")
    out["income_poverty_category"] = pd.cut(
        out["INDFMPIR"],
        bins=[-np.inf, 1.299999, 3.499999, np.inf],
        labels=["<1.30", "1.30-3.49", ">=3.50"],
    ).astype("object")

    out["education_adult"] = out["DMDEDUC2"].map(
        {
            1: "Less than 9th grade",
            2: "9-11th grade",
            3: "High school/GED",
            4: "Some college/AA",
            5: "College graduate or above",
        }
    )
    out.loc[out["sample"] != "Adults 20+", "education_adult"] = np.nan

    out["marital_status_adult"] = out["DMDMARTL"].map(
        {
            1: "Married",
            2: "Widowed",
            3: "Divorced",
            4: "Separated",
            5: "Never married",
            6: "Living with partner",
        }
    )
    out.loc[out["sample"] != "Adults 20+", "marital_status_adult"] = np.nan

    out["bmi_category_adult"] = pd.cut(
        out["BMXBMI"],
        bins=[-np.inf, 18.5, 25, 30, np.inf],
        labels=["Underweight", "Healthy weight", "Overweight", "Obesity"],
        right=False,
    ).astype("object")
    out.loc[out["sample"] != "Adults 20+", "bmi_category_adult"] = np.nan

    out["bmi_category_child"] = out["BMDBMIC"].map(
        {
            1: "Underweight",
            2: "Healthy weight",
            3: "Overweight",
            4: "Obesity",
        }
    )
    out.loc[out["sample"] != "Children/adolescents 6-19", "bmi_category_child"] = np.nan

    out["bmi_status_for_sample"] = np.where(
        out["sample"] == "Adults 20+",
        out["bmi_category_adult"],
        out["bmi_category_child"],
    )
    return out


def build_participant_metrics(
    eligible_people: pd.DataFrame,
    valid_days: pd.DataFrame,
) -> pd.DataFrame:
    valid = valid_days[valid_days["is_valid_day"]].copy()
    day_summary = (
        valid.groupby(["SEQN", "cycle", "day_type"])
        .agg(
            mean_mims=("PAXMTSD", "mean"),
            n_valid_days=("PAXMTSD", "size"),
        )
        .reset_index()
    )
    wide = day_summary.pivot(
        index=["SEQN", "cycle"],
        columns="day_type",
        values=["mean_mims", "n_valid_days"],
    )
    wide.columns = ["_".join(col).strip() for col in wide.columns]
    wide = wide.reset_index()
    for col in [
        "mean_mims_weekday",
        "mean_mims_weekend",
        "n_valid_days_weekday",
        "n_valid_days_weekend",
    ]:
        if col not in wide.columns:
            wide[col] = np.nan

    participant = eligible_people.merge(wide, on=["SEQN", "cycle"], how="left")
    participant["meets_valid_day_rule"] = (
        (participant["n_valid_days_weekday"] >= 3)
        & (participant["n_valid_days_weekend"] >= 1)
    )
    participant = participant[participant["meets_valid_day_rule"]].copy()
    participant["weekday_minus_weekend_mims"] = (
        participant["mean_mims_weekday"] - participant["mean_mims_weekend"]
    )
    participant["pct_difference_from_weekday"] = (
        participant["weekday_minus_weekend_mims"] / participant["mean_mims_weekday"] * 100
    )
    return recode_people(participant)


def survey_weighted_mean_ci(
    df: pd.DataFrame,
    value_col: str,
    weight_col: str = "WTMEC4YR",
    strata_col: str = "SDMVSTRA",
    psu_col: str = "SDMVPSU",
) -> dict[str, float]:
    """Approximate weighted mean and Taylor-linearised CI.

    This is designed for visualisation estimates, not for exact replication of
    the published inferential analysis.
    """
    data = df.dropna(subset=[value_col, weight_col, strata_col, psu_col]).copy()
    data = data[data[weight_col] > 0]
    if data.empty:
        return {
            "estimate": np.nan,
            "se": np.nan,
            "ci_low": np.nan,
            "ci_high": np.nan,
            "unweighted_n": 0,
            "weighted_n": np.nan,
        }

    weights = data[weight_col]
    y = data[value_col]
    estimate = float(np.average(y, weights=weights))

    denominator = weights.sum()
    data["_linearized"] = weights * (y - estimate) / denominator
    psu_totals = (
        data.groupby([strata_col, psu_col], dropna=True)["_linearized"]
        .sum()
        .reset_index()
    )

    variance = 0.0
    for _, stratum in psu_totals.groupby(strata_col):
        m = len(stratum)
        if m <= 1:
            continue
        centered = stratum["_linearized"] - stratum["_linearized"].mean()
        variance += float(m / (m - 1) * np.square(centered).sum())

    se = float(np.sqrt(max(variance, 0.0)))
    return {
        "estimate": estimate,
        "se": se,
        "ci_low": estimate - 1.96 * se,
        "ci_high": estimate + 1.96 * se,
        "unweighted_n": int(len(data)),
        "weighted_n": float(weights.sum()),
    }


def summarize_domain(
    participant: pd.DataFrame,
    domain: str,
    levels: Iterable[str] | None = None,
) -> pd.DataFrame:
    metric_map = {
        "Weekday MIMS-units": "mean_mims_weekday",
        "Weekend-day MIMS-units": "mean_mims_weekend",
        "Weekday minus weekend MIMS-units": "weekday_minus_weekend_mims",
        "Percent difference from weekday": "pct_difference_from_weekday",
    }
    rows = []
    source = participant.copy()

    if levels is None:
        levels = [level for level in source[domain].dropna().unique()]

    for sample in ["Children/adolescents 6-19", "Adults 20+"]:
        sample_df = source[source["sample"] == sample]
        for level in levels:
            level_df = sample_df[sample_df[domain] == level]
            if level_df.empty:
                continue
            for metric_label, metric_col in metric_map.items():
                stats = survey_weighted_mean_ci(level_df, metric_col)
                rows.append(
                    {
                        "sample": sample,
                        "domain": domain,
                        "level": level,
                        "metric": metric_label,
                        **stats,
                    }
                )
    return pd.DataFrame(rows)


def build_summary_estimates(participant: pd.DataFrame) -> pd.DataFrame:
    domains = [
        "sample",
        "sex",
        "age_group",
        "race_ethnicity",
        "income_poverty_category",
        "education_adult",
        "marital_status_adult",
        "bmi_status_for_sample",
    ]
    summaries = [summarize_domain(participant, domain) for domain in domains]
    return pd.concat([s for s in summaries if not s.empty], ignore_index=True)


def build_report(
    inventory: pd.DataFrame,
    exclusions: pd.DataFrame,
    valid_days: pd.DataFrame,
    participant: pd.DataFrame,
    estimates: pd.DataFrame,
) -> str:
    valid_by_cycle = (
        valid_days.groupby("cycle")
        .agg(
            day_records=("SEQN", "size"),
            candidate_full_days=("is_candidate_full_day", "sum"),
            valid_days=("is_valid_day", "sum"),
        )
        .reset_index()
    )
    valid_by_type = (
        valid_days.groupby("day_type")
        .agg(
            candidate_full_days=("is_candidate_full_day", "sum"),
            valid_days=("is_valid_day", "sum"),
        )
        .reset_index()
    )
    sample_counts = participant["sample"].value_counts().rename_axis("sample").reset_index(name="n")
    cycle_counts = participant["cycle"].value_counts().rename_axis("cycle").reset_index(name="n")

    overall = estimates[estimates["domain"] == "sample"].copy()
    overall = overall[
        [
            "sample",
            "level",
            "metric",
            "estimate",
            "ci_low",
            "ci_high",
            "unweighted_n",
        ]
    ]

    lines = [
        "# Case Study Dataset Audit",
        "",
        "This report checks whether the uploaded NHANES files are sufficient to reconstruct the accelerometer-derived metrics needed for the worked case study.",
        "",
        "## Short Answer",
        "",
        "The uploaded files are sufficient to reconstruct the direct accelerometer metrics needed for the visualisation case study: participant-level mean weekday MIMS-units, mean weekend-day MIMS-units, weekday-minus-weekend differences, and percentage differences from weekday activity.",
        "",
        "Exact replication of every published estimate may still require checking the paper's precise subgroup recoding and inferential procedure. The current script uses NHANES MEC four-year weights and an approximate Taylor-linearised confidence interval for visualisation estimates.",
        "",
        "## Files Checked",
        "",
        inventory[["cycle", "file", "rows", "columns_n", "unique_participants"]].to_markdown(index=False),
        "",
        "## Key Variables Available",
        "",
        "- `PAXMTSD`: day-level MIMS triaxial value.",
        "- `PAXDAYD`: wear day number; days 2-8 are treated as complete candidate days.",
        "- `PAXDAYWD`: day of week; Sunday and Saturday are weekend days.",
        "- `PAXVMD`: valid minutes in the day.",
        "- `PAXNWMD`: valid non-wear minutes in the day.",
        "- `PAXSWMD`: valid sleep wear minutes in the day.",
        "- `PAXHAND`: non-dominant wrist placement.",
        "- `PFQ054`: need special equipment to walk.",
        "- `RIDEXPRG`: pregnancy status at exam.",
        "- `WTMEC2YR`, `SDMVSTRA`, `SDMVPSU`: NHANES weighting and design variables.",
        "- `BMXBMI`, `BMDBMIC`: adult BMI and child/adolescent BMI category variables.",
        "",
        "## Rules Implemented",
        "",
        f"- Include participants aged 6 years or older.",
        f"- Include participants with PAM summary data available (`PAXSTS == 1`).",
        f"- Keep non-dominant wrist placement only (`PAXHAND == 1`).",
        f"- Exclude participants known to be pregnant at exam (`RIDEXPRG == 1`).",
        f"- Exclude participants reporting special equipment needed to walk (`PFQ054 == 1`).",
        f"- Candidate full days are wear days 2-8.",
        f"- Valid days require at least {VALID_MINUTES_MIN} valid minutes, fewer than {NONWEAR_MINUTES_MAX} non-wear minutes, and fewer than {SLEEP_MINUTES_MAX} sleep wear minutes.",
        "- The analytic participant dataset requires at least 3 valid weekdays and at least 1 valid weekend day.",
        "- Four-year MEC weights are calculated as `WTMEC2YR / 2`.",
        "",
        "## Participant Exclusions",
        "",
        exclusions.to_markdown(index=False),
        "",
        "## Valid Day Counts",
        "",
        "By cycle:",
        "",
        valid_by_cycle.to_markdown(index=False),
        "",
        "By day type:",
        "",
        valid_by_type.to_markdown(index=False),
        "",
        "## Analytic Participant Counts",
        "",
        sample_counts.to_markdown(index=False),
        "",
        cycle_counts.to_markdown(index=False),
        "",
        "## First Overall Estimates",
        "",
        "These are preliminary visualisation estimates from the reproduced participant-level metrics. They are not intended as a final inferential reproduction until subgroup recoding and CI handling are checked against the paper.",
        "",
        overall.round(2).to_markdown(index=False),
        "",
        "## Outputs Created",
        "",
        "- `outputs/case_study_file_inventory.csv`",
        "- `outputs/case_study_exclusion_counts.csv`",
        "- `outputs/case_study_valid_day_metrics.csv`: all valid days after participant-level exclusions.",
        "- `outputs/case_study_analytic_valid_day_metrics.csv`: valid days for participants who meet the final 3-weekday/1-weekend rule.",
        "- `outputs/case_study_participant_metrics.csv`",
        "- `outputs/case_study_summary_estimates.csv`",
        "- `outputs/case_study_dataset_audit.md`",
        "",
        "## Remaining Checks Before Plotting",
        "",
        "- Compare the sample counts and overall estimates against the published paper tables.",
        "- Confirm whether the paper grouped children/adolescents as 6-19 years or used a narrower child age range.",
        "- Confirm exact subgroup categories for education, marital status, income-to-poverty ratio, and BMI.",
        "- Decide whether the case-study figures should use the approximate CIs generated here or values copied from a final survey-analysis reproduction.",
        "",
        "## Sources",
        "",
        *[f"- {link}" for link in SOURCE_LINKS],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    base = find_base_dir()
    paths = Paths(base=base, output=base / "outputs")
    paths.output.mkdir(exist_ok=True)

    inventory = build_file_inventory(paths)
    data = load_all(paths)
    person = build_person_file(data)
    eligible_people, exclusions = apply_participant_exclusions(person)
    valid_days = build_valid_days(data["paxday"], eligible_people)
    participant = build_participant_metrics(eligible_people, valid_days)
    estimates = build_summary_estimates(participant)
    analytic_valid_days = valid_days[valid_days["is_valid_day"]].merge(
        participant[["SEQN", "cycle"]],
        on=["SEQN", "cycle"],
        how="inner",
    )

    inventory.to_csv(paths.output / "case_study_file_inventory.csv", index=False)
    exclusions.to_csv(paths.output / "case_study_exclusion_counts.csv", index=False)
    valid_days[valid_days["is_valid_day"]].to_csv(
        paths.output / "case_study_valid_day_metrics.csv",
        index=False,
    )
    analytic_valid_days.to_csv(
        paths.output / "case_study_analytic_valid_day_metrics.csv",
        index=False,
    )
    participant.to_csv(paths.output / "case_study_participant_metrics.csv", index=False)
    estimates.to_csv(paths.output / "case_study_summary_estimates.csv", index=False)

    report = build_report(inventory, exclusions, valid_days, participant, estimates)
    (paths.output / "case_study_dataset_audit.md").write_text(report, encoding="utf-8")

    print("Case-study dataset preparation complete.")
    print(f"Base folder: {paths.base}")
    print(f"Outputs: {paths.output}")
    print(f"Analytic participants: {len(participant):,}")


if __name__ == "__main__":
    main()
