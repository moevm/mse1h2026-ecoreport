class S3Client:
    """
    Клиент для взаимодействия с S3-совместимым хранилищем.
    """
    async def upload(self, file_content: bytes, filename: str) -> str:
        return f"s3://reports/{filename}"
