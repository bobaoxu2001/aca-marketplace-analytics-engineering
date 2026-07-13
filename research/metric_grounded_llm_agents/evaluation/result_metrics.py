"""Gold-result and answer-faithfulness metrics for analytics-agent outputs."""

from __future__ import annotations

import math
import re
from numbers import Number
from typing import Any


NUMBER_PATTERN = re.compile(r"(?<![A-Za-z0-9_])[-+]?\$?\d[\d,]*(?:\.\d+)?%?")


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, Number):
        value = float(value)
        return value if math.isfinite(value) else None
    if isinstance(value, str):
        cleaned = value.strip().replace("$", "").replace(",", "")
        percent = cleaned.endswith("%")
        if percent:
            cleaned = cleaned[:-1]
        try:
            result = float(cleaned)
            return result / 100 if percent else result
        except ValueError:
            return None
    return None


def _equal(left: Any, right: Any, *, rel_tol: float = 1e-6, abs_tol: float = 1e-6) -> bool:
    left_number, right_number = _number(left), _number(right)
    if left_number is not None and right_number is not None:
        return math.isclose(left_number, right_number, rel_tol=rel_tol, abs_tol=abs_tol)
    return str(left).strip().casefold() == str(right).strip().casefold()


MEASURE_HINTS = (
    "_count", "count_", "_rate", "premium", "average", "median", "_gap", "_iqr", "p25", "p75",
    "stddev", "minimum", "maximum", "rows", "share", "error", "total", "number",
)
DIMENSION_HINTS = (
    "dimension", "_id", "_code", "_name", "_status", "_level", "_type", "_reason",
    "_category", "_label", "state", "county", "area", "metal", "benefit", "rating_value",
)


def _is_dimension(column: str, rows: list[dict[str, Any]]) -> bool:
    lowered = column.casefold()
    if any(hint in lowered for hint in MEASURE_HINTS):
        return False
    if any(hint in lowered for hint in DIMENSION_HINTS):
        return True
    return any(_number(row.get(column)) is None for row in rows[:20])


