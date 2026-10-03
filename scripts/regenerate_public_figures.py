from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"figures/reproduced_public"
OUT.mkdir(parents=True,exist_ok=True)

def save(fig,name):
    fig.tight_layout()
    fig.savefig(OUT/f"{name}.png",dpi=300,bbox_inches="tight")
    fig.savefig(OUT/f"{name}.pdf",bbox_inches="tight")
    plt.close(fig)

def wilson(k,n,z=1.959963984540054):
    p=k/n; den=1+z*z/n
    center=(p+z*z/(2*n))/den
    half=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return center-half,center+half

# Figure 2
m=pd.read_csv(ROOT/"results/verified_baseline/tables/primary_model_summary.csv")
order=["linear","ridge","random_forest","hist_gbr","dummy_mean"]
m=m.set_index("model").loc[order].reset_index()
fig,ax=plt.subplots(figsize=(7.2,4.6)); x=np.arange(len(m)); ax.bar(x,m.mae)
ax.set_xticks(x,["linear","ridge","random forest","hist. GBR","dummy mean"],rotation=18,ha="right")
ax.set_ylabel("Leave-one-region-out MAE (percentage points)")
for i,v in enumerate(m.mae): ax.text(i,v+0.4,f"{v:.2f}",ha="center",fontsize=8)
save(fig,"Fig2_Model_Comparison")

# Figure 3 from linear OOF with deterministic bootstrap
p=pd.read_csv(ROOT/"results/verified_baseline/results/primary_logo_predictions.csv")
p=p[p.model=="linear"].copy(); p["ae"]=(p.pred-p.y).abs()
inc=["Low income","Lower middle income","Upper middle income","High income"]
vals=[]; lows=[]; highs=[]; rng=np.random.default_rng(19019)
for g in inc:
    x=p.loc[p.income_group==g,"ae"].to_numpy(); reps=x[rng.integers(0,len(x),size=(20000,len(x)))].mean(axis=1)
    vals.append(x.mean()); lows.append(np.quantile(reps,.025)); highs.append(np.quantile(reps,.975))
fig,ax=plt.subplots(figsize=(7.2,4.8)); xx=np.arange(4); ax.bar(xx,vals,hatch=["///","xx","..","\\\\"])
ax.errorbar(xx,vals,yerr=[np.array(vals)-lows,np.array(highs)-vals],fmt="none",capsize=4)
ax.set_xticks(xx,["Low","Lower-middle","Upper-middle","High"]); ax.set_ylabel("MAE (percentage points)"); ax.set_xlabel("Current World Bank income group")
save(fig,"Fig3_Income_MAE")

# Figure 4 region MAE
reg=p.groupby("region").agg(mae=("ae","mean"),n=("iso3","size")).sort_values("mae",ascending=False)
fig,ax=plt.subplots(figsize=(8.3,4.8)); xx=np.arange(len(reg)); ax.bar(xx,reg.mae)
labels=["Sub-Saharan Africa","S. Asia","Mid. East & N. Africa","L. Amer. & Caribbean","E. Asia & Pacific","Eur. & Cent. Asia","N. Amer."]
# use computed order to avoid assuming exact label ordering
ax.set_xticks(xx,reg.index,rotation=28,ha="right"); ax.set_ylabel("MAE (percentage points)")
for i,(v,n) in enumerate(zip(reg.mae,reg.n)): ax.text(i,v+0.35,f"{v:.1f}\n(n={n})",ha="center",fontsize=7)
save(fig,"Fig4_Regional_MAE")

# Figures 5-6 conformal/OOD
c=pd.read_csv(ROOT/"results/verified_baseline/results/primary_conformal_predictions.csv")
c["covered"]=(c.y>=c.lo_global)&(c.y<=c.hi_global); c["abs_error"]=(c.pred-c.y).abs()
vals=[]; lo=[]; hi=[]; ns=[]
for g in inc:
    z=c[c.income_group==g]; k=int(z.covered.sum()); n=len(z); l,h=wilson(k,n); vals.append(k/n);lo.append(l);hi.append(h);ns.append(n)
fig,ax=plt.subplots(figsize=(7.2,4.8)); xx=np.arange(4); ax.bar(xx,vals,hatch=["///","xx","..","\\\\"])
ax.errorbar(xx,vals,yerr=[np.array(vals)-lo,np.array(hi)-vals],fmt="none",capsize=4); ax.axhline(.9,linestyle="--",linewidth=1)
ax.set_ylim(0,1.08); ax.set_xticks(xx,["Low","Lower-middle","Upper-middle","High"]); ax.set_ylabel("Empirical interval coverage"); ax.set_xlabel("Current World Bank income group")
save(fig,"Fig5_Conformal_Coverage")

from scipy.stats import spearmanr
rho,pv=spearmanr(c.ood,c.abs_error)
fig,ax=plt.subplots(figsize=(6.6,5.2)); ax.scatter(c.ood,c.abs_error,s=24)
coef=np.polyfit(c.ood,c.abs_error,1); xs=np.linspace(c.ood.min(),c.ood.max(),100); ax.plot(xs,coef[0]*xs+coef[1],linestyle="--",linewidth=1)
ax.set_xlabel("Mahalanobis out-of-distribution score"); ax.set_ylabel("Absolute prediction error (percentage points)"); ax.text(.04,.95,rf"Spearman $\rho$ = {rho:.3f}; p = {pv:.3f}",transform=ax.transAxes,va="top")
save(fig,"Fig6_OOD_vs_Error")

# Reuse exact V2 audit code for Figs 7-8 by recomputing into temp output
print(f"Public figures regenerated in {OUT}")
