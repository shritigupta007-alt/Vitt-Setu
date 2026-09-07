from __future__ import annotations

from app.services.lenders import normalize_identifier, search_lenders


def test_normalization_ignores_case_and_punctuation() -> None:
    assert normalize_identifier("Udyam-Sathi Demo!") == "udyamsathidemo"


def test_exact_registry_match() -> None:
    response = search_lenders("Udyam Sathi Demo")

    assert response.status == "LISTED_ASSOCIATION"
    assert response.exact_match is not None
    assert response.exact_match.regulated_entity_name == "Sampoorna Finance Demo Ltd."


def test_near_name_is_only_a_possible_match() -> None:
    response = search_lenders("Udyam Sati")

    assert response.status == "POSSIBLE_MATCH"
    assert response.exact_match is None
    assert response.suggestions


def test_unknown_name_is_not_found_and_not_fraud() -> None:
    response = search_lenders("Completely Unknown App")

    assert response.status == "NOT_FOUND"
    assert "not a fraud verdict" in response.user_message
