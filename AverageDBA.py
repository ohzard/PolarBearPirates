# import numpy as np
# from tslearn.clustering import TimeSeriesKMeans
# from tslearn.preprocessing import TimeSeriesScalerMeanVariance
# from tslearn.barycenters import dtw_barycenter_averaging
# from pymongo import MongoClient
# from sklearn.preprocessing import LabelEncoder
# import matplotlib.pyplot as plt

# # MongoDB 연결 설정
# client = MongoClient("mongodb://localhost:27017/")
# db = client['PolarBear_Pirates']  # 데이터베이스 이름으로 변경
# collection = db['time-interval-stat']
# print("connection complete")

# # 특정 User Id와 TL에 해당하는 visited_venues 데이터 가져오기
# user_id = 15  # User ID로 변경
# TL = 'A'  # TL (M, A, E, N) 중 하나로 변경

# # MongoDB 쿼리
# query = {"User Id": user_id, "TL": TL}
# results = collection.find(query)

# # visited_venues 리스트 수집
# paths = [result['visited_venues'] for result in results]

# # 데이터가 비어 있는지 확인
# if not paths:
#     print("No data found for the specified user_id and TL.")
# else:
#     # 모든 장소 ID 수집
#     all_places = set(place for path in paths for place in path)

#     # 장소 ID를 숫자로 변환
#     le = LabelEncoder()
#     le.fit(list(all_places))
#     encoded_paths = [le.transform(path) for path in paths]

#     # 경로 데이터를 같은 길이로 패딩
#     max_len = max(len(path) for path in encoded_paths)
#     padded_paths = np.array([np.pad(path, (0, max_len - len(path)), 'constant', constant_values=-1) for path in encoded_paths])
#     print("=======================")
#     print(padded_paths)
#     print("=======================")

#     # K-means 클러스터링 수행
#     n_clusters = 3  # 클러스터 수 설정
#     km = TimeSeriesKMeans(n_clusters=n_clusters, metric="softdtw", verbose=True)
#     km.fit(padded_paths)

#     # 각 클러스터의 중심(평균) 경로를 확인
#     for i, barycenter in enumerate(km.cluster_centers_):
#         decoded_barycenter = le.inverse_transform(barycenter[barycenter != -1].astype(int))
#         print(f"Cluster {i} barycenter path: {decoded_barycenter}")

#     # 각 경로의 클러스터 할당
#     labels = km.labels_
#     for i, label in enumerate(labels):
#         decoded_path = le.inverse_transform(padded_paths[i][padded_paths[i] != -1].astype(int))
#         print(f"Path {i} is in cluster {label}: {decoded_path}")

#     # 클러스터링 결과 시각화
#     plt.figure(figsize=(10, 8))
#     colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # 다양한 색상 설정

#     for cluster in range(n_clusters):
#         cluster_indices = np.where(labels == cluster)[0]
#         for idx in cluster_indices:
#             plt.plot(padded_paths[idx][padded_paths[idx] != -1], color=colors[cluster % len(colors)], alpha=0.5)

#     for i, barycenter in enumerate(km.cluster_centers_):
#         plt.plot(barycenter[barycenter != -1], color=colors[i % len(colors)], linewidth=2, label=f'Cluster {i} center')

#     plt.title(f'Clustering of paths for User {user_id} at Time {TL}')
#     plt.xlabel('Steps')
#     plt.ylabel('Location ID')
#     plt.legend()
#     plt.show()

import numpy as np
from tslearn.clustering import TimeSeriesKMeans
from pymongo import MongoClient
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# MongoDB 연결 설정
client = MongoClient("mongodb://localhost:27017/")
db = client['PolarBear_Pirates']  # 데이터베이스 이름으로 변경
collection = db['time-interval-stat']
print("connection complete")

# 특정 User Id와 TL에 해당하는 visited_venues 데이터 가져오기
user_id = 15  # User ID로 변경
TL = 'A'  # TL (M, A, E, N) 중 하나로 변경

# MongoDB 쿼리
query = {"User Id": user_id, "TL": TL}
results = collection.find(query)

# visited_venues 리스트 수집
paths = [result['visited_venues'] for result in results]

# 데이터가 비어 있는지 확인
if not paths:
    print("No data found for the specified user_id and TL.")
else:
    # 모든 장소 ID 수집
    all_places = set(place for path in paths for place in path)

    # 장소 ID를 숫자로 변환
    le = LabelEncoder()
    le.fit(list(all_places))
    encoded_paths = [le.transform(path) for path in paths]

    # 경로 데이터를 같은 길이로 패딩
    max_len = max(len(path) for path in encoded_paths)
    padded_paths = np.array([np.pad(path, (0, max_len - len(path)), 'constant', constant_values=-1) for path in encoded_paths])

    # K-means 클러스터링 수행
    n_clusters = 3  # 클러스터 수 설정
    km = TimeSeriesKMeans(n_clusters=n_clusters, metric="softdtw", verbose=True)
    km.fit(padded_paths)

    # 각 클러스터의 중심(평균) 경로를 확인
    for i, barycenter in enumerate(km.cluster_centers_):
        # 패딩된 부분을 제거하고 원래 값으로 변환
        valid_indices = np.where(barycenter != -1)[0]
        valid_barycenter = barycenter[valid_indices]
        decoded_barycenter = le.inverse_transform(valid_barycenter.astype(int))
        print(f"Cluster {i} barycenter path: {decoded_barycenter}")

    # 각 경로의 클러스터 할당
    labels = km.labels_
    for i, label in enumerate(labels):
        valid_indices = np.where(padded_paths[i] != -1)[0]
        valid_path = padded_paths[i][valid_indices]
        decoded_path = le.inverse_transform(valid_path.astype(int))
        print(f"Path {i} is in cluster {label}: {decoded_path}")

    # 클러스터링 결과 시각화
    plt.figure(figsize=(10, 8))
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # 다양한 색상 설정

    for cluster in range(n_clusters):
        cluster_indices = np.where(labels == cluster)[0]
        for idx in cluster_indices:
            valid_indices = np.where(padded_paths[idx] != -1)[0]
            valid_path = padded_paths[idx][valid_indices]
            plt.plot(valid_path, color=colors[cluster % len(colors)], alpha=0.5)

    for i, barycenter in enumerate(km.cluster_centers_):
        valid_indices = np.where(barycenter != -1)[0]
        valid_barycenter = barycenter[valid_indices]
        plt.plot(valid_barycenter, color=colors[i % len(colors)], linewidth=2, label=f'Cluster {i} center')

    plt.title(f'Clustering of paths for User {user_id} at Time {TL}')
    plt.xlabel('Steps')
    plt.ylabel('Location ID')
    plt.legend()
    plt.show()

