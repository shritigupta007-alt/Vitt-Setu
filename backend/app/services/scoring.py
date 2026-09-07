from __future__ import annotations

from dataclasses import dataclass

from app.repository import load_data_file
from app.schemas import Contribution, FinancialFeatures, Guidance, IntendedUse, ScoreResponse


@dataclass(frozen=True)
class FeatureCalculation:
    key: str
    label: str
    points: float
    reason_code: str
    reason: str


def _score_band(score: float) -> tuple[str, str]:
    if score < 40:
        return "BUILDING", "Building readiness"
    if score < 60:
        return "EMERGING", "Emerging readiness"
    if score < 80:
        return "STEADY", "Steady readiness"
    return "STRONG", "Strong readiness"


def _confidence(features: FinancialFeatures) -> tuple[float, str]:
    observed_count = sum(
        value is not None
        for value in (
            features.inflow_regularity,
            features.income_volatility,
            features.bill_punctuality,
            features.supplier_payment_consistency,
            features.balance_buffer_days,
        )
    )
    months_component = min(features.data_coverage_months / 6, 1) * 0.6
    observed_component = observed_count / 5 * 0.4
    value = round(months_component + observed_component, 2)
    if value >= 0.8:
        return value, "More complete demo evidence"
    if value >= 0.5:
        return value, "Partial demo evidence"
    return value, "Limited demo evidence"


def _direction(points: float) -> str:
    if points > 0:
        return "positive"
    if points < 0:
        return "negative"
    return "neutral"


def _guidance(intended_use: IntendedUse, calculations: list[FeatureCalculation]) -> Guidance:
    guide = {
        IntendedUse.INVENTORY: (
            "WORKING_CAPITAL",
            "Small working-capital conversation",
            "Your stated need is inventory-related, so a small working-capital product category is the most relevant category to explore.",
        ),
        IntendedUse.EMERGENCY: (
            "EMERGENCY_CASH_FLOW",
            "Emergency cash-flow support conversation",
            "Your stated need is urgent, so start with support that makes total cost, repayment dates, and payment destination clear.",
        ),
        IntendedUse.SEASONAL_INPUT: (
            "SEASONAL_INPUT",
            "Seasonal-input finance conversation",
            "Your stated need is seasonal, so explore a category whose repayment timing is understandable alongside the seasonal cycle.",
        ),
    }[intended_use]

    lower_features = {calculation.key for calculation in calculations if calculation.points < 0}
    tips: list[str] = []
    if "bill_punctuality" in lower_features:
        tips.append(
            "Keep the selected recurring bills on time where possible and review due dates before they pass."
        )
    if "supplier_payment_consistency" in lower_features:
        tips.append(
            "Use a simple weekly supplier-payment plan to make business outflows more predictable."
        )
    if "balance_buffer_days" in lower_features:
        tips.append(
            "When possible, set aside a small buffer after essential expenses before seeking more credit."
        )
    if "income_volatility" in lower_features:
        tips.append(
            "Track income across several weeks so higher- and lower-income periods are easier to plan around."
        )
    if "inflow_regularity" in lower_features:
        tips.append(
            "Keep a simple record of regular business inflows to make income patterns easier to understand."
        )
    if len(tips) < 2:
        tips.extend(
            [
                "Review the Key Fact Statement, APR, repayment schedule, and payment destination before accepting credit.",
                "Use this result as a conversation starter, not as a promise of loan approval.",
            ]
        )

    return Guidance(
        category_code=guide[0],
        category=guide[1],
        rationale=guide[2],
        improvement_tips=tips[:2],
        disclaimer="This is non-binding prototype guidance. It does not determine eligibility, loan amount, interest rate, or approval.",
    )


def calculate_score(features: FinancialFeatures, intended_use: IntendedUse) -> ScoreResponse:
    model = load_data_file("model.json")
    baseline = float(model["baseline_score"])
    calculations: list[FeatureCalculation] = []

    definition_map = {item["key"]: item for item in model["features"]}
    input_values = {
        "inflow_regularity": features.inflow_regularity,
        "income_volatility": features.income_volatility,
        "bill_punctuality": features.bill_punctuality,
        "supplier_payment_consistency": features.supplier_payment_consistency,
        "balance_buffer_days": features.balance_buffer_days,
    }

    for key, value in input_values.items():
        if value is None:
            continue
        definition = definition_map[key]
        normalized_value = (
            min(value / definition["cap"], 1) if key == "balance_buffer_days" else value
        )
        contribution = round((normalized_value - 0.5) * definition["range_points"], 2)
        reason = (
            definition["positive_reason"] if contribution >= 0 else definition["negative_reason"]
        )
        calculations.append(
            FeatureCalculation(
                key=key,
                label=definition["label"],
                points=contribution,
                reason_code=definition["reason_code"],
                reason=reason,
            )
        )

    total_points = round(sum(item.points for item in calculations), 2)
    score = round(max(0, min(100, baseline + total_points)), 2)
    band, band_label = _score_band(score)
    confidence, confidence_label = _confidence(features)
    strongest = sorted(calculations, key=lambda item: abs(item.points), reverse=True)[:3]

    contributions = [
        Contribution(
            feature=item.key,
            label=item.label,
            points=item.points,
            direction=_direction(item.points),
            reason_code=item.reason_code,
            reason=item.reason,
        )
        for item in strongest
    ]

    return ScoreResponse(
        score=score,
        display_score=round(score),
        band=band,
        band_label=band_label,
        baseline_score=baseline,
        total_contribution_points=total_points,
        evidence_confidence=confidence,
        evidence_confidence_label=confidence_label,
        contributions=contributions,
        guidance=_guidance(intended_use, calculations),
        limitations=[
            "Synthetic demo data only; this result is not validated for real-world underwriting.",
            "Evidence confidence describes completeness of the demo inputs, not likelihood of repayment.",
            "The score does not replace a lender's policy, KYC, affordability review, or regulated decision process.",
        ],
        model_version=model["model_version"],
        feature_schema_version=model["feature_schema_version"],
    )
