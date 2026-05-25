from datetime import datetime, date as date_type
from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import (
    ReportsRepository, FileRepository, DocumentsGostRepository,
    TestResultsRepository, ObservationPointRepository, ObservationDynamicRepository
)
from reports.schemas.report_models import (
    DraftInputData, FileUpdate, DocumentsGostUpdate, TestResultsUpdate,
    ObservationPointCreate, ObservationDynamicCreate
)


class UpdateDraftUseCase:
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

    async def execute(self, file_id: int, user_id: int, data: DraftInputData, promote: bool = False) -> None:
        async with self._database.session() as session:
            try:
                draft = await self._postgres_repository.get_draft_by_file_id(file_id, user_id, session)
                if not draft:
                    raise ValueError(f"Draft with file_id={file_id} not found for user {user_id}")

                existing_file = await self._file_repository.get_by_id(file_id, session)
                if not existing_file:
                    raise ValueError(f"File with id={file_id} not found")

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

                if existing_file.gost_id and data.DOCUMENTS_GOST:
                    gost_data = DocumentsGostUpdate(description=",".join(data.DOCUMENTS_GOST))
                    await self._documents_gost_repository.update(existing_file.gost_id, gost_data, session)

                if existing_file.test_results_id:
                    test_results_data = TestResultsUpdate(
                        results_ph=data.RESULTS_PH,
                        results_iron=data.RESULTS_IRON,
                        results_manganese=data.RESULTS_MANGANESE,
                        results_nitrates=data.RESULTS_NITRATES,
                        results_sulfates=data.RESULTS_SULFATES,
                    )
                    await self._test_results_repository.update(existing_file.test_results_id, test_results_data, session)

                file_data = FileUpdate(
                    full_object_name=data.FULL_OBJECT_NAME,
                    short_object_name=data.SHORT_OBJECT_NAME,
                    organization_name=data.ORGANIZATION_NAME,
                    region=data.REGION,
                    year=_parse_year(data.YEAR),
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
                    selected_indicators=",".join(data.SELECTED_TEST_INDICATORS) if data.SELECTED_TEST_INDICATORS else None,
                    organization_address=data.ORGANIZATION_ADDRESS,
                    organization_phone=data.ORGANIZATION_PHONE,
                    organization_email=data.ORGANIZATION_EMAIL,
                    responsible_name=data.RESPONSIBLE_NAME,
                    responsible_position=data.RESPONSIBLE_POSITION,
                    report_date=datetime.strptime(data.REPORT_DATE, "%Y-%m-%d").date() if data.REPORT_DATE else None,
                )
                await self._file_repository.update(file_id, file_data, session)

                await self._observation_point_repository.delete_by_file_id(file_id, session)
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

                await self._observation_dynamic_repository.delete_by_file_id(file_id, session)
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

                if promote:
                    await self._postgres_repository.mark_as_final(file_id, user_id, session)

                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
