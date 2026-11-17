from sqlalchemy import create_engine
from warehouse.loader import URL
from .features import build_features
from .normalize import zscore
from .elbow import calculate_elbow
from .kmeans_model import fit_model
from .evaluation import evaluate
from .insight import summarize
def run_analysis():
    f=build_features(create_engine(URL)); n,p=zscore(f); e=calculate_elbow(n); k=next((r["K"] for i,r in enumerate(e[1:],1) if r["WCSS"] <= e[i-1]["WCSS"]*.5),3); labels,cent=fit_model(n,k); sil,db=evaluate(n[["Mean_Harga","Std_Harga"]],labels.Cluster); summary,ins=summarize(f,labels)
    return dict(features=f,normalized=n,normalization_params=p,elbow_data=e,k_optimal=k,labels=labels,centroids=cent,silhouette=sil,dbi=db,cluster_summary=summary,insight_text=ins)
