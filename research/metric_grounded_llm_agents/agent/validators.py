"""Validation checks for generated and gold SQL."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


FORBIDDEN_SQL = re.compile(r"\b(insert|update|delete|drop|alter|create|copy|attach|detach|pragma)\b", re.I)
TABLE_PATTERN = re.compile(r"\b(?:from|join)\s+([A-Za-z_][A-Za-z0-9_\.]*)", re.I)
CTE_PATTERN = re.compile(r"(?:with|,)\s+([A-Za-z_][A-Za-z0-9_]*)\s+as\s*\(", re.I)


@dataclass
class ValidationResult:
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    messages: list[str] = field(default_factory=list)


def referenced_tables(sql: str) -> set[str]:
    ctes = {match.group(1).lower() for match in CTE_PATTERN.finditer(sql)}
    tables = {match.group(1).split(".")[-1].lower() for match in TABLE_PATTERN.finditer(sql)}
    return tables.difference(ctes)


def validate_sql(
    sql: str,
    allowed_tables: Iterable[str],
    required_terms: Iterable[str] = (),
) -> ValidationResult:
    allowed = {table.lower() for table in allowed_tables}
    tables = referenced_tables(sql)
    checks = {
        "is_select_query": bool(re.match(r"^\s*(with\b.*)?select\b", sql, re.I | re.S)),
        "no_forbidden_statements": FORBIDDEN_SQL.search(sql) is None,
        "uses_only_allowed_tables": not tables.difference(allowed),
        "has_referenced_table": bool(tables),
        "required_terms_present": all(term.lower() in sql.lower() for term in required_terms),
    }
    messages: list[str] = []
    if tables.difference(allowed):
        messages.append(f"Unexpected tables: {', '.join(sorted(tables.difference(allowed)))}")
    for term in required_terms:
        if term.lower() not in sql.lower():
            messages.append(f"Missing required term: {term}")
    return ValidationResult(passed=all(checks.values()), checks=checks, messages=messages)


def claim_support_status(rows: list[dict], answer: str) -> str:
    if not rows:
        return "unsupported_no_rows"
    if "unknown" in answer.lower() or "not available" in answer.lower():
        return "unsupported_claim_marked"
    return "supported_by_result_rows"
