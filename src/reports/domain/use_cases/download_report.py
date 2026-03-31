from reports.infrastructure.minio.repository import MinioRepository


class DownloadReportUseCase:
    def __init__(self,
                 minio_repository: MinioRepository):
        self._minio_repository = minio_repository

    async def execute(self, report_id: str) -> bytes:
        report_name = f"{report_id}.pdf"
        return self._minio_repository.get_object(report_name)
