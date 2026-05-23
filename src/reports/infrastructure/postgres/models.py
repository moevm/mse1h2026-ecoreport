from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, DateTime, func, Date, Integer, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from reports.infrastructure.postgres.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("file.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), server_default=func.timezone("UTC", func.current_timestamp()))

    user: Mapped["User"] = relationship()
    file: Mapped["File"] = relationship()


class File(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_object_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    short_object_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    organization_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    year: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gost_id: Mapped[Optional[int]] = mapped_column(ForeignKey("documents_gost.id"), nullable=True)
    relief_type: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    soil_type: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    groundwater_level: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    climate_zone: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    coordinates_latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    coordinates_longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    object_type: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    system_type: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pipe_material: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    pipe_diameter: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    pipe_depth: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    pipe_length: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    pipe_install_year: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    manhole_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    monitoring_point_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    observation_frequency: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    test_results_id: Mapped[Optional[int]] = mapped_column(ForeignKey("test_results.id"), nullable=True)
    organization_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    organization_phone: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    organization_email: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    responsible_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    responsible_position: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    report_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    documents_gost: Mapped[Optional["DocumentsGost"]] = relationship()
    test_results: Mapped[Optional["TestResults"]] = relationship()


class DocumentsGost(Base):
    __tablename__ = "documents_gost"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gost_r_72274_2025: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_1811_2019: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_4_225_83: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_32_13330_2018: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    snip_32_03_96: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_r_71831_2024: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_r_54560_2015: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_286_82: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_100_13330_2016: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    snip_2_06_15_85: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_r_71856_2024: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_33068_2014: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sanpin_2_1_3684_21: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_104_13330_2016: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    snip_2_04_03_85: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_r_70628_1_2023: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_31416_2009: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_31_13330_2021: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_250_1325800_2016: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    snip_2_05_02_85: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_r_70628_2_2023: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_6942_98: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_34_13330_2021: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_116_13330_2012: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    snip_2_06_03_85: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_r_70628_5_2023: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    gost_17_1_3_13_86: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_121_13330_2019: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sp_50_101_2004: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class ObservationPoint(Base):
    __tablename__ = "observation_point"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("file.id"), nullable=True)
    observation_point: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    medium_type: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    file: Mapped[Optional["File"]] = relationship()


class TestResults(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    results_ph: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    results_iron: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    results_manganese: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    results_nitrates: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    results_sulfates: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)


class ObservationDynamic(Base):
    __tablename__ = "observation_dynamic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("file.id"), nullable=True)
    dynamic_ph: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    dynamic_iron: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    dynamic_manganese: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    dynamic_nitrates: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    dynamic_sulfates: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 4), nullable=True)
    dynamic_data: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    file: Mapped[Optional["File"]] = relationship()


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False),
                                                 server_default=func.timezone("UTC", func.current_timestamp()))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False),
                                                 server_default=func.timezone("UTC", func.current_timestamp()),
                                                 onupdate=func.timezone("UTC", func.current_timestamp()))
