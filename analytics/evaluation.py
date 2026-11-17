from sklearn.metrics import silhouette_score, davies_bouldin_score
def evaluate(x, labels): return silhouette_score(x,labels), davies_bouldin_score(x,labels)
