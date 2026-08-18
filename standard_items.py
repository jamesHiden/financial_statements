"""Map our detailed canonical line items onto a global-standard statement
template - the fixed set of line items sites like stockanalysis.com or
macrotrends present (Revenue, Gross Profit, Operating Income, Net Income,
Total Assets, Cash from Operations, etc.), so every company lands on the
same comparable structure regardless of how Codal happened to format it.

Each canonical_key maps to exactly one standard_key, so summing by
standard_key never double-counts. Totals (total_assets, revenue, ...) are
taken as a direct pass-through from Codal's own reported subtotal rather
than re-summed from components, since that's more reliable than trying to
enumerate every possible line item that could feed into it.
"""

STANDARD_LABELS: dict[str, str] = {
    # --- Income statement ---
    "revenue": "Revenue",
    "cost_of_revenue": "Cost of Revenue",
    "gross_profit": "Gross Profit",
    "sga_expenses": "Selling, General & Administrative Expenses",
    "other_operating_expense": "Other Operating Expenses",
    "operating_expenses": "Operating Expenses",
    "operating_income": "Operating Income",
    "interest_expense": "Interest Expense",
    "other_income_expense": "Other Income (Expense)",
    "pretax_income": "Pretax Income",
    "income_tax_expense": "Income Tax Expense",
    "net_income": "Net Income",
    "eps_basic": "EPS (Basic)",
    "eps_diluted": "EPS (Diluted)",
    # --- Balance sheet ---
    "cash_and_equivalents": "Cash & Equivalents",
    "short_term_investments": "Short-Term Investments",
    "accounts_receivable": "Accounts Receivable",
    "inventory": "Inventory",
    "other_current_assets": "Other Current Assets",
    "total_current_assets": "Total Current Assets",
    "ppe_net": "Property, Plant & Equipment",
    "goodwill_and_intangibles": "Goodwill & Intangible Assets",
    "long_term_investments": "Long-Term Investments",
    "other_noncurrent_assets": "Other Non-Current Assets",
    "total_noncurrent_assets": "Total Non-Current Assets",
    "total_assets": "Total Assets",
    "accounts_payable": "Accounts Payable",
    "short_term_debt": "Short-Term Debt",
    "other_current_liabilities": "Other Current Liabilities",
    "total_current_liabilities": "Total Current Liabilities",
    "long_term_debt": "Long-Term Debt",
    "other_noncurrent_liabilities": "Other Non-Current Liabilities",
    "total_noncurrent_liabilities": "Total Non-Current Liabilities",
    "total_liabilities": "Total Liabilities",
    "common_stock": "Common Stock",
    "retained_earnings": "Retained Earnings",
    "other_equity": "Other Equity",
    "total_equity": "Total Equity",
    "total_liabilities_and_equity": "Total Liabilities & Equity",
    # --- Cash flow ---
    "other_operating_activities": "Other Operating Activities",
    "cash_from_operations": "Cash from Operations",
    "capital_expenditures": "Capital Expenditures",
    "other_investing_activities": "Other Investing Activities",
    "cash_from_investing": "Cash from Investing",
    "common_stock_issued": "Common Stock Issued",
    "debt_issued": "Debt Issued",
    "debt_repaid": "Debt Repaid",
    "dividends_paid": "Dividends Paid",
    "fx_effect": "Effect of Exchange Rate Changes",
    "other_financing_activities": "Other Financing Activities",
    "cash_from_financing": "Cash from Financing",
    "net_change_in_cash": "Net Change in Cash",
    "cash_beginning_balance": "Cash - Beginning of Period",
    "cash_ending_balance": "Cash - End of Period",
}

