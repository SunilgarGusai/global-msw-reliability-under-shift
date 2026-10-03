from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
models=pd.read_csv(ROOT/"results/verified_baseline/tables/primary_model_summary.csv").set_index("model")
sg=pd.read_csv(ROOT/"results/verified_baseline/tables/primary_subgroup_metrics.csv")
sg=sg[(sg.model=="linear") & (sg.group_type=="income_group")].set_index("group")
rank=pd.read_csv(ROOT/"results/v2_upgrade/v2_prioritization_rank_metrics.csv").set_index("metric")
print("Global MSW reliability frozen summary")
print(f"Linear LORO: MAE={models.loc['linear','mae']:.2f}, RMSE={models.loc['linear','rmse']:.2f}, R2={models.loc['linear','r2']:.3f}")
print(f"Low income: MAE={sg.loc['Low income','mae']:.2f}, bias={sg.loc['Low income','bias']:+.2f}")
print(f"High income: MAE={sg.loc['High income','mae']:.2f}, bias={sg.loc['High income','bias']:+.2f}")
print(f"Deficit-rank Spearman={rank.loc['deficit_rank_spearman','value']:.3f}")
print(f"Worst-10% deficit recall={rank.loc['top_10pct_deficit_recall','value']:.3f}")
