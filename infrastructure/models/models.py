from typing import Optional

from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config.const import COORDS_SYSTEM_2D


class Base(DeclarativeBase):
    pass


company_activity = Table(
    "company_activity",
    Base.metadata,
    Column("company_id", ForeignKey("company.id"), primary_key=True),
    Column("activity_id", ForeignKey("activity.id"), primary_key=True),
)


class PhoneOrm(Base):
    __tablename__ = "phone"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
    number: Mapped[str]

    company: Mapped["CompanyOrm"] = relationship(back_populates="phones")


class CompanyOrm(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    legal_form: Mapped[str]
    building_id: Mapped[int] = mapped_column(ForeignKey("building.id"))

    building: Mapped["BuildingOrm"] = relationship(back_populates="companies")
    phones: Mapped[list[PhoneOrm]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
        order_by=PhoneOrm.id,
    )
    activities: Mapped[list["ActivityOrm"]] = relationship(
        secondary=company_activity,
        back_populates="companies",
    )


class ActivityOrm(Base):
    __tablename__ = "activity"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("activity.id"), nullable=True)

    parent: Mapped[Optional["ActivityOrm"]] = relationship(remote_side=[id], backref="children")
    companies: Mapped[list["CompanyOrm"]] = relationship(secondary=company_activity, back_populates="activities")


class BuildingOrm(Base):
    __tablename__ = "building"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str]
    coordinates: Mapped[Optional[str]] = mapped_column(Geography(geometry_type="POINT", srid=COORDS_SYSTEM_2D))
    companies: Mapped[list[CompanyOrm]] = relationship(back_populates="building")
