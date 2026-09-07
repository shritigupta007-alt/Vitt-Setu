from __future__ import annotations

from app.schemas import FinancialFeatures, IntendedUse
from app.services.scoring import calculate_score


def _features(**overrides: float | int | None) -> FinancialFeatures:
    defaults: dict[str, float | int | None] = {
        "inflow_regularity": 0.7,
        "income_volatility": 0.3,
        "bill_punctuality": 0.8,
        "supplier_payment_consistency": 0.7,
        "balance_buffer_days": 12,
        "data_coverage_months": 6,
    }
    defaults.update(overrides)
    return FinancialFeatures(**defaults)


def test_score_is_deterministic_and_reconciles() -> None:
    response = calculate_score(_features(), IntendedUse.INVENTORY)

    assert response == calculate_score(_features(), IntendedUse.INVENTORY)
    assert 0 <= response.score <= 100
    assert response.score == round(response.baseline_score + response.total_contribution_points, 2)
    assert len(response.contributions) == 3
    assert response.guidance.category_code == "WORKING_CAPITAL"


def test_more_bill_punctuality_does_not_lower_score() -> None:
    lower = calculate_score(_features(bill_punctuality=0.2), IntendedUse.INVENTORY)
    higher = calculate_score(_features(bill_punctuality=0.9), IntendedUse.INVENTORY)

    assert higher.score >= lower.score


def test_missing_data_reduces_confidence_without_zero_filling() -> None:
    complete = calculate_score(_features(), IntendedUse.EMERGENCY)
    partial = calculate_score(
        _features(
            supplier_payment_consistency=None, balance_buffer_days=None, data_coverage_months=3
        ),
        IntendedUse.EMERGENCY,
    )

    assert partial.evidence_confidence < complete.evidence_confidence
    assert {contribution.feature for contribution in partial.contributions}.isdisjoint(
        {"supplier_payment_consistency", "balance_buffer_days"}
    )
