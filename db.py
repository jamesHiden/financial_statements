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

import fx_rates
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
    tsetmc_ins_code = Column(String)
    name_en = Column(String)
    mnemonic_en = Column(String)
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


class UsdIrrRate(Base):
    __tablename__ = "usd_irr_rates"

    day = Column(Date, primary_key=True)
    close_rial = Column(Numeric, nullable=False)


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True)
    last_price = Column(Numeric)
    closing_price = Column(Numeric)
    price_change_pct = Column(Numeric)
    day_low = Column(Numeric)
    day_high = Column(Numeric)
    volume = Column(Numeric)
    trade_value = Column(Numeric)
    trade_count = Column(Numeric)
    market_cap = Column(Numeric)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketIndex(Base):
    __tablename__ = "market_indices"

    index_key = Column(String, primary_key=True)
    value = Column(Numeric, nullable=False)
    change_pct = Column(Numeric)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())


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


def set_tsetmc_ins_code(session: Session, company_id: int, ins_code: str) -> None:
    session.execute(
        Company.__table__.update().where(Company.id == company_id).values(tsetmc_ins_code=ins_code)
    )


def set_industry(session: Session, company_id: int, industry: str) -> None:
    session.execute(
        Company.__table__.update().where(Company.id == company_id).values(industry=industry)
    )


def set_english_identity(
    session: Session, company_id: int, name_en: str | None, mnemonic_en: str | None
) -> None:
    session.execute(
        Company.__table__.update()
        .where(Company.id == company_id)
        .values(name_en=name_en, mnemonic_en=mnemonic_en)
    )


def upsert_market_snapshot(
    session: Session,
    company_id: int,
    last_price: float | None,
    closing_price: float | None,
    price_change_pct: float | None,
    day_low: float | None,
    day_high: float | None,
    volume: float | None,
    trade_value: float | None,
    trade_count: float | None,
    market_cap: float | None,
) -> None:
    stmt = pg_insert(MarketSnapshot).values(
        company_id=company_id,
        last_price=last_price,
        closing_price=closing_price,
        price_change_pct=price_change_pct,
        day_low=day_low,
        day_high=day_high,
        volume=volume,
        trade_value=trade_value,
        trade_count=trade_count,
        market_cap=market_cap,
        fetched_at=datetime.utcnow(),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["company_id"],
        set_={
            "last_price": stmt.excluded.last_price,
            "closing_price": stmt.excluded.closing_price,
            "price_change_pct": stmt.excluded.price_change_pct,
            "day_low": stmt.excluded.day_low,
            "day_high": stmt.excluded.day_high,
            "volume": stmt.excluded.volume,
            "trade_value": stmt.excluded.trade_value,
            "trade_count": stmt.excluded.trade_count,
            "market_cap": stmt.excluded.market_cap,
            "fetched_at": stmt.excluded.fetched_at,
        },
    )
    session.execute(stmt)


def upsert_market_index(
    session: Session, index_key: str, value: float, change_pct: float | None
) -> None:
    stmt = pg_insert(MarketIndex).values(
        index_key=index_key, value=value, change_pct=change_pct, fetched_at=datetime.utcnow()
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["index_key"],
        set_={"value": stmt.excluded.value, "change_pct": stmt.excluded.change_pct, "fetched_at": stmt.excluded.fetched_at},
    )
    session.execute(stmt)


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


def upsert_fx_rates(session: Session, rates: list[fx_rates.DailyRate]) -> None:
    """Bulk upsert the USD/IRR daily history. Cheap enough to just replace
    the whole thing on every run rather than tracking incremental updates."""
    if not rates:
        return
    stmt = pg_insert(UsdIrrRate).values(
        [{"day": r.day, "close_rial": r.close_rial} for r in rates]
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["day"],
        set_={"close_rial": stmt.excluded.close_rial},
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
