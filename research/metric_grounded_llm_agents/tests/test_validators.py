from agent.validators import referenced_tables, validate_sql


def test_referenced_tables_extracts_from_and_join():
    sql = "select * from fact_premium join dim_plan using (plan_key)"
    assert referenced_tables(sql) == {"fact_premium", "dim_plan"}


def test_validate_sql_blocks_forbidden_statement():
    result = validate_sql("drop table fact_premium", {"fact_premium"})
    assert not result.passed
    assert not result.checks["no_forbidden_statements"]


def test_validate_sql_allows_metric_query():
    sql = "select state_code, avg(monthly_premium) from fact_premium group by 1"
    result = validate_sql(sql, {"fact_premium"})
    assert result.passed
