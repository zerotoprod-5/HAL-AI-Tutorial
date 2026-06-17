"""
Regenerate the dark-themed SVG charts embedded in slides.html (the deck) into ../figs/.
Run with the validation venv:  /tmp/hal_val/bin/python build/make_figs.py
Charts are transparent so the slide background shows through; text is rendered as
vector paths (svg.fonttype='path') so they look identical on any machine, offline.
"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier

GREEN,RED,TEAL,AMBER,MUTED,GRID="#56c08a","#d4756b","#36b6c9","#e7a657","#88a1b2","#2b3f4f"
plt.rcParams.update({"svg.fonttype":"path","font.size":13,"font.family":"sans-serif",
    "text.color":"#cddde6","axes.labelcolor":"#cddde6","xtick.color":MUTED,"ytick.color":MUTED,
    "axes.edgecolor":GRID,"axes.linewidth":1.1})
FIG=os.path.join(os.path.dirname(__file__),"..","figs"); os.makedirs(FIG,exist_ok=True)
def base(ax):
    ax.set_facecolor("none")
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.tick_params(length=0); ax.grid(alpha=.16,color=TEAL,linewidth=.7)
def save(fig,name):
    fig.savefig(os.path.join(FIG,name),transparent=True,bbox_inches="tight"); plt.close(fig)
rng=np.random.default_rng(42)

# 1 pattern scatter + decision regions
n=240; temp=rng.normal(72,9,n); vib=np.clip(rng.normal(3,1,n),.4,None)
y=((.085*(temp-72)+.95*(vib-3)+rng.normal(0,.4,n))>.5).astype(int)
clf=LogisticRegression().fit(np.c_[temp,vib],y)
xx,yy=np.meshgrid(np.linspace(temp.min()-2,temp.max()+2,300),np.linspace(vib.min()-.3,vib.max()+.3,300))
Z=clf.predict(np.c_[xx.ravel(),yy.ravel()]).reshape(xx.shape)
fig,ax=plt.subplots(figsize=(7.4,4.8))
ax.contourf(xx,yy,Z,cmap=ListedColormap(["#1c3b34","#3a2626"]),alpha=.55,levels=1)
ax.scatter(temp[y==0],vib[y==0],c=GREEN,edgecolors="#0c1116",linewidth=.6,s=46,label="Worked fine",zorder=3)
ax.scatter(temp[y==1],vib[y==1],c=RED,edgecolors="#0c1116",linewidth=.6,s=46,label="Needed service",zorder=3)
ax.set_xlabel("Temperature  (°C)"); ax.set_ylabel("Vibration  (mm/s)")
ax.legend(loc="upper left",frameon=False,labelcolor="#cddde6"); base(ax); fig.tight_layout()
save(fig,"pattern_scatter.svg")

# 2 regression line
age=rng.uniform(0,14,120); cost=2500+950*age+rng.normal(0,1400,120)
lr=LinearRegression().fit(age.reshape(-1,1),cost); xs=np.linspace(0,14,100)
fig,ax=plt.subplots(figsize=(7.4,4.8))
ax.scatter(age,cost,c=TEAL,edgecolors="#0c1116",linewidth=.5,s=42,alpha=.85,zorder=3)
ax.plot(xs,lr.predict(xs.reshape(-1,1)),color=AMBER,lw=3,zorder=4,label="Line of best fit")
ax.set_xlabel("Machine age  (years)"); ax.set_ylabel("Monthly running cost  (₹)")
ax.legend(loc="upper left",frameon=False,labelcolor="#cddde6"); base(ax); fig.tight_layout()
save(fig,"regression_line.svg")

# 3 forecast
m=np.arange(36); demand=140+3.2*m+22*np.sin(2*np.pi*m/12)+rng.normal(0,7,36)
F=np.c_[m,np.sin(2*np.pi*m/12),np.cos(2*np.pi*m/12)]; lr=LinearRegression().fit(F,demand)
fm=np.arange(36,44); fc=lr.predict(np.c_[fm,np.sin(2*np.pi*fm/12),np.cos(2*np.pi*fm/12)])
fig,ax=plt.subplots(figsize=(7.4,4.8))
ax.plot(m,demand,color=TEAL,lw=2.4,marker="o",ms=4,label="History (what happened)",zorder=3)
ax.plot(np.r_[m[-1],fm],np.r_[demand[-1],fc],color=AMBER,lw=2.6,ls="--",marker="o",ms=4,label="Forecast (next months)",zorder=4)
ax.axvline(35.5,color=MUTED,ls=":",lw=1.2); ax.text(35.5,ax.get_ylim()[1]*.98,"  today",color=MUTED,va="top",fontsize=11)
ax.set_xlabel("Month"); ax.set_ylabel("Spare-parts demand  (units)")
ax.legend(loc="upper left",frameon=False,labelcolor="#cddde6"); base(ax); fig.tight_layout()
save(fig,"forecast.svg")

# 4 feature importance (vibration leads, matching the notebook + the deck narrative)
N=600; temp=rng.normal(72,10,N); vib=np.clip(rng.normal(3,1.1,N),.3,None)
press=rng.normal(5,1.2,N); oil=rng.uniform(40,100,N); hrs=rng.uniform(0,2000,N)
score=1.7*(vib-3)+.045*(temp-72)+.0009*hrs+.12*abs(press-5)-.012*(oil-70)+rng.normal(0,.32,N)
yy2=(score>np.quantile(score,.78)).astype(int)
rf=RandomForestClassifier(n_estimators=200,max_depth=8,random_state=0).fit(np.c_[temp,vib,press,oil,hrs],yy2)
names=np.array(["Temperature","Vibration","Pressure","Oil quality","Hours since service"])
imp=rf.feature_importances_; order=np.argsort(imp)
fig,ax=plt.subplots(figsize=(7.4,4.8))
ax.barh(names[order],imp[order],color=TEAL,edgecolor="#0c1116",height=.66)
ax.set_xlabel("How much the model relied on each sensor")
base(ax); ax.grid(axis="y",alpha=0); fig.tight_layout()
save(fig,"feature_importance.svg")

print("regenerated 4 charts ->", os.path.normpath(FIG))
