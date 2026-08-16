"""SQLAlchemy models and upsert helpers for the Postgres schema in db/schema.sql."""
from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import date, datetime
from typing import Iterator

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

from line_items import MAPS_BY_STATEMENT_TYPE
from parser import ParsedStatement
from standard_items import aggregate_standard_values

load_dotenv()

Base = declarative_base()
StatementTypeEnum = Enum(
    "balance_sheet", "income_statement", "cash_flow", name="statement_type", create_type=False
)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, unique=True)
    name_fa = Column(String)
    industry = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    filings = relationship("Filing", back_populates="company")


class Filing(Base):
    __tablename__ = "filings"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "statement_type", "period_end_date", "audited", "amended", "consolidated"
        ),
    )

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    statement_type = Column(StatementTypeEnum, nullable=False)
    period_end_date = Column(Date, nullable=False)
    fiscal_quarter = Column(String)
    audited = Column(Boolean, nullable=False, default=False)
    amended = Column(Boolean, nullable=False, default=False)
    consolidated = Column(Boolean, nullable=False, default=False)
    source_url = Column(String)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="filings")
    line_items = relationship(
        "StatementLineItem", back_populates="filing", cascade="all, delete-orphan"
    )


class StatementLineItem(Base):
    __tablename__ = "statement_line_items"
    __table_args__ = (UniqueConstraint("filing_id", "label_fa"),)

    id = Column(Integer, primary_key=True)
    filing_id = Column(Integer, ForeignKey("filings.id", ondelete="CASCADE"), nullable=False)
    canonical_key = Column(String)
    label_fa = Column(String, nullable=False)
    value = Column(Numeric)

    filing = relationship("Filing", back_populates="line_items")


class LineItemMapping(Base):
    __tablename__ = "line_item_mapping"

    label_fa = Column(String, primary_key=True)
    statement_type = Column(StatementTypeEnum, primary_key=True)
    canonical_key = Column(String, nullable=False)


class StandardLineItem(Base):
    __tablename__ = "standard_line_items"
    __table_args__ = (UniqueConstraint("filing_id", "standard_key"),)

    id = Column(Integer, primary_key=True)
    filing_id = Column(Integer, ForeignKey("filings.id", ondelete="CASCADE"), nullable=False)
    standard_key = Column(String, nullable=False)
    value = Column(Numeric, nullable=False)


_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        database_url = os.environ["DATABASE_URL"]
        _engine = create_engine(database_url)
        _SessionLocal = sessionmaker(bind=_engine)
    return _engine


@contextmanager
def get_session() -> Iterator[Session]:
    _get_engine()
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def upsert_company(session: Session, symbol: str, name_fa: str | None = None) -> Company:
    stmt = (
        pg_insert(Company)
        .values(symbol=symbol, name_fa=name_fa)
        .on_conflict_do_update(index_elements=["symbol"], set_={"name_fa": name_fa})
        .returning(Company.id)
    )
    company_id = session.execute(stmt).scalar_one()
    return session.get(Company, company_id)


def upsert_filing(
    session: Session,
    company_id: int,
    statement_type: str,
    period_end_date: date,
    audited: bool,
    amended: bool,
    consolidated: bool,
    source_url: str,
    fiscal_quarter: str | None = None,
) -> Filing:
    stmt = (
        pg_insert(Filing)
        .values(
            company_id=company_id,
            statement_type=statement_type,
            period_end_date=period_end_date,
            fiscal_quarter=fiscal_quarter,
            audited=audited,
            amended=amended,
            consolidated=consolidated,
            source_url=source_url,
            fetched_at=datetime.utcnow(),
        )
        .on_conflict_do_update(
            index_elements=[
                "company_id", "statement_type", "period_end_date", "audited", "amended", "consolidated",
            ],
            set_={"source_url": source_url, "fetched_at": datetime.utcnow()},
        )
        .returning(Filing.id)
    )
    filing_id = session.execute(stmt).scalar_one()
    return session.get(Filing, filing_id)


def upsert_line_items(
    session: Session, filing_id: int, rows: list[tuple[str, str | None, float | None]]
) -> None:
    """rows: list of (label_fa, canonical_key, value)."""
    if not rows:
        return
    # Some Codal tables repeat the same label (merged section headers, messy
    # HTML); keep the last occurrence so one batch insert never targets the
    # same (filing_id, label_fa) row twice - Postgres rejects that outright.
    deduped = {label_fa: (canonical_key, value) for label_fa, canonical_key, value in rows}
    stmt = pg_insert(StatementLineItem).values(
        [
            {"filing_id": filing_id, "label_fa": label_fa, "canonical_key": canonical_key, "value": value}
            for label_fa, (canonical_key, value) in deduped.items()
        ]
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["filing_id", "label_fa"],
        set_={"canonical_key": stmt.excluded.canonical_key, "value": stmt.excluded.value},
    )
    session.execute(stmt)


def upsert_standard_line_items(session: Session, filing_id: int, totals: dict[str, float]) -> None:
    """totals: standard_key -> summed value, from standard_items.aggregate_standard_values."""
    if not totals:
        return
    stmt = pg_insert(StandardLineItem).values(
        [
            {"filing_id": filing_id, "standard_key": standard_key, "value": value}
            for standard_key, value in totals.items()
        ]
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["filing_id", "standard_key"],
        set_={"value": stmt.excluded.value},
    )
    session.execute(stmt)


def seed_line_item_mappings(session: Session) -> None:
    """Sync the Python-side label->canonical_key maps into the DB table."""
    rows = [
        {"label_fa": label_fa, "statement_type": statement_type, "canonical_key": canonical_key}
        for statement_type, mapping in MAPS_BY_STATEMENT_TYPE.items()
        for label_fa, canonical_key in mapping.items()
    ]
    stmt = pg_insert(LineItemMapping).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["label_fa", "statement_type"],
        set_={"canonical_key": stmt.excluded.canonical_key},
    )
    session.execute(stmt)


def store_parsed_statement(
    session: Session,
    company_id: int,
    statement: ParsedStatement,
    audited: bool,
    amended: bool,
    consolidated: bool,
    source_url: str,
) -> None:
    """Persist one parsed statement: one Filing row per period column, each
    with its own set of line items."""
    for period_iso in statement.periods:
        period_end_date = date.fromisoformat(period_iso)
        filing = upsert_filing(
            session,
            company_id=company_id,
            statement_type=statement.statement_type,
            period_end_date=period_end_date,
            audited=audited,
            amended=amended,
            consolidated=consolidated,
            source_url=source_url,
        )
        rows = [
            (row.label_fa, row.canonical_key, row.values_by_period.get(period_iso))
            for row in statement.rows
        ]
        upsert_line_items(session, filing.id, rows)

        standard_totals = aggregate_standard_values(
            [(canonical_key, value) for _, canonical_key, value in rows],
            statement.statement_type,
        )
        upsert_standard_line_items(session, filing.id, standard_totals)
