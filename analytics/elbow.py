from sklearn.cluster import KMeans
def calculate_elbow(normalized, max_k=10):
    x=normalized[["Mean_Harga","Std_Harga"]].dropna(); rows=[]
    for k in range(1,min(max_k,len(x))+1): rows.append({"K":k,"WCSS":KMeans(n_clusters=k,n_init=10,random_state=42).fit(x).inertia_})
    return rows
