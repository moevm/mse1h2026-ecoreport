from io import BytesIO
from minio import Minio
from reports.core.config import settings


class MinioRepository:
    def __init__(self, client: Minio):
        self._client = client

    def put_object(self, obj_id: str, obj: bytes, bucket: str = settings.MINIO_BUCKET_NAME) -> str:
        data = BytesIO(obj)

        result = self._client.put_object(
            bucket_name=bucket,
            object_name=f"{obj_id}.pdf",
            data=data,
            length=len(obj),
            content_type="application/pdf"
        )
        return result.object_name

    def get_object(self, obj_name: str, bucket: str = settings.MINIO_BUCKET_NAME) -> bytes:
        result = self._client.get_object(
            bucket,
            obj_name
        )

        try:
            data = result.read()
            return data
        finally:
            result.close()
            result.release_conn()

    def list_objects(self, bucket: str = settings.MINIO_BUCKET_NAME):
        return [
            obj
            for obj in self._client.list_objects(bucket_name=bucket, recursive=True)
            if not obj.is_dir
        ]