from minio import Minio
from reports.core.config import settings

class MinioClient:
    def __init__(self, client: Minio):
        self.client = client

    def ensure_bucket(self, bucket_name: str) -> None:
        found = self.client.bucket_exists(bucket_name)
        if not found:
           self.client.make_bucket(bucket_name)
