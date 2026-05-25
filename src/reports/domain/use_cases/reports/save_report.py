from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import (
    ReportsRepository, FileRepository, DocumentsGostRepository,
    TestResultsRepository, ObservationPointRepository, ObservationDynamicRepository
)
from reports.schemas.report_models import (
    ReportInputData, FileCreate, DocumentsGostCreate, TestResultsCreate,
    ObservationPointCreate, ObservationDynamicCreate, GeneratedReportData
)
from datetime import datetime

class SaveDataUseCase:
    def __init__(
        self, 
        postgres_repository: ReportsRepository, 
        database: Database,
        file_repository: FileRepository,
        documents_gost_repository: DocumentsGostRepository,
        test_results_repository: TestResultsRepository,
        observation_point_repository: ObservationPointRepository,
        observation_dynamic_repository: ObservationDynamicRepository
    ):
        self._postgres_repository = postgres_repository
        self._database = database
        self._file_repository = file_repository
        self._documents_gost_repository = documents_gost_repository
        self._test_results_repository = test_results_repository
        self._observation_point_repository = observation_point_repository
        self._observation_dynamic_repository = observation_dynamic_repository

    async def execute(self, data: ReportInputData):
        async with self._database.session() as session:
            try:
                gost_data = DocumentsGostCreate(description=",".join(data.DOCUMENTS_GOST))
                gost_id = await self._documents_gost_repository.add(gost_data, session)

                test_results_data = TestResultsCreate(
                    results_ph=data.RESULTS_PH,
                    results_iron=data.RESULTS_IRON,
                    results_manganese=data.RESULTS_MANGANESE,
                    results_nitrates=data.RESULTS_NITRATES,
                    results_sulfates=data.RESULTS_SULFATES
                )
                test_results_id = await self._test_results_repository.add(test_results_data, session)

                file_data = FileCreate(
                    full_object_name=data.FULL_OBJECT_NAME,
                    short_object_name=data.SHORT_OBJECT_NAME,
                    organization_name=data.ORGANIZATION_NAME,
                    region=data.REGION,
                    year=datetime.strptime(str(data.YEAR), "%Y").date() if data.YEAR else None,
                    gost_id=gost_id,
                    relief_type=data.RELIEF_TYPE,
                    soil_type=data.SOIL_TYPE,
                    climate_zone=data.CLIMATE_ZONE,
                    coordinates_latitude=data.COORDINATES_LATITUDE,
                    coordinates_longitude=data.COORDINATES_LONGITUDE,
                    object_type=data.OBJECT_TYPE,
                    system_type=data.SYSTEM_TYPE,
                    pipe_material=data.PIPE_MATERIAL,
                    pipe_diameter=data.PIPE_DIAMETER,
                    pipe_depth=data.PIPE_DEPTH,
                    pipe_length=data.PIPE_LENGTH,
                    pipe_install_year=datetime.strptime(str(data.PIPE_INSTALL_YEAR), "%Y").date() if data.PIPE_INSTALL_YEAR else None,
                    manhole_count=data.MANHOLE_COUNT,
                    monitoring_point_count=data.MONITORING_POINT_COUNT,
                    observation_frequency=data.OBSERVATION_FREQUENCY,
                    test_results_id=test_results_id,
                    organization_address=data.ORGANIZATION_ADDRESS,
                    organization_phone=data.ORGANIZATION_PHONE,
                    organization_email=data.ORGANIZATION_EMAIL,
                    responsible_name=data.RESPONSIBLE_NAME,
                    responsible_position=data.RESPONSIBLE_POSITION
                )
                file_id = await self._file_repository.add(file_data, session)

                for pt in data.OBSERVATION_POINTS:
                    point_data = ObservationPointCreate(
                        file_id=file_id,
                        observation_point=pt.get("point") if isinstance(pt, dict) else str(pt),
                        latitude=pt.get("lat") if isinstance(pt, dict) else None,
                        longitude=pt.get("lon") if isinstance(pt, dict) else None,
                        medium_type=pt.get("type") if isinstance(pt, dict) else None,
                        description=pt.get("desc") if isinstance(pt, dict) else None
                    )
                    await self._observation_point_repository.add(point_data, session)

                for dyn in data.RESULTS_DYNAMIC:
                    dyn_data = ObservationDynamicCreate(
                        file_id=file_id,
                        dynamic_ph=dyn.pH,
                        dynamic_iron=dyn.iron,
                        dynamic_manganese=dyn.manganese,
                        dynamic_nitrates=dyn.nitrates,
                        dynamic_sulfates=dyn.sulfates
                    )
                    await self._observation_dynamic_repository.add(dyn_data, session)

                report_data = GeneratedReportData(
                    user_id=data.user_id,
                    file_name=str(file_id) 
                )
                await self._postgres_repository.add_report(report_data, session)
                
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
