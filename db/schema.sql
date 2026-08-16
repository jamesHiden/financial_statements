-- Codal financial statements schema.
-- Run this once against the Postgres database (e.g. via the Supabase SQL editor).

CREATE TYPE statement_type AS ENUM ('balance_sheet', 'income_statement', 'cash_flow');

CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    symbol TEXT NOT NULL UNIQUE,           -- Persian ticker, e.g. 'فولاد'
    name_fa TEXT,
    industry TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One row per filing "version": a given period can have both an unaudited
-- and an audited row (and amended variants of each). We keep all of them
-- and let readers prefer audited/amended at query time, rather than trying
-- to collapse them during ingestion.
CREATE TABLE filings (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    statement_type statement_type NOT NULL,
    period_end_date DATE NOT NULL,
    fiscal_quarter TEXT,                   -- 'Q1'..'Q4'
    audited BOOLEAN NOT NULL DEFAULT false,
    amended BOOLEAN NOT NULL DEFAULT false,
    consolidated BOOLEAN NOT NULL DEFAULT false,
    source_url TEXT,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (company_id, statement_type, period_end_date, audited, amended, consolidated)
);

CREATE TABLE statement_line_items (
    id SERIAL PRIMARY KEY,
    filing_id INTEGER NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    canonical_key TEXT,                    -- e.g. 'total_assets'; NULL if unmapped
    label_fa TEXT NOT NULL,
    value NUMERIC,
    UNIQUE (filing_id, label_fa)
);

-- Global-standard view of each filing: the same fixed set of line items
-- (Revenue, Net Income, Total Assets, Cash from Operations, ...) for every
-- company, computed from statement_line_items via standard_items.py's
-- canonical_key -> standard_key mapping. This is what the site's compare /
-- visualization views should read from.
CREATE TABLE standard_line_items (
    id SERIAL PRIMARY KEY,
    filing_id INTEGER NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    standard_key TEXT NOT NULL,
    value NUMERIC NOT NULL,
    UNIQUE (filing_id, standard_key)
);

CREATE INDEX idx_standard_items_filing ON standard_line_items(filing_id);
CREATE INDEX idx_standard_items_key ON standard_line_items(standard_key);

-- Structured, editable replacement for the old giant if/elif translation chain.
-- Seeded from line_items.py at ingest time; can also be hand-edited later for
-- labels the automatic pass doesn't recognize.
CREATE TABLE line_item_mapping (
    label_fa TEXT NOT NULL,
    statement_type statement_type NOT NULL,
    canonical_key TEXT NOT NULL,
    PRIMARY KEY (label_fa, statement_type)
);

CREATE INDEX idx_filings_company ON filings(company_id);
CREATE INDEX idx_line_items_filing ON statement_line_items(filing_id);
CREATE INDEX idx_line_items_canonical ON statement_line_items(canonical_key);
