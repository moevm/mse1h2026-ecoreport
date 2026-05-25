from reports.infrastructure.postgres.database import Database
from reports.infrastructure.postgres.repository import (
    ReportsRepository, FileRepository, DocumentsGostRepository,
    TestResultsRepository, ObservationPointRepository, ObservationDynamicRepository
)
from reports.schemas.report_models import DraftPayload


class GetDraftUseCase:
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

    async def execute(self, file_id: int, user_id: int) -> DraftPayload:
        async with self._database.session() as session:
            draft = await self._postgres_repository.get_draft_by_file_id(file_id, user_id, session)
            if not draft:
                raise ValueError(f"Draft with file_id={file_id} not found for user {user_id}")

            f = await self._file_repository.get_by_id(file_id, session)
            if not f:
                raise ValueError(f"File with id={file_id} not found")

            gost_description = None
            if f.gost_id:
                gost = await self._documents_gost_repository.get_by_id(f.gost_id, session)
                if gost and gost.description:
                    gost_description = gost.description

            test_results = None
            if f.test_results_id:
                test_results = await self._test_results_repository.get_by_id(f.test_results_id, session)

            points = await self._observation_point_repository.list_by_file_id(file_id, session)
            dynamics = await self._observation_dynamic_repository.list_by_file_id(file_id, session)

            def _year_str(d):
                return d.year if d else None

            def _float(v):
                return float(v) if v is not None else None

            def _float2(v):
                return f"{float(v):.2f}" if v is not None else None

            observation_points = [
                {
                    "observation_point": p.observation_point,
                    "latitude": _float(p.latitude),
                    "longitude": _float(p.longitude),
                    "medium_type": p.medium_type,
                    "description": p.description,
                }
                for p in points
            ]

            observation_dynamics = [
                {
                    "date": d.dynamic_data.strftime("%Y-%m-%d") if d.dynamic_data else "",
                    "pH": _float(d.dynamic_ph),
                    "iron": _float(d.dynamic_iron),
                    "manganese": _float(d.dynamic_manganese),
                    "nitrates": _float(d.dynamic_nitrates),
                    "sulfates": _float(d.dynamic_sulfates),
                }
                for d in dynamics
            ]

            selected_indicators = f.selected_indicators.split(",") if f.selected_indicators else None

            return DraftPayload(
                file_id=file_id,
                user_id=user_id,
                FULL_OBJECT_NAME=f.full_object_name,
                SHORT_OBJECT_NAME=f.short_object_name,
                YEAR=_year_str(f.year),
                ORGANIZATION_NAME=f.organization_name,
                REGION=f.region,
                DOCUMENTS_GOST=gost_description.split(",") if gost_description else [],
                RELIEF_TYPE=f.relief_type,
                SOIL_TYPE=f.soil_type,
                GROUNDWATER_LEVEL=_float2(f.groundwater_level),
                CLIMATE_ZONE=f.climate_zone,
                COORDINATES_LATITUDE=_float(f.coordinates_latitude),
                COORDINATES_LONGITUDE=_float(f.coordinates_longitude),
                OBJECT_TYPE=f.object_type,
                SYSTEM_TYPE=f.system_type,
                PIPE_MATERIAL=f.pipe_material,
                PIPE_DIAMETER=_float2(f.pipe_diameter),
                PIPE_DEPTH=_float2(f.pipe_depth),
                PIPE_LENGTH=_float2(f.pipe_length),
                PIPE_INSTALL_YEAR=_year_str(f.pipe_install_year),
                MANHOLE_COUNT=f.manhole_count,
                MONITORING_POINT_COUNT=f.monitoring_point_count,
                OBSERVATION_FREQUENCY=f.observation_frequency,
                OBSERVATION_POINTS=observation_points,
                RESULTS_PH=_float(test_results.results_ph) if test_results else None,
                RESULTS_IRON=_float(test_results.results_iron) if test_results else None,
                RESULTS_MANGANESE=_float(test_results.results_manganese) if test_results else None,
                RESULTS_NITRATES=_float(test_results.results_nitrates) if test_results else None,
                RESULTS_SULFATES=_float(test_results.results_sulfates) if test_results else None,
                OBSERVATION_DYNAMICS=observation_dynamics,
                SELECTED_TEST_INDICATORS=selected_indicators,
                ORGANIZATION_ADDRESS=f.organization_address,
                ORGANIZATION_PHONE=f.organization_phone,
                ORGANIZATION_EMAIL=f.organization_email,
                RESPONSIBLE_NAME=f.responsible_name,
                RESPONSIBLE_POSITION=f.responsible_position,
                REPORT_DATE=str(f.report_date) if f.report_date else None,
            )
