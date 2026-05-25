from datetime import datetime, date as date_type
from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import (
    ReportsRepository, FileRepository, DocumentsGostRepository,
    TestResultsRepository, ObservationPointRepository, ObservationDynamicRepository
)
from reports.schemas.report_models import (
    DraftInputData, FileCreate, DocumentsGostCreate, TestResultsCreate,
    ObservationPointCreate, ObservationDynamicCreate, ReportCreate
)


class SaveDraftUseCase:
    def __init__(
        self,
        postgres_repository: ReportsRepository,
        database: Database,
        file_repository: FileRepository,
        documents_gost_repository: DocumentsGostRepository,
        test_results_repository: TestResultsRepository,
        observation_point_repository: ObservationPointRepository,
        observation_dynamic_repository: ObservationDynamicRepository,
    ):
        self._postgres_repository = postgres_repository
        self._database = database
        self._file_repository = file_repository
        self._documents_gost_repository = documents_gost_repository
        self._test_results_repository = test_results_repository
        self._observation_point_repository = observation_point_repository
        self._observation_dynamic_repository = observation_dynamic_repository

    async def execute(self, data: DraftInputData) -> int:
        async with self._database.session() as session:
            try:
                gost_id = None
                if data.DOCUMENTS_GOST:
                    gost_data = DocumentsGostCreate(description=",".join(data.DOCUMENTS_GOST))
                    gost_id = await self._documents_gost_repository.add(gost_data, session)

                test_results_data = TestResultsCreate(
                    results_ph=data.RESULTS_PH,
                    results_iron=data.RESULTS_IRON,
                    results_manganese=data.RESULTS_MANGANESE,
                    results_nitrates=data.RESULTS_NITRATES,
                    results_sulfates=data.RESULTS_SULFATES,
                )
                test_results_id = await self._test_results_repository.add(test_results_data, session)

                def _parse_year(val):
                    try:
                        return datetime.strptime(str(val), "%Y").date() if val else None
                    except ValueError:
                        return None

                def _parse_decimal(val):
                    if val is None:
                        return None
                    try:
                        return float(str(val).replace(',', '.'))
                    except (ValueError, TypeError):
                        return None

                file_data = FileCreate(
                    full_object_name=data.FULL_OBJECT_NAME,
                    short_object_name=data.SHORT_OBJECT_NAME,
                    organization_name=data.ORGANIZATION_NAME,
                    region=data.REGION,
                    year=_parse_year(data.YEAR),
                    gost_id=gost_id,
                    relief_type=data.RELIEF_TYPE,
                    soil_type=data.SOIL_TYPE,
                    groundwater_level=_parse_decimal(data.GROUNDWATER_LEVEL),
                    climate_zone=data.CLIMATE_ZONE,
                    coordinates_latitude=_parse_decimal(data.COORDINATES_LATITUDE),
                    coordinates_longitude=_parse_decimal(data.COORDINATES_LONGITUDE),
                    object_type=data.OBJECT_TYPE,
                    system_type=data.SYSTEM_TYPE,
                    pipe_material=data.PIPE_MATERIAL,
                    pipe_diameter=_parse_decimal(data.PIPE_DIAMETER),
                    pipe_depth=_parse_decimal(data.PIPE_DEPTH),
                    pipe_length=_parse_decimal(data.PIPE_LENGTH),
                    pipe_install_year=_parse_year(data.PIPE_INSTALL_YEAR),
                    manhole_count=data.MANHOLE_COUNT,
                    monitoring_point_count=data.MONITORING_POINT_COUNT,
                    observation_frequency=data.OBSERVATION_FREQUENCY,
                    test_results_id=test_results_id,
                    selected_indicators=",".join(data.SELECTED_TEST_INDICATORS) if data.SELECTED_TEST_INDICATORS else None,
                    organization_address=data.ORGANIZATION_ADDRESS,
                    organization_phone=data.ORGANIZATION_PHONE,
                    organization_email=data.ORGANIZATION_EMAIL,
                    responsible_name=data.RESPONSIBLE_NAME,
                    responsible_position=data.RESPONSIBLE_POSITION,
                    report_date=datetime.strptime(data.REPORT_DATE, "%Y-%m-%d").date() if data.REPORT_DATE else None,
                )
                file_id = await self._file_repository.add(file_data, session)

                for pt in data.OBSERVATION_POINTS:
                    if not isinstance(pt, dict):
                        continue
                    point_data = ObservationPointCreate(
                        file_id=file_id,
                        observation_point=pt.get("observation_point"),
                        latitude=_parse_decimal(pt.get("latitude")),
                        longitude=_parse_decimal(pt.get("longitude")),
                        medium_type=pt.get("medium_type"),
                        description=pt.get("description"),
                    )
                    await self._observation_point_repository.add(point_data, session)

                def _parse_date(val):
                    if not val:
                        return None
                    try:
                        return datetime.strptime(str(val), "%Y-%m-%d").date()
                    except ValueError:
                        return None

                def _dec(val):
                    if val is None or str(val).strip() == "":
                        return None
                    try:
                        return float(str(val).replace(",", "."))
                    except (ValueError, TypeError):
                        return None

                for dyn in data.OBSERVATION_DYNAMICS:
                    if isinstance(dyn, dict):
                        dyn_data = ObservationDynamicCreate(
                            file_id=file_id,
                            dynamic_ph=_dec(dyn.get("pH") or dyn.get("ph")),
                            dynamic_iron=_dec(dyn.get("iron")),
                            dynamic_manganese=_dec(dyn.get("manganese")),
                            dynamic_nitrates=_dec(dyn.get("nitrates")),
                            dynamic_sulfates=_dec(dyn.get("sulfates")),
                            dynamic_data=_parse_date(dyn.get("date")),
                        )
                        await self._observation_dynamic_repository.add(dyn_data, session)

                report_data = ReportCreate(user_id=data.user_id, file_id=file_id, is_draft=True)
                await self._postgres_repository.add_report(report_data, session)

                await session.commit()
                return file_id
            except Exception as e:
                await session.rollback()
                raise e
