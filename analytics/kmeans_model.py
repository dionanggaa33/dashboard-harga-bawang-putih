from sklearn.cluster import KMeans
def fit_model(normalized, k):
    cols=["Mean_Harga","Std_Harga"]; model=KMeans(n_clusters=k,n_init=10,random_state=42).fit(normalized[cols])
    labels=normalized[["Kabupaten"]].copy(); labels["Cluster"]=model.labels_
    return labels, model.cluster_centers_
