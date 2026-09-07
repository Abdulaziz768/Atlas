from typing import Any

from atlas.transformation.models import FinancialStatementRecord
from atlas.transformation.utils import to_date, to_int


class FinancialStatementTransformer:
    """Transform raw financial statement data into FinancialStatementRecord objects."""

    def transform(self, data: dict[str, Any]) -> list[FinancialStatementRecord]:
        income_statement = data["income_statement"]
        balance_sheet = data["balance_sheet"]
        cash_flow = data["cash_flow"]

        records = []

        for report_type in ("annual", "quarterly"):
            income_reports = income_statement[f"{report_type}Reports"]
            balance_reports = balance_sheet[f"{report_type}Reports"]
            cash_flow_reports = cash_flow[f"{report_type}Reports"]

            balance_by_date = {
                report["fiscalDateEnding"]: report
                for report in balance_reports
            }

            cash_flow_by_date = {
                report["fiscalDateEnding"]: report
                for report in cash_flow_reports
            }

            for income_report in income_reports:
                fiscal_date = income_report["fiscalDateEnding"]

                balance_report = balance_by_date.get(fiscal_date)
                cash_flow_report = cash_flow_by_date.get(fiscal_date)

                if balance_report is None or cash_flow_report is None:
                    continue

                records.append(
                    FinancialStatementRecord(
                        ticker=income_statement["symbol"],
                        fiscal_date=to_date(fiscal_date),
                        report_type=report_type,
                        currency=income_report["reportedCurrency"],
                        revenue=to_int(income_report.get("totalRevenue")),
                        gross_profit=to_int(income_report.get("grossProfit")),
                        operating_income=to_int(
                            income_report.get("operatingIncome")
                        ),
                        net_income=to_int(income_report.get("netIncome")),
                        ebitda=to_int(income_report.get("ebitda")),
                        total_assets=to_int(
                            balance_report.get("totalAssets")
                        ),
                        total_liabilities=to_int(
                            balance_report.get("totalLiabilities")
                        ),
                        total_equity=to_int(
                            balance_report.get("totalShareholderEquity")
                        ),
                        cash=to_int(
                            balance_report.get(
                                "cashAndCashEquivalentsAtCarryingValue"
                            )
                        ),
                        inventory=to_int(
                            balance_report.get("inventory")
                        ),
                        total_debt=to_int(
                            balance_report.get("shortLongTermDebtTotal")
                        ),
                        operating_cash_flow=to_int(
                            cash_flow_report.get("operatingCashflow")
                        ),
                        capital_expenditure=to_int(
                            cash_flow_report.get("capitalExpenditures")
                        ),
                        investing_cash_flow=to_int(
                            cash_flow_report.get("cashflowFromInvestment")
                        ),
                        financing_cash_flow=to_int(
                            cash_flow_report.get("cashflowFromFinancing")
                        ),
                        free_cash_flow=self._calculate_free_cash_flow(
                            cash_flow_report
                        ),
                    )
                )

        return records

    @staticmethod
    def _calculate_free_cash_flow(
        cash_flow_report: dict[str, Any],
    ) -> int | None:
        operating_cash_flow = to_int(
            cash_flow_report.get("operatingCashflow")
        )
        capital_expenditure = to_int(
            cash_flow_report.get("capitalExpenditures")
        )

        if operating_cash_flow is None or capital_expenditure is None:
            return None

        return operating_cash_flow - capital_expenditure