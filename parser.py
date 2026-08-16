"""Parse a Codal filing document into tidy (label, period, value) rows.

Codal's "Excel" export is actually an HTML document with one or more
<table>s. A single filing can contain more than one statement (balance
sheet, income statement, cash flow all in one document), so - like the
original main.py - we read every table and classify each one by keyword.

Known limitation: a minority of older filings render the balance sheet as
two side-by-side blocks (assets | equity & liabilities) inside one table
instead of stacked rows. That layout isn't handled here yet; if manual
validation in Phase 2 turns up companies with suspiciously short balance
sheets, that's the likely cause and this is the place to add it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from io import StringIO

import pandas as pd

import jalali
from line_items import canonical_key_for
from numeric import parse_number

_DATE_RE = re.compile(r"\d{4}/\d{2}/\d{2}")

_STATEMENT_MARKERS: dict[str, tuple[str, ...]] = {
    "balance_sheet": ("جمع دارایی‌های جاری", "جمع دارايي‌هاي جاري", "جمع دارایی‌ها", "جمع دارايي‌ها"),
    "cash_flow": ("نقد حاصل از عملیات", "نقد حاصل از عمليات", "جریان­‌های نقدی حاصل از فعالیت‌های تامین مالی", "فعالیت‌های عملیاتی"),
    "income_statement": ("سود (زیان) پایه هر سهم", "سود (زيان) پايه هر سهم", "درآمد سود سهام"),
}


@dataclass
class ParsedRow:
    label_fa: str
    canonical_key: str | None
    values_by_period: dict[str, float | None]  # period_end_date (ISO) -> value


@dataclass
class ParsedStatement:
    statement_type: str
    periods: list[str] = field(default_factory=list)  # ISO dates found as columns
    rows: list[ParsedRow] = field(default_factory=list)


def _classify(df: pd.DataFrame) -> str | None:
    flat_values = df.astype(str).values.ravel()
    for statement_type, markers in _STATEMENT_MARKERS.items():
        if any(marker in flat_values for marker in markers):
            return statement_type
    return None


def _normalize_header(df: pd.DataFrame) -> pd.DataFrame:
    """Promote row 0 to the header when read_html failed to detect it."""
    header_has_dates = any(_DATE_RE.search(str(c)) for c in df.columns)
    if header_has_dates:
        return df
    df = df.copy()
    df.columns = df.iloc[0]
    return df.iloc[1:].reset_index(drop=True)


def _period_columns(df: pd.DataFrame) -> dict[object, str]:
    """Map each dataframe column to an ISO period-end date, for date columns."""
    mapping = {}
    for col in df.columns:
        match = _DATE_RE.search(str(col))
        if match:
            mapping[col] = jalali.Persian(match.group()).gregorian_datetime().isoformat()
    return mapping


def _parse_table(df: pd.DataFrame, statement_type: str) -> ParsedStatement | None:
    df = _normalize_header(df)
    period_cols = _period_columns(df)
    if not period_cols:
        return None

    label_col = df.columns[0]
    statement = ParsedStatement(statement_type=statement_type, periods=list(period_cols.values()))

    for _, row in df.iterrows():
        label_fa = str(row[label_col]).strip()
        if not label_fa or label_fa.lower() == "nan":
            continue
        values_by_period = {
            period_iso: parse_number(row[col]) for col, period_iso in period_cols.items()
        }
        statement.rows.append(
            ParsedRow(
                label_fa=label_fa,
                canonical_key=canonical_key_for(label_fa, statement_type),
                values_by_period=values_by_period,
            )
        )

    return statement


def _decode_html(content: bytes) -> str:
    """Codal's newer filings are UTF-8; filings from before ~2018 are usually
    windows-1256 (the legacy Persian/Arabic encoding old Office HTML exports
    used). Try both before giving up and replacing bad bytes."""
    for encoding in ("utf-8", "windows-1256", "windows-1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def parse_filing(content: bytes) -> list[ParsedStatement]:
    """Parse every recognizable statement table out of a filing document."""
    tables = pd.read_html(StringIO(_decode_html(content)))
    statements: list[ParsedStatement] = []
    for raw_df in tables:
        statement_type = _classify(raw_df)
        if statement_type is None:
            continue
        parsed = _parse_table(raw_df, statement_type)
        if parsed is not None and parsed.rows:
            statements.append(parsed)
    return statements
