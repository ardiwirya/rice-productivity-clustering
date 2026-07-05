import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


class AnomalyDetector:
    """Detects anomalous kecamatan and groups the rest into
    High / Medium / Low productivity clusters.

    Pipeline: StandardScaler -> IsolationForest decision scores
    (percentile-based threshold) -> KMeans on the non-anomalous subset.
    """

    def __init__(self, n_estimators=100, contamination=0.15, random_state=42):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state

    def analyze_data(self, df):
        if df.empty or len(df) < 3:
            return None

        features = ["Produktivitas", "Luas_Panen", "Produksi"]
        available_features = [f for f in features if f in df.columns]
        if not available_features:
            return None

        X = df[available_features].values
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # A small, seeded jitter keeps KMeans stable when many kecamatan
        # report near-identical productivity. Seeded so results are
        # reproducible across runs with the same parameters.
        rng = np.random.RandomState(self.random_state)
        X_scaled = X_scaled + rng.normal(0, 0.01, X_scaled.shape)

        iso_forest = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=min(self.contamination, 0.2),
            random_state=self.random_state,
            max_samples=min(256, len(X_scaled)),
        )
        iso_forest.fit(X_scaled)
        scores = iso_forest.decision_function(X_scaled)

        # Flag the lowest-scoring `contamination` fraction as anomalies.
        anomaly_threshold = np.percentile(scores, self.contamination * 100)
        is_anomaly = scores < anomaly_threshold

        non_anomaly_mask = ~is_anomaly
        X_non_anomaly = X_scaled[non_anomaly_mask]

        if len(X_non_anomaly) >= 3:
            n_clusters = min(3, max(2, len(X_non_anomaly) // 3))
            kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=20)
            clusters = kmeans.fit_predict(X_non_anomaly)

            original_data = df[available_features].values
            original_data = np.nan_to_num(original_data, nan=0.0)

            cluster_means = []
            for i in range(n_clusters):
                cluster_indices = np.where(non_anomaly_mask)[0][clusters == i]
                if len(cluster_indices) > 0:
                    productivity_values = original_data[cluster_indices, 0]
                    cluster_means.append(np.mean(productivity_values))
                else:
                    cluster_means.append(0)

            sorted_indices = np.argsort(cluster_means)[::-1]
            cluster_labels = ["Tinggi", "Sedang", "Rendah"][:n_clusters]
            cluster_map = {sorted_indices[i]: cluster_labels[i] for i in range(n_clusters)}
        else:
            clusters = np.zeros(len(X_non_anomaly))
            cluster_map = {0: "Sedang"}
            n_clusters = 1

        results = []
        cluster_idx = 0

        for i, (_, row) in enumerate(df.iterrows()):
            anomaly_score = scores[i]
            if is_anomaly[i]:
                final_cluster = "Anomali"
            elif len(X_non_anomaly) >= 3 and n_clusters >= 2:
                final_cluster = cluster_map[clusters[cluster_idx]]
                cluster_idx += 1
            else:
                final_cluster = "Sedang"

            results.append(
                {
                    "Kecamatan": row["Kecamatan"],
                    "Tahun": row["Tahun"],
                    "Produktivitas": row["Produktivitas"],
                    "Luas_Panen": row["Luas_Panen"],
                    "Produksi": row["Produksi"],
                    "Skor_Anomali": round(anomaly_score, 4),
                    "Klaster": final_cluster,
                }
            )

        silhouette = 0.0
        if len(X_non_anomaly) >= 2 and n_clusters >= 2:
            try:
                silhouette = silhouette_score(X_non_anomaly, clusters)
            except Exception:
                silhouette = 0.0

        return {
            "results": pd.DataFrame(results),
            "silhouette_score": silhouette,
            "anomaly_count": int(np.sum(is_anomaly)),
            "features_used": available_features,
        }
