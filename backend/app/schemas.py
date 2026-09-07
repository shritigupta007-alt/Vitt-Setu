from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class IntendedUse(str, Enum):
    INVENTORY = "inventory"
    EMERGENCY = "emergency"
    SEASONAL_INPUT = "seasonal_input"


class FinancialFeatures(BaseModel):
    """Derived, consented features only. Values may be missing; they are never zero-filled."""

    model_config = ConfigDict(extra="forbid")

    inflow_regularity: float | None = Field(default=None, ge=0, le=1)
    income_volatility: float | None = Field(default=None, ge=0, le=1)
    bill_punctuality: float | None = Field(default=None, ge=0, le=1)
    supplier_payment_consistency: float | None = Field(default=None, ge=0, le=1)
    balance_buffer_days: float | None = Field(default=None, ge=0, le=365)
    data_coverage_months: int = Field(ge=0, le=24)

    @model_validator(mode="after")
    def require_observed_feature(self) -> "FinancialFeatures":
        observed = (
            self.inflow_regularity,
            self.income_volatility,
            self.bill_punctuality,
            self.supplier_payment_consistency,
            self.balance_buffer_days,
        )
        if all(value is None for value in observed):
            raise ValueError("At least one derived financial feature is required.")
        return self


class ScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    consent_acknowledged: bool
    intended_use: IntendedUse
    features: FinancialFeatures


class Contribution(BaseModel):
    feature: str
    label: str
    points: float
    direction: str
    reason_code: str
    reason: str


class Guidance(BaseModel):
    category_code: str
    category: str
    rationale: str
    improvement_tips: list[str]
    disclaimer: str


class ScoreResponse(BaseModel):
    score: float = Field(ge=0, le=100)
    display_score: int = Field(ge=0, le=100)
    band: str
    band_label: str
    baseline_score: float
    total_contribution_points: float
    evidence_confidence: float = Field(ge=0, le=1)
    evidence_confidence_label: str
    contributions: list[Contribution]
    guidance: Guidance
    limitations: list[str]
    model_version: str
    feature_schema_version: str
    demo_data_only: bool = True


class Persona(BaseModel):
    id: str
    name: str
    age: int = Field(ge=18, le=120)
    occupation: str
    scenario: str
    intended_use: IntendedUse
    derived_features: FinancialFeatures


class RegistryAssociation(BaseModel):
    app_name: str
    app_package: str | None = None
    domain: str | None = None
    regulated_entity_name: str
    association_evidence: str


class RegistryProvenance(BaseModel):
    snapshot_id: str
    as_of_date: str
    source: str
    limitation: str
    synthetic_demo_data: bool = True


class LenderSearchResponse(BaseModel):
    query: str
    normalized_query: str
    status: str
    user_message: str
    required_next_action: str
    exact_match: RegistryAssociation | None = None
    suggestions: list[RegistryAssociation] = Field(default_factory=list)
    provenance: RegistryProvenance


class ModelCardResponse(BaseModel):
    model_version: str
    feature_schema_version: str
    scoring_approach: str
    baseline_score: float
    features: list[dict[str, object]]
    exclusions: list[str]
    limitations: list[str]
    test_summary: list[str]
    registry_provenance: RegistryProvenance
