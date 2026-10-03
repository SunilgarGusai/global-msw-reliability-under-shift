\
import numpy as np
import pandas as pd

from config import (
    DATA_RAW, DATA_PROCESSED, OUT_TABLES,
    PRIMARY_UNIT_PRIORITY, STRICT_CONTROLLED_TREATMENTS,
    PERMISSIVE_EXTRA_TREATMENTS
)
from common import checkpoint, save_json, add_engineered_features

def merge_wdi(base):
    df = base.copy()
    for name in ["gdp_ppp_pc", "urban_pct", "population", "pop_density"]:
        w = pd.read_csv(DATA_RAW / f"WDI_{name}.csv")
        w = w.rename(columns={"value": name})
        df = df.merge(w[["iso3", "year", name]], on=["iso3", "year"], how="left")
    meta = pd.read_csv(DATA_RAW / "world_bank_country_metadata.csv")
    df = df.merge(meta[["iso3", "income_group"]], on="iso3", how="left")
    return add_engineered_features(df)

def build_primary():
    d = pd.read_csv(DATA_RAW / "WM_COL_COV.csv")
    q = d[
        (d["URBANIZATION"] == "_T") &
        (d["EV_CRITERIA"] == "RC") &
        (d["UNIT_MEASURE"].isin(PRIMARY_UNIT_PRIORITY))
    ].copy()
    q["unit_priority"] = q["UNIT_MEASURE"].map(PRIMARY_UNIT_PRIORITY)
    q = q.sort_values(["REF_AREA", "unit_priority", "TIME_PERIOD"], ascending=[True, True, False])
    # Preferred measure first, then latest year within that measure.
    q = q.drop_duplicates("REF_AREA", keep="first")
    primary = pd.DataFrame({
        "iso3": q["REF_AREA"],
        "country": q["REF_AREA_LABEL"],
        "region": q["REGION_WB"],
        "year": q["TIME_PERIOD"].astype(int),
        "y": pd.to_numeric(q["OBS_VALUE"], errors="coerce"),
        "unit": q["UNIT_MEASURE"],
        "unit_label": q["UNIT_MEASURE_LABEL"],
        "source_url": q.get("SOURCE_URL"),
        "source": q.get("SOURCE"),
    })
    primary = merge_wdi(primary)
    primary.to_csv(DATA_PROCESSED / "primary_collection_cohort.csv", index=False)

    audit = {
        "n": int(len(primary)),
        "year_min": int(primary["year"].min()),
        "year_max": int(primary["year"].max()),
        "year_median": float(primary["year"].median()),
        "unit_counts": primary["unit"].value_counts(dropna=False).to_dict(),
        "region_counts": primary["region"].value_counts(dropna=False).to_dict(),
        "income_counts": primary["income_group"].value_counts(dropna=False).to_dict(),
        "coverage_summary": primary["y"].describe().to_dict(),
        "feature_nonmissing": {
            c: int(primary[c].notna().sum())
            for c in ["gdp_ppp_pc", "urban_pct", "population", "pop_density"]
        },
    }
    save_json(audit, OUT_TABLES / "primary_cohort_audit.json")
    return primary

def build_secondary():
    d = pd.read_csv(DATA_RAW / "WM_MSW_TREAT.csv")
    d["OBS_VALUE"] = pd.to_numeric(d["OBS_VALUE"], errors="coerce")
    rows = []
    for iso3, part in d.groupby("REF_AREA"):
        latest_year = int(part["TIME_PERIOD"].max())
        x = part[part["TIME_PERIOD"] == latest_year].copy()
        total_reported = float(x["OBS_VALUE"].sum(skipna=True))
        strict = float(x.loc[x["TREATMENT_TYPE_LABEL"].isin(STRICT_CONTROLLED_TREATMENTS), "OBS_VALUE"].sum())
        permissive_set = STRICT_CONTROLLED_TREATMENTS | PERMISSIVE_EXTRA_TREATMENTS
        permissive = float(x.loc[x["TREATMENT_TYPE_LABEL"].isin(permissive_set), "OBS_VALUE"].sum())
        rows.append({
            "iso3": iso3,
            "country": x["REF_AREA_LABEL"].iloc[0],
            "region": x["REGION_WB"].iloc[0],
            "year": latest_year,
            "strict_controlled": strict,
            "permissive_controlled": permissive,
            "ambiguity_delta": permissive - strict,
            "total_reported": total_reported,
            "has_unspecified_landfill": bool((x["TREATMENT_TYPE_LABEL"] == "Unspecified landfill").any()),
            "has_other": bool((x["TREATMENT_TYPE_LABEL"] == "Other").any()),
        })
    sec = pd.DataFrame(rows)
    sec = sec[sec["total_reported"].between(95, 102)].copy()
    sec = merge_wdi(sec)
    sec.to_csv(DATA_PROCESSED / "secondary_treatment_cohort.csv", index=False)

    audit = {
        "n": int(len(sec)),
        "year_min": int(sec["year"].min()),
        "year_max": int(sec["year"].max()),
        "since_2020_n": int((sec["year"] >= 2020).sum()),
        "ambiguity_delta_mean": float(sec["ambiguity_delta"].mean()),
        "ambiguity_delta_median": float(sec["ambiguity_delta"].median()),
        "unspecified_landfill_n": int(sec["has_unspecified_landfill"].sum()),
        "other_n": int(sec["has_other"].sum()),
    }
    save_json(audit, OUT_TABLES / "secondary_cohort_audit.json")
    return sec

def main():
    p = build_primary()
    s = build_secondary()
    checkpoint("02_build_cohorts", {"primary_n": len(p), "secondary_n": len(s)})
    print(f"PRIMARY N={len(p)} | SECONDARY N={len(s)}")
    print("PHASE 02 COMPLETE")

if __name__ == "__main__":
    main()
