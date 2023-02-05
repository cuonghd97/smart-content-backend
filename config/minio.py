from minio import Minio

minio_client = Minio(
    "94.237.76.12:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)