def _dimension_columns(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    return [key for key in rows[0] if _is_dimension(key, rows)]


def _numeric_columns(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    return [key for key in rows[0] if not _is_dimension(key, rows)]


def _column_map(predicted: list[dict[str, Any]], gold: list[dict[str, Any]]) -> dict[str, str]:
    if not predicted or not gold:
        return {}
    gold_keys = list(gold[0])
    mapping = {key: key for key in predicted[0] if key in gold[0]}
    used = set(mapping.values())
    for pred_group, gold_group in (
        (_dimension_columns(predicted), _dimension_columns(gold)),
        (_numeric_columns(predicted), _numeric_columns(gold)),
    ):
        unmatched_pred = [key for key in pred_group if key not in mapping]
        unmatched_gold = [key for key in gold_group if key not in used]
        for pred_key, gold_key in zip(unmatched_pred, unmatched_gold):
            mapping[pred_key] = gold_key
            used.add(gold_key)
    return mapping


def _row_key(row: dict[str, Any], columns: list[str]) -> tuple[str, ...]:
    return tuple(str(row.get(column)).strip().casefold() for column in columns)


def _rows_equal_unordered(predicted: list[dict[str, Any]], gold: list[dict[str, Any]]) -> bool:
    """Match complete rows one-to-one while ignoring nondeterministic tie order."""
    if len(predicted) != len(gold):
        return False
    unmatched = list(gold)
    for pred_row in predicted:
        match_index = next((
            index for index, gold_row in enumerate(unmatched)
            if set(pred_row) == set(gold_row)
            and all(_equal(pred_row[column], gold_row[column]) for column in gold_row)
        ), None)
        if match_index is None:
            return False
        unmatched.pop(match_index)
    return not unmatched


def compare_result_rows(
    predicted: list[dict[str, Any]] | None,
    gold: list[dict[str, Any]] | None,
    *,
    top_k: int = 10,
) -> dict[str, Any]:
    """Compare result tables with strict and explicitly relaxed measures.

    ``execution_result_match`` is deliberately strict: column names, row count,
    and every cell must match. Row order is ignored because SQL ties can be
    nondeterministic; ranking quality is reported separately. ``compatible_projection_match`` keeps
    the earlier alias/projection-tolerant diagnostic but is not a primary exact
    correctness measure.
    """
    predicted = predicted or []
    gold = gold or []
    if not gold:
        return {"status": "missing_gold", "execution_result_match": None}
    if not predicted:
        return {
            "status": "missing_prediction_rows",
            "execution_result_match": False,
            "compatible_projection_match": False,
            "strict_columns_match": False,
            "group_match_rate": 0.0,
            "group_precision": 0.0,
            "group_recall": 0.0,
            "group_jaccard": 0.0,
            "top_k_overlap": 0.0,
            "top_k_precision": 0.0,
            "top_k_recall": 0.0,
            "mean_numeric_relative_error": None,
            "max_numeric_relative_error": None,
        }

    mapping = _column_map(predicted, gold)
    pred_dimensions = [key for key in _dimension_columns(predicted) if key in mapping]
    pred_numeric = [key for key in _numeric_columns(predicted) if key in mapping]
    gold_dimensions = [mapping[key] for key in pred_dimensions]

    strict_columns_match = set(predicted[0]) == set(gold[0])
    strict_rows_match = (
        strict_columns_match
        and _rows_equal_unordered(predicted, gold)
    )
    rank_order_match = (
        strict_columns_match and len(predicted) == len(gold)
        and all(
            all(_equal(pred_row.get(column), gold_row.get(column)) for column in gold_row)
            for pred_row, gold_row in zip(predicted, gold)
        )
    )

    pred_keys = [_row_key(row, pred_dimensions) for row in predicted]
    gold_keys = [_row_key(row, gold_dimensions) for row in gold]
    pred_key_set, gold_key_set = set(pred_keys), set(gold_keys)
    group_intersection = len(pred_key_set & gold_key_set)
    group_precision = group_intersection / len(pred_key_set) if pred_key_set else 0.0
    group_recall = group_intersection / len(gold_key_set) if gold_key_set else 1.0
    group_f1 = (
        2 * group_precision * group_recall / (group_precision + group_recall)
        if group_precision + group_recall else 0.0
    )
    group_union = len(pred_key_set | gold_key_set)
    group_jaccard = group_intersection / group_union if group_union else 1.0

    pred_top = set(pred_keys[: min(top_k, len(pred_keys))])
    gold_top = set(gold_keys[: min(top_k, len(gold_keys))])
    top_intersection = len(pred_top & gold_top)
    top_precision = top_intersection / len(pred_top) if pred_top else 0.0
    top_recall = top_intersection / len(gold_top) if gold_top else 1.0
    top_union = len(pred_top | gold_top)
    top_jaccard = top_intersection / top_union if top_union else 1.0

    gold_by_key = {key: row for key, row in zip(gold_keys, gold)}
    errors: list[float] = []
    absolute_errors: list[float] = []
    symmetric_errors: list[float] = []
    compared_values = 0
    compatible_equal = len(predicted) == len(gold)
    if pred_dimensions:
        for key, pred_row in zip(pred_keys, predicted):
            gold_row = gold_by_key.get(key)
            if gold_row is None:
                compatible_equal = False
                continue
            for pred_column in pred_numeric:
                gold_column = mapping[pred_column]
                left, right = _number(pred_row.get(pred_column)), _number(gold_row.get(gold_column))
                if left is None or right is None:
                    continue
                compared_values += 1
                denominator = max(abs(right), 1e-12)
                errors.append(abs(left - right) / denominator)
                absolute_errors.append(abs(left - right))
                symmetric_denominator = abs(left) + abs(right)
                symmetric_errors.append(0.0 if symmetric_denominator == 0 else 2 * abs(left - right) / symmetric_denominator)
                if not _equal(left, right):
                    compatible_equal = False

    if not pred_dimensions and len(predicted) == len(gold):
        # Aggregates without labels are compared positionally.
        for pred_row, gold_row in zip(predicted, gold):
            for pred_column in pred_numeric:
                gold_column = mapping[pred_column]
                left, right = _number(pred_row.get(pred_column)), _number(gold_row.get(gold_column))
                if left is None or right is None:
                    continue
                compared_values += 1
                errors.append(abs(left - right) / max(abs(right), 1e-12))
                absolute_errors.append(abs(left - right))
                symmetric_denominator = abs(left) + abs(right)
                symmetric_errors.append(0.0 if symmetric_denominator == 0 else 2 * abs(left - right) / symmetric_denominator)
                if not _equal(left, right):
                    compatible_equal = False

    return {
        "status": "compared",
        "column_mapping": mapping,
        "predicted_row_count": len(predicted),
        "gold_row_count": len(gold),
        "compared_numeric_values": compared_values,
        "execution_result_match": bool(strict_rows_match),
        "compatible_projection_match": bool(compatible_equal and compared_values > 0),
        "strict_columns_match": strict_columns_match,
        "rank_order_match": rank_order_match,
        "group_match_rate": round(group_f1, 6),
        "group_precision": round(group_precision, 6),
        "group_recall": round(group_recall, 6),
        "group_jaccard": round(group_jaccard, 6),
        "top_k_overlap": round(top_jaccard, 6),
        "top_k_precision": round(top_precision, 6),
        "top_k_recall": round(top_recall, 6),
        "mean_numeric_relative_error": round(sum(errors) / len(errors), 8) if errors else None,
        "max_numeric_relative_error": round(max(errors), 8) if errors else None,
        "mean_numeric_absolute_error": round(sum(absolute_errors) / len(absolute_errors), 8) if absolute_errors else None,
        "numeric_smape": round(sum(symmetric_errors) / len(symmetric_errors), 8) if symmetric_errors else None,
    }


def numeric_claim_faithfulness(answer: str | None, evidence_rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Check whether explicit numeric claims appear in the cited/executed rows.

    This deterministic metric does not judge qualitative entailment; such cases
    are marked for human review rather than being silently counted as faithful.
    """
    answer = answer or ""
    evidence_rows = evidence_rows or []
    claims = [_number(match.group(0)) for match in NUMBER_PATTERN.finditer(answer)]
    claims = [value for value in claims if value is not None]
    evidence: list[float] = []
    for row in evidence_rows:
        for value in row.values():
            number = _number(value)
            if number is not None:
                evidence.append(number)
            elif isinstance(value, str):
                evidence.extend(
                    parsed for match in NUMBER_PATTERN.finditer(value)
                    if (parsed := _number(match.group(0))) is not None
                )
    if not claims:
        return {
            "numeric_claim_count": 0,
            "supported_numeric_claim_count": 0,
            "numeric_claim_faithfulness": None,
            "qualitative_review_required": True,
        }
    supported = sum(any(_equal(claim, value, rel_tol=1e-4, abs_tol=1e-4) for value in evidence) for claim in claims)
    return {
        "numeric_claim_count": len(claims),
        "supported_numeric_claim_count": supported,
        "numeric_claim_faithfulness": round(supported / len(claims), 6),
        "qualitative_review_required": True,
    }