# canonical_key (from line_items.py) -> standard_key. Section headers and
# intermediate subtotals we don't want in the standard view are simply
# absent from these maps.
BALANCE_SHEET_STANDARD_MAP: dict[str, str] = {
    "no_trade_receivables": "accounts_receivable",
    "trade_and_other_receivables": "accounts_receivable",
    "other_receivable_accounts": "accounts_receivable",
    "inventory": "inventory",
    "cash_and_equivalents": "cash_and_equivalents",
    "shortterm_investments": "short_term_investments",
    "orders_and_prepayments": "other_current_assets",
    "assets_held_for_sale": "other_current_assets",
    "claims_from_banks": "other_current_assets",
    "claims_from_government": "other_current_assets",
    "total_current_assets": "total_current_assets",
    "tangible_fixed_assets": "ppe_net",
    "intangible_assets": "goodwill_and_intangibles",
    "longterm_investments": "long_term_investments",
    "investment_in_securities": "long_term_investments",
    "investment_in_properties": "other_noncurrent_assets",
    "longterm_receivables": "other_noncurrent_assets",
    "tax_moved_assets": "other_noncurrent_assets",
    "other_assets": "other_noncurrent_assets",
    "loans_and_claims_govt_entities": "other_noncurrent_assets",
    "loans_and_claims_nongovt_entities": "other_noncurrent_assets",
    "claims_from_subsidiaries": "other_noncurrent_assets",
    "total_noncurrent_assets": "total_noncurrent_assets",
    "total_assets": "total_assets",
    "no_trade_payables": "accounts_payable",
    "trade_and_other_payables": "accounts_payable",
    "shortterm_financial_facilities": "short_term_debt",
    "debt_to_banks": "short_term_debt",
    "tax_payable": "other_current_liabilities",
    "dividends_payable": "other_current_liabilities",
    "provisions": "other_current_liabilities",
    "advances_received": "other_current_liabilities",
    "noncurrent_advances_received": "other_current_liabilities",
    "liabilities_related_to_assets_held_for_sale": "other_current_liabilities",
    "customer_deposits": "other_current_liabilities",
    "income_tax_reserve": "other_current_liabilities",
    "total_current_liabilities": "total_current_liabilities",
    "longterm_financial_facilities": "long_term_debt",
    "debt_securities": "long_term_debt",
    "longterm_payables": "other_noncurrent_liabilities",
    "tax_moved_liabilities": "other_noncurrent_liabilities",
    "employee_benefits_provision": "other_noncurrent_liabilities",
    "reserves_and_other_liabilities": "other_noncurrent_liabilities",
    "employee_retirement_reserve": "other_noncurrent_liabilities",
    "total_noncurrent_liabilities": "total_noncurrent_liabilities",
    "total_liabilities": "total_liabilities",
    "capital": "common_stock",
    "retained_earnings": "retained_earnings",
    "capital_increase_in_progress": "other_equity",
    "share_premium": "other_equity",
    "treasury_share_premium": "other_equity",
    "legal_reserve": "other_equity",
    "other_reserves": "other_equity",
    "revaluation_surplus": "other_equity",
    "foreign_ops_exchange_diff": "other_equity",
    "treasury_shares": "other_equity",
    "revaluation_surplus_assets_held_for_sale": "other_equity",
    "forex_reserve_govt_entities": "other_equity",
    "deposit_holders_equity": "other_equity",
    "total_equity": "total_equity",
    "total_equity_and_liabilities": "total_liabilities_and_equity",
}

