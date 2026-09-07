from __future__ import annotations

import re
from difflib import SequenceMatcher

from app.repository import load_data_file
from app.schemas import LenderSearchResponse, RegistryAssociation, RegistryProvenance


def normalize_identifier(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _association(record: dict[str, str]) -> RegistryAssociation:
    return RegistryAssociation(
        app_name=record["app_name"],
        app_package=record.get("app_package"),
        domain=record.get("domain"),
        regulated_entity_name=record["regulated_entity_name"],
        association_evidence=record["association_evidence"],
    )


def search_lenders(query: str) -> LenderSearchResponse:
    registry = load_data_file("registry.json")
    normalized_query = normalize_identifier(query)
    provenance = RegistryProvenance(**registry["provenance"])
    records = registry["associations"]

    for record in records:
        identifiers = (record["app_name"], record.get("app_package", ""), record.get("domain", ""))
        if normalized_query in {
            normalize_identifier(identifier) for identifier in identifiers if identifier
        }:
            return LenderSearchResponse(
                query=query,
                normalized_query=normalized_query,
                status="LISTED_ASSOCIATION",
                user_message="A matching association appears in this illustrative, dated prototype snapshot.",
                required_next_action="Confirm the regulated entity's official website, publisher, Key Fact Statement, APR, and payment destination before taking any action.",
                exact_match=_association(record),
                provenance=provenance,
            )

    ranked = sorted(
        (
            (
                max(
                    SequenceMatcher(
                        None, normalized_query, normalize_identifier(record["app_name"])
                    ).ratio(),
                    SequenceMatcher(
                        None,
                        normalized_query,
                        normalize_identifier(record["regulated_entity_name"]),
                    ).ratio(),
                ),
                record,
            )
            for record in records
        ),
        key=lambda item: item[0],
        reverse=True,
    )
    suggestions = [_association(record) for score, record in ranked[:3] if score >= 0.58]
    if suggestions:
        return LenderSearchResponse(
            query=query,
            normalized_query=normalized_query,
            status="POSSIBLE_MATCH",
            user_message="Similar names were found, but the identifiers do not exactly match. This is not a verification result.",
            required_next_action="Open the evidence, choose the exact entity, and independently verify the official regulated-entity source before sharing information or making a payment.",
            suggestions=suggestions,
            provenance=provenance,
        )

    return LenderSearchResponse(
        query=query,
        normalized_query=normalized_query,
        status="NOT_FOUND",
        user_message="No exact association was found in this illustrative prototype snapshot. This is not a fraud verdict.",
        required_next_action="Do not pay or share documents yet. Verify the entity through official sources and seek support if conduct concerns remain.",
        provenance=provenance,
    )
