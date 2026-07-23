"""Offline routing tests for the NYC 311 oracle compiler.

These do not touch the database; they check that the deterministic compiler
routes each metric/grain to the intended canonical SQL shape.
"""

from __future__ import annotations

import pytest

from agent.metric_sql_nyc311 import generate_nyc311_metric_sql


def _sql(qid, question, metrics):
    return generate_nyc311_metric_sql({"id": qid, "question": question, "metrics": metrics})


def test_per_capita_joins_borough_population():
    sql = _sql("N011", "Which boroughs have the most requests per 1,000 residents?",
               ["requests_per_1k_residents"])
    assert "dim_borough" in sql and "population_2020" in sql


def test_resolution_rate_by_borough():
    sql = _sql("N007", "What is the resolution rate by borough?", ["resolution_rate"])
    assert "status = 'Closed'" in sql and "group by 1" in sql


def test_unresolved_share_by_borough_routes_to_borough_not_complaint():
    # Regression: N030 must not fall through to the complaint_type unresolved template.
    sql = _sql("N030", "What share of requests is unresolved by borough?", ["resolution_rate"])
    assert "borough" in sql and "unresolved_share" in sql
    assert "complaint_type" not in sql


def test_median_response_excludes_open_requests():
    sql = _sql("N006", "What is the median response time in hours by borough?",
               ["median_response_hours"])
    assert "response_hours is not null" in sql and "median(response_hours)" in sql


def test_agency_share_uses_window_denominator():
    sql = _sql("N013", "What share of all requests does each agency handle?", ["agency_share"])
    assert "over ()" in sql


def test_unknown_metric_raises():
    with pytest.raises(ValueError):
        _sql("Q", "something", ["not_a_metric"])
