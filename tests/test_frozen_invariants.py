from pathlib import Path
import math
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]

def test_primary_model_and_cohort():
    p=pd.read_csv(ROOT/"results/verified_baseline/results/primary_logo_predictions.csv")
    assert len(p)==770
    assert p.groupby("model").size().to_dict()=={"dummy_mean":154,"hist_gbr":154,"linear":154,"random_forest":154,"ridge":154}
    lin=p[p.model=="linear"]
    assert lin.iso3.nunique()==154
    assert lin.region.nunique()==7
    m=pd.read_csv(ROOT/"results/verified_baseline/tables/primary_model_summary.csv").set_index("model")
    assert math.isclose(m.loc["linear","mae"],13.981872987542106,abs_tol=1e-12)
    assert math.isclose(m.loc["linear","r2"],0.5625520466303008,abs_tol=1e-12)

def test_income_reliability_gradient():
    s=pd.read_csv(ROOT/"results/verified_baseline/tables/primary_subgroup_metrics.csv")
    s=s[(s.model=="linear") & (s.group_type=="income_group")].set_index("group")
    assert s.loc["Low income","mae"] > s.loc["Lower middle income","mae"] > s.loc["Upper middle income","mae"] > s.loc["High income","mae"]
    assert math.isclose(s.loc["Low income","bias"],17.701214390261097,abs_tol=1e-12)

def test_conformal_and_ood():
    c=pd.read_csv(ROOT/"results/verified_baseline/results/primary_conformal_predictions.csv")
    covered=(c.y>=c.lo_global)&(c.y<=c.hi_global)
    assert math.isclose(covered.mean(),0.8506493506493507,abs_tol=1e-12)
    assert math.isclose(covered[c.income_group=="Low income"].mean(),0.5384615384615384,abs_tol=1e-12)
    rho,p=spearmanr(c.ood,(c.pred-c.y).abs())
    assert math.isclose(rho,0.03523236690524286,abs_tol=1e-12)
    assert p>0.6

def test_v2_decision_audit():
    r=pd.read_csv(ROOT/"results/v2_upgrade/v2_prioritization_rank_metrics.csv").set_index("metric")
    assert math.isclose(r.loc["deficit_rank_spearman","value"],0.8074889754750134,abs_tol=1e-12)
    assert math.isclose(r.loc["top_10pct_deficit_recall","value"],0.375,abs_tol=1e-12)
    t=pd.read_csv(ROOT/"results/v2_upgrade/v2_service_deficit_threshold_audit.csv").set_index("coverage_threshold")
    assert int(t.loc[25,"n_actual_below_or_equal"])==18
    assert int(t.loc[25,"n_predicted_below_or_equal"])==0