CASH_FLOW_STANDARD_MAP: dict[str, str] = {
    "income_tax_paid": "other_operating_activities",
    "cash_generated_from_operations": "other_operating_activities",
    "net_cash_operating": "cash_from_operations",
    "purchase_tangible_assets": "capital_expenditures",
    "purchase_intangible_assets": "capital_expenditures",
    "purchase_real_estate_investments": "capital_expenditures",
    "proceeds_sale_tangible_assets": "other_investing_activities",
    "proceeds_sale_held_for_sale_assets": "other_investing_activities",
    "proceeds_sale_intangible_assets": "other_investing_activities",
    "proceeds_sale_longterm_investments": "other_investing_activities",
    "purchase_longterm_investments": "other_investing_activities",
    "proceeds_sale_real_estate_investments": "other_investing_activities",
    "proceeds_sale_shortterm_investments": "other_investing_activities",
    "purchase_shortterm_investments": "other_investing_activities",
    "loans_granted_to_others": "other_investing_activities",
    "repayment_loans_granted": "other_investing_activities",
    "interest_income_loans_granted": "other_investing_activities",
    "dividend_income_received": "other_investing_activities",
    "other_investment_income_received": "other_investing_activities",
    "net_cash_investing": "cash_from_investing",
    "capital_contributions_received": "common_stock_issued",
    "proceeds_share_premium": "common_stock_issued",
    "proceeds_sale_treasury_shares": "other_financing_activities",
    "purchase_treasury_shares": "other_financing_activities",
    "proceeds_from_facilities": "debt_issued",
    "proceeds_participation_certificates": "debt_issued",
    "proceeds_sukuk": "debt_issued",
    "repayment_facilities_principal": "debt_repaid",
    "repayment_participation_certificates": "debt_repaid",
    "repayment_sukuk": "debt_repaid",
    "repayment_capital_lease": "debt_repaid",
    "interest_paid_facilities": "other_financing_activities",
    "interest_paid_participation_certificates": "other_financing_activities",
    "interest_paid_sukuk": "other_financing_activities",
    "interest_paid_capital_lease": "other_financing_activities",
    "investment_returns_and_financing_interest": "other_financing_activities",
    "dividends_paid": "dividends_paid",
    "net_cash_financing": "cash_from_financing",
    "fx_rate_effect": "fx_effect",
    "net_increase_in_cash": "net_change_in_cash",
    "cash_beginning_balance": "cash_beginning_balance",
    "cash_ending_balance": "cash_ending_balance",
    "other_financing_nci": "other_financing_activities",
}

INCOME_STATEMENT_STANDARD_MAP: dict[str, str] = {
    "total_operating_revenues": "revenue",
    "cost_of_goods_sold": "cost_of_revenue",
    "gross_profit": "gross_profit",
    "sga_expenses": "sga_expenses",
    "other_operating_expenses": "other_operating_expense",
    "total_operating_expenses": "operating_expenses",
    "operating_profit": "operating_income",
    "financial_expenses": "interest_expense",
    "dividend_income": "other_income_expense",
    "guaranteed_profit_income": "other_income_expense",
    "gain_loss_sale_investments": "other_income_expense",
    "gain_loss_fv_change_securities": "other_income_expense",
    "other_nonoperating_income_expenses": "other_income_expense",
    "discontinued_ops_profit_after_tax": "other_income_expense",
    "other_income": "other_income_expense",
    "other_expenses": "other_income_expense",
    "other_nonoperating_misc": "other_income_expense",
    "continuing_ops_profit_before_tax": "pretax_income",
    "income_tax": "income_tax_expense",
    "net_profit": "net_income",
    "basic_eps": "eps_basic",
    "diluted_eps": "eps_diluted",
    "share_of_associates_profit": "other_income_expense",
    "share_of_joint_ventures_profit": "other_income_expense",
    "payroll_expenses": "other_operating_expense",
    "rent_expense": "other_operating_expense",
    "depreciation_expense": "other_operating_expense",
    # Deliberately NOT mapped (would double-count against net_profit/total_equity
    # above, which are already the consolidated totals): minority_interest_net_income,
    # net_income_attributable_parent, minority_interest_retained_earnings,
    # retained_earnings_attributable_parent, profit_before_associates_share,
    # attributable_to_header, attributable_to_parent_label, attributable_to_nci_label.
}

MAPS_BY_STATEMENT_TYPE: dict[str, dict[str, str]] = {
    "balance_sheet": BALANCE_SHEET_STANDARD_MAP,
    "cash_flow": CASH_FLOW_STANDARD_MAP,
    "income_statement": INCOME_STATEMENT_STANDARD_MAP,
}


def standard_key_for(canonical_key: str | None, statement_type: str) -> str | None:
    if canonical_key is None:
        return None
    return MAPS_BY_STATEMENT_TYPE[statement_type].get(canonical_key)


def aggregate_standard_values(
    rows: list[tuple[str | None, float | None]], statement_type: str
) -> dict[str, float]:
    """rows: list of (canonical_key, value) from one parsed statement/period.

    Sums values per standard_key; a standard_key with no non-null
    contributions is omitted rather than reported as zero.
    """
    totals: dict[str, float] = {}
    for canonical_key, value in rows:
        if value is None:
            continue
        standard_key = standard_key_for(canonical_key, statement_type)
        if standard_key is None:
            continue
        totals[standard_key] = totals.get(standard_key, 0.0) + value
    return totals
