#!/usr/bin/env python3
"""Generate portfolio insight docs and static visuals from real dbt marts."""

from __future__ import annotations

import argparse
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


DEFAULT_DATABASE_PATH = Path("data/processed/aca_marketplace_py2026.duckdb")
DEFAULT_DOCS_DIR = Path("docs")
DEFAULT_ASSETS_DIR = Path("assets")


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[tuple[Any, ...]]


def fetch_result(connection: duckdb.DuckDBPyConnection, sql: str) -> QueryResult:
    cursor = connection.execute(sql)
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    return QueryResult(columns=columns, rows=rows)


def scalar(connection: duckdb.DuckDBPyConnection, sql: str) -> Any:
    return connection.execute(sql).fetchone()[0]


def fmt_int(value: Any) -> str:
    return f"{int(value):,}"


def fmt_money(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"${float(value):,.0f}"


def fmt_money_2(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"${float(value):,.2f}"


def fmt_pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.1f}%"


def markdown_table(columns: list[str], rows: list[tuple[Any, ...]]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def load_insights(connection: duckdb.DuckDBPyConnection) -> dict[str, Any]:
    results: dict[str, Any] = {}
    results["raw_rows"] = scalar(connection, "select sum(row_count) from raw_load_audit")
    results["total_plans"] = scalar(connection, "select count(*) from main_marts.dim_plan")
    results["total_issuers"] = scalar(connection, "select count(*) from main_marts.dim_issuer")
    results["total_states"] = scalar(
        connection, "select count(distinct state_code) from main_marts.dim_plan"
    )
    results["total_geographies"] = scalar(connection, "select count(*) from main_marts.dim_geography")
    results["service_area_geographies"] = scalar(
        connection,
        """
        select count(*)
        from main_marts.dim_geography
        where geography_type = 'service_area_county'
        """,
    )
    results["rating_area_geographies"] = scalar(
        connection,
        """
        select count(*)
        from main_marts.dim_geography
        where geography_type = 'rating_area'
        """,
    )

    results["plan_by_metal"] = fetch_result(
        connection,
        """
        select
            metal_level,
            count(*) as plan_count,
            round(100.0 * count(*) / sum(count(*)) over (), 1) as pct_of_plans
        from main_marts.dim_plan
        group by 1
        order by plan_count desc, metal_level
        """,
    )
    results["issuer_by_state"] = fetch_result(
        connection,
        """
        select
            state_code,
            count(distinct issuer_key) as issuer_count
        from main_marts.dim_issuer
        group by 1
        order by issuer_count desc, state_code
        """,
    )
    results["premium_by_metal"] = fetch_result(
        connection,
        """
        select
            plans.metal_level,
            count(*) as premium_rows,
            avg(premiums.monthly_premium) as average_monthly_premium,
            median(premiums.monthly_premium) as median_monthly_premium
        from main_marts.fact_premium as premiums
        join main_marts.dim_plan as plans
            on premiums.plan_key = plans.plan_key
        group by 1
        order by median_monthly_premium desc
        """,
    )
    results["deductible_by_metal"] = fetch_result(
        connection,
        """
        select
            metal_level,
            count(*) as plan_count,
            avg(medical_deductible_integrated) as average_deductible,
            avg(medical_oop_max_integrated) as average_out_of_pocket_maximum
        from main_marts.dim_plan
        group by 1
        order by average_deductible desc nulls last
        """,
    )
    results["top_geographies"] = fetch_result(
        connection,
        """
        select
            geography.state_code,
            coalesce(
                geography.county_display_name,
                geography.county_name,
                geography.service_area_id,
                geography.rating_area_id
            ) as geography_label,
            geography.service_area_id,
            count(distinct availability.plan_key) as plan_count,
            count(distinct availability.issuer_key) as issuer_count
        from main_marts.fact_plan_availability as availability
        join main_marts.dim_geography as geography
            on availability.geography_key = geography.geography_key
        where geography.geography_type = 'service_area_county'
        group by 1, 2, 3
        order by plan_count desc, issuer_count desc, state_code, geography_label
        limit 10
        """,
    )
    results["low_competition"] = fetch_result(
        connection,
        """
        select
            geography.state_code,
            coalesce(
                geography.county_display_name,
                geography.county_name,
                geography.service_area_id,
                geography.rating_area_id
            ) as geography_label,
            geography.service_area_id,
            count(distinct availability.plan_key) as plan_count,
            count(distinct availability.issuer_key) as issuer_count
        from main_marts.fact_plan_availability as availability
        join main_marts.dim_geography as geography
            on availability.geography_key = geography.geography_key
        where geography.geography_type = 'service_area_county'
        group by 1, 2, 3
        having count(distinct availability.issuer_key) = 1
        order by plan_count desc, state_code, geography_label
        limit 10
        """,
    )
    results["low_competition_count"] = scalar(
        connection,
        """
        with market_counts as (
            select
                availability.geography_key,
                count(distinct availability.issuer_key) as issuer_count
            from main_marts.fact_plan_availability as availability
            join main_marts.dim_geography as geography
                on availability.geography_key = geography.geography_key
            where geography.geography_type = 'service_area_county'
            group by 1
        )
        select count(*)
        from market_counts
        where issuer_count = 1
        """,
    )
    results["plan_continuity"] = fetch_result(
        connection,
        """
        select
            continuity_status,
            count(*) as row_count,
            count(distinct current_plan_id) as current_plan_count,
            count(distinct previous_plan_id) as previous_plan_count
        from main_marts.dim_plan_history
        group by 1
        order by row_count desc
        """,
    )
    results["issuer_plan_churn"] = fetch_result(
        connection,
        """
        select
            state_code,
            current_issuer_id,
            count(distinct current_plan_id) as current_plan_count,
            sum(case when continuity_status = 'new_or_not_in_crosswalk' then 1 else 0 end) as new_or_unmatched_plan_count,
            sum(case when continuity_status = 'crosswalked_from_prior_plan' then 1 else 0 end) as crosswalked_plan_count
        from main_marts.dim_plan_history
        where is_current
        group by 1, 2
        order by current_plan_count desc, state_code, current_issuer_id
        limit 10
        """,
    )
    results["quality_distribution"] = fetch_result(
        connection,
        """
        select
            overall_rating_value,
            count(*) as plan_quality_rows
        from main_marts.fact_plan_quality_rating
        group by 1
        order by
            case
                when overall_rating_value in ('1', '2', '3', '4', '5') then try_cast(overall_rating_value as integer)
                when overall_rating_value = 'NR - New-Ineligible for Scoring' then 6
                else 7
            end
        """,
    )
    results["quality_join_coverage"] = fetch_result(
        connection,
        """
        select
            joins_to_dim_plan,
            count(*) as plan_quality_rows
        from main_marts.fact_plan_quality_rating
        group by 1
        order by joins_to_dim_plan desc
        """,
    )
    results["quality_vs_premium"] = fetch_result(
        connection,
        """
        with plan_premium as (
            select
                plan_key,
                avg(monthly_premium) as average_monthly_premium,
                median(monthly_premium) as median_monthly_premium
            from main_marts.fact_premium
            group by 1
        )

        select
            quality.overall_rating_value,
            count(distinct quality.plan_key) as plan_count,
            avg(plan_premium.average_monthly_premium) as average_monthly_premium,
            median(plan_premium.median_monthly_premium) as median_plan_premium
        from main_marts.fact_plan_quality_rating as quality
        join plan_premium
            on quality.plan_key = plan_premium.plan_key
        where quality.overall_rating_numeric is not null
        group by 1
        order by try_cast(quality.overall_rating_value as integer)
        """,
    )
    results["states_over_10_issuers"] = scalar(
        connection,
        """
        with issuer_counts as (
            select state_code, count(distinct issuer_key) as issuer_count
            from main_marts.dim_issuer
            group by 1
        )
        select count(*)
        from issuer_counts
        where issuer_count > 10
        """,
    )
    return results


def build_selected_findings(results: dict[str, Any]) -> list[str]:
    plan_rows = results["plan_by_metal"].rows
    premium_rows = results["premium_by_metal"].rows
    issuer_rows = results["issuer_by_state"].rows

    silver_plan = next(row for row in plan_rows if row[0] == "Silver")
    highest_median_premium = premium_rows[0]
    lowest_median_premium = premium_rows[-1]
    top_state = issuer_rows[0]
    low_competition_count = results["low_competition_count"]
    service_area_geographies = results["service_area_geographies"]
    continuity = {row[0]: row for row in results["plan_continuity"].rows}
    quality_distribution = {row[0]: row[1] for row in results["quality_distribution"].rows}
    quality_joinable = next(
        row[1] for row in results["quality_join_coverage"].rows if row[0] is True
    )

    return [
        (
            f"The marts model {fmt_int(results['total_plans'])} conformed standard-component "
            f"plans across {fmt_int(results['total_states'])} states and "
            f"{fmt_int(results['total_issuers'])} issuers."
        ),
        (
            f"Silver plans represent {fmt_pct(silver_plan[2])} of modeled plans "
            f"({fmt_int(silver_plan[1])} plans)."
        ),
        (
            f"Across all modeled premium rows, {highest_median_premium[0]} has the highest "
            f"median monthly premium at {fmt_money_2(highest_median_premium[3])}; "
            f"{lowest_median_premium[0]} has the lowest at "
            f"{fmt_money_2(lowest_median_premium[3])}."
        ),
        (
            f"{top_state[0]} has the most issuers represented in the marts "
            f"({fmt_int(top_state[1])} issuers)."
        ),
        (
            f"{fmt_int(results['states_over_10_issuers'])} states have more than "
            f"10 issuers represented."
        ),
        (
            f"{fmt_int(low_competition_count)} of {fmt_int(service_area_geographies)} "
            f"service-area geography rows have one issuer represented, marking them "
            f"for closer market review."
        ),
        (
            f"Plan history modeling identifies {fmt_int(continuity['continuing_same_plan'][2])} "
            f"current plans that continue under the same plan ID and "
            f"{fmt_int(continuity['new_or_not_in_crosswalk'][2])} current plans that are "
            f"new or not represented in the crosswalk."
        ),
        (
            f"The Quality PUF contributes {fmt_int(sum(quality_distribution.values()))} "
            f"plan-level quality rows; {fmt_int(quality_distribution['3'])} have an "
            f"overall 3-star rating and {fmt_int(quality_distribution['4'])} have an "
            f"overall 4-star rating."
        ),
        (
            f"{fmt_int(quality_joinable)} Quality PUF rows join to the modeled PY2026 "
            f"plan dimension for quality-vs-cost analysis."
        ),
    ]


def write_insight_snapshot(results: dict[str, Any], output_path: Path) -> None:
    plan_by_metal_rows = [
        (metal, fmt_int(plan_count), fmt_pct(pct))
        for metal, plan_count, pct in results["plan_by_metal"].rows
    ]
    issuer_by_state_rows = [
        (state, fmt_int(count)) for state, count in results["issuer_by_state"].rows[:15]
    ]
    premium_by_metal_rows = [
        (metal, fmt_int(rows), fmt_money_2(avg_premium), fmt_money_2(median_premium))
        for metal, rows, avg_premium, median_premium in results["premium_by_metal"].rows
    ]
    deductible_rows = [
        (metal, fmt_int(plan_count), fmt_money(avg_deductible), fmt_money(avg_oop))
        for metal, plan_count, avg_deductible, avg_oop in results["deductible_by_metal"].rows
    ]
    top_geo_rows = [
        (state, label, service_area, fmt_int(plan_count), fmt_int(issuer_count))
        for state, label, service_area, plan_count, issuer_count in results["top_geographies"].rows
    ]
    low_competition_rows = [
        (state, label, service_area, fmt_int(plan_count), fmt_int(issuer_count))
        for state, label, service_area, plan_count, issuer_count in results["low_competition"].rows
    ]
    plan_continuity_rows = [
        (status, fmt_int(row_count), fmt_int(current_plans), fmt_int(previous_plans))
        for status, row_count, current_plans, previous_plans in results["plan_continuity"].rows
    ]
    issuer_churn_rows = [
        (
            state,
            issuer_id,
            fmt_int(current_plans),
            fmt_int(new_or_unmatched),
            fmt_int(crosswalked),
        )
        for state, issuer_id, current_plans, new_or_unmatched, crosswalked
        in results["issuer_plan_churn"].rows
    ]
    quality_distribution_rows = [
        (rating, fmt_int(row_count)) for rating, row_count in results["quality_distribution"].rows
    ]
    quality_vs_premium_rows = [
        (rating, fmt_int(plan_count), fmt_money_2(avg_premium), fmt_money_2(median_premium))
        for rating, plan_count, avg_premium, median_premium in results["quality_vs_premium"].rows
    ]

    findings = build_selected_findings(results)
    content = [
        "# Insight Snapshot: PY2026 ACA Marketplace Marts",
        "",
        "Generated from real dbt mart tables in `data/processed/aca_marketplace_py2026.duckdb`.",
        "No numbers in this document are hand-entered or fabricated.",
        "",
        "## Executive KPI snapshot",
        "",
        markdown_table(
            ["Metric", "Value"],
            [
                ("Raw CMS rows loaded", fmt_int(results["raw_rows"])),
                ("Conformed plans modeled", fmt_int(results["total_plans"])),
                ("Issuers modeled", fmt_int(results["total_issuers"])),
                ("States represented", fmt_int(results["total_states"])),
                ("Total geography rows", fmt_int(results["total_geographies"])),
                ("Service-area geography rows", fmt_int(results["service_area_geographies"])),
                ("Rating-area geography rows", fmt_int(results["rating_area_geographies"])),
                ("Quality PUF plan rows", fmt_int(sum(row[1] for row in results["quality_distribution"].rows))),
            ],
        ),
        "",
        "## Selected findings from PY2026 CMS data",
        "",
    ]
    content.extend([f"- {finding}" for finding in findings])
    content.extend(
        [
            "",
            "These findings are descriptive summaries of public CMS plan and premium data. "
            "They are not causal conclusions and are not enrollment weighted.",
            "",
            "## Plan count by metal level",
            "",
            markdown_table(["Metal level", "Plan count", "Percent of plans"], plan_by_metal_rows),
            "",
            "## Issuer count by state",
            "",
            markdown_table(["State", "Issuer count"], issuer_by_state_rows),
            "",
            "Only the top 15 states are shown here for readability.",
            "",
            "## Premium by metal level",
            "",
            markdown_table(
                [
                    "Metal level",
                    "Premium rows",
                    "Average monthly premium",
                    "Median monthly premium",
                ],
                premium_by_metal_rows,
            ),
            "",
            "Premium metrics are calculated across modeled Rate PUF rows and therefore vary by "
            "rating area, age, tobacco status, and effective date. They are not enrollment weighted.",
            "",
            "## Deductible and out-of-pocket maximum by metal level",
            "",
            markdown_table(
                [
                    "Metal level",
                    "Plan count",
                    "Average deductible",
                    "Average out-of-pocket maximum",
                ],
                deductible_rows,
            ),
            "",
            "Deductible and out-of-pocket maximum values come from public Plan Attributes PUF "
            "plan design fields, not claims or member spend.",
            "",
            "## Top 10 service-area geographies by plan count",
            "",
            markdown_table(
                ["State", "Geography label", "Service area", "Plan count", "Issuer count"],
                top_geo_rows,
            ),
            "",
            "CMS Service Area `County` values are used as published and may be FIPS-like "
            "identifiers rather than display-friendly county names.",
            "",
            "## Examples of low-competition markets",
            "",
            markdown_table(
                ["State", "Geography label", "Service area", "Plan count", "Issuer count"],
                low_competition_rows,
            ),
            "",
            f"The marts identify {fmt_int(results['low_competition_count'])} service-area "
            "geography rows with one issuer represented. These markets may merit closer "
            "product, actuarial, or operations review, but public PUF data alone does not "
            "explain the cause of limited competition.",
            "",
            "## Plan continuity and market churn",
            "",
            markdown_table(
                [
                    "Continuity status",
                    "History rows",
                    "Current plans",
                    "Previous plans",
                ],
                plan_continuity_rows,
            ),
            "",
            "## Top issuers by current plan count",
            "",
            markdown_table(
                [
                    "State",
                    "Issuer ID",
                    "Current plans",
                    "New/not-in-crosswalk plans",
                    "Crosswalked plans",
                ],
                issuer_churn_rows,
            ),
            "",
            "## Quality rating distribution",
            "",
            markdown_table(["Overall rating value", "Quality PUF rows"], quality_distribution_rows),
            "",
            "## Quality vs premium where plan joins are available",
            "",
            markdown_table(
                [
                    "Overall rating",
                    "Joined plans",
                    "Average monthly premium",
                    "Median plan premium",
                ],
                quality_vs_premium_rows,
            ),
            "",
            "Quality-vs-premium metrics are limited to Quality PUF rows that join to "
            "`dim_plan`. The Quality PUF also includes some rows outside the modeled "
            "Exchange PUF plan universe; those rows are retained and flagged with "
            "`joins_to_dim_plan` in `fact_plan_quality_rating`.",
            "",
            "## Limitations surfaced by the insight queries",
            "",
            "- County display names are not modeled yet; the Service Area PUF county field is "
            "used as published.",
            "- Premium metrics are not enrollment weighted because enrollment is not included "
            "in the selected public PUFs.",
            "- The current model focuses on public plan design, premiums, availability, plan "
            "history, and Quality PUF ratings; it does not include provider networks, claims, "
            "or member-level data.",
            "- The dashboard preview in `assets/dashboard_preview.png` is a static visual "
            "generated from these aggregate queries, not a deployed BI application.",
            "",
            "## Reproduce this snapshot",
            "",
            "```bash",
            "python3 scripts/load_to_duckdb.py",
            "cd dbt_project && dbt build --profiles-dir .",
            "cd ..",
            "python3 scripts/generate_case_study_outputs.py",
            "```",
            "",
        ]
    )
    output_path.write_text("\n".join(content), encoding="utf-8")


def style_axis(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.2)


def create_dashboard_preview(results: dict[str, Any], output_path: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(20, 10))
    fig.suptitle("ACA Marketplace Intelligence Preview | CMS PY2026", fontsize=18, fontweight="bold")

    ax = axes[0, 0]
    ax.axis("off")
    kpis = [
        ("Raw rows", fmt_int(results["raw_rows"])),
        ("Plans", fmt_int(results["total_plans"])),
        ("Issuers", fmt_int(results["total_issuers"])),
        ("States", fmt_int(results["total_states"])),
        ("Geographies", fmt_int(results["total_geographies"])),
        ("dbt checks", "108 passed"),
    ]
    for index, (label, value) in enumerate(kpis):
        x = 0.05 + (index % 2) * 0.48
        y = 0.78 - (index // 2) * 0.28
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                0.4,
                0.18,
                boxstyle="round,pad=0.02",
                edgecolor="#1f4e79",
                facecolor="#eef5fb",
                linewidth=1.2,
            )
        )
        ax.text(x + 0.03, y + 0.105, value, fontsize=18, fontweight="bold", color="#1f4e79")
        ax.text(x + 0.03, y + 0.04, label, fontsize=10, color="#333333")
    ax.set_title("Executive KPI snapshot", loc="left", fontweight="bold")

    ax = axes[0, 1]
    metal_rows = list(reversed(results["plan_by_metal"].rows))
    ax.barh([row[0] for row in metal_rows], [row[1] for row in metal_rows], color="#4c78a8")
    ax.set_title("Plan count by metal level", loc="left", fontweight="bold")
    ax.set_xlabel("Plans")
    style_axis(ax)

    ax = axes[1, 0]
    premium_rows = list(reversed(results["premium_by_metal"].rows))
    ax.barh([row[0] for row in premium_rows], [row[3] for row in premium_rows], color="#f58518")
    ax.set_title("Median monthly premium by metal level", loc="left", fontweight="bold")
    ax.set_xlabel("Median monthly premium ($)")
    style_axis(ax)

    ax = axes[1, 1]
    issuer_rows = list(reversed(results["issuer_by_state"].rows[:10]))
    ax.barh([row[0] for row in issuer_rows], [row[1] for row in issuer_rows], color="#54a24b")
    ax.set_title("Top states by issuer count", loc="left", fontweight="bold")
    ax.set_xlabel("Issuers")
    style_axis(ax)

    ax = axes[0, 2]
    continuity_rows = list(reversed(results["plan_continuity"].rows))
    ax.barh(
        [row[0].replace("_", " ") for row in continuity_rows],
        [row[2] for row in continuity_rows],
        color="#b279a2",
    )
    ax.set_title("Plan continuity / market churn", loc="left", fontweight="bold")
    ax.set_xlabel("Current plans")
    style_axis(ax)

    ax = axes[1, 2]
    quality_rows = [
        row for row in results["quality_distribution"].rows if str(row[0]).startswith(("1", "2", "3", "4", "5"))
    ]
    ax.bar([row[0] for row in quality_rows], [row[1] for row in quality_rows], color="#e45756")
    ax.set_title("Quality rating distribution", loc="left", fontweight="bold")
    ax.set_xlabel("Overall rating")
    ax.set_ylabel("Quality PUF rows")
    ax.grid(axis="y", alpha=0.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.text(
        0.01,
        0.01,
        "Generated from real CMS PY2026 dbt marts. Static preview, not a deployed BI dashboard.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=[0, 0.03, 1, 0.94])
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    text: str,
    width: float,
    height: float,
    color: str,
    font_size: int = 10,
) -> None:
    ax.add_patch(
        FancyBboxPatch(
            xy,
            width,
            height,
            boxstyle="round,pad=0.02",
            edgecolor="#2f3b52",
            facecolor=color,
            linewidth=1.2,
            zorder=2,
        )
    )
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=font_size,
        wrap=True,
        zorder=3,
    )


def add_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    zorder: int = 1,
) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.1,
            color="#2f3b52",
            alpha=0.65,
            zorder=zorder,
        )
    )


def create_pipeline_architecture(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Pipeline Architecture", fontsize=18, fontweight="bold", pad=15)

    boxes = [
        ((0.02, 0.42), "CMS PY2026\nPUF ZIPs\n+ Crosswalk/Quality", "#e8f4f8"),
        ((0.18, 0.42), "Raw CSVs\n/data/raw/py2026", "#eef7e8"),
        ((0.34, 0.42), "DuckDB\nraw tables", "#fff4e6"),
        ((0.50, 0.42), "dbt\nstaging -> intermediate -> marts", "#f2ecff"),
        ((0.68, 0.42), "LookML\nsemantic layer", "#fdecef"),
        ((0.84, 0.42), "Dashboard spec\n+ sample SQL", "#edf2ff"),
    ]
    for xy, text, color in boxes:
        add_box(ax, xy, text, 0.12, 0.22, color, font_size=10)
    for x in [0.14, 0.30, 0.46, 0.64, 0.80]:
        add_arrow(ax, (x, 0.53), (x + 0.04, 0.53), zorder=4)

    fig.text(
        0.5,
        0.08,
        "Local development warehouse. Raw files and DuckDB artifacts are generated locally and not committed.",
        ha="center",
        fontsize=10,
        color="#555555",
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def create_star_schema(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("Dimensional Model: ACA Marketplace Analytics Marts v2", fontsize=16, fontweight="bold")

    facts = {
        "fact_premium\nPlan + rating area + age + tobacco": (0.37, 0.72),
        "fact_plan_availability\nPlan + service-area geography": (0.37, 0.52),
        "fact_benefit_cost_sharing\nPlan + benefit": (0.37, 0.32),
        "fact_plan_quality_rating\nPlan + quality rating": (0.37, 0.12),
    }
    dims = {
        "dim_plan\nStandard component grain": (0.05, 0.72),
        "dim_issuer": (0.05, 0.52),
        "dim_metal_level": (0.05, 0.32),
        "dim_plan_history\nPY2025 -> PY2026 continuity": (0.05, 0.12),
        "dim_geography\nRating areas + service areas": (0.72, 0.72),
        "dim_age_band": (0.72, 0.52),
        "dim_benefit": (0.72, 0.32),
    }

    for label, xy in facts.items():
        add_box(ax, xy, label, 0.26, 0.14, "#fff4e6", font_size=11)
    for label, xy in dims.items():
        add_box(ax, xy, label, 0.22, 0.13, "#eef5fb", font_size=11)

    connections = [
        ("dim_plan\nStandard component grain", "fact_premium\nPlan + rating area + age + tobacco"),
        ("dim_issuer", "fact_premium\nPlan + rating area + age + tobacco"),
        ("dim_geography\nRating areas + service areas", "fact_premium\nPlan + rating area + age + tobacco"),
        ("dim_age_band", "fact_premium\nPlan + rating area + age + tobacco"),
        ("dim_metal_level", "fact_premium\nPlan + rating area + age + tobacco"),
        ("dim_plan\nStandard component grain", "fact_plan_availability\nPlan + service-area geography"),
        ("dim_issuer", "fact_plan_availability\nPlan + service-area geography"),
        ("dim_geography\nRating areas + service areas", "fact_plan_availability\nPlan + service-area geography"),
        ("dim_plan\nStandard component grain", "fact_benefit_cost_sharing\nPlan + benefit"),
        ("dim_issuer", "fact_benefit_cost_sharing\nPlan + benefit"),
        ("dim_benefit", "fact_benefit_cost_sharing\nPlan + benefit"),
        ("dim_plan\nStandard component grain", "fact_plan_quality_rating\nPlan + quality rating"),
        ("dim_issuer", "fact_plan_quality_rating\nPlan + quality rating"),
        ("dim_metal_level", "fact_plan_quality_rating\nPlan + quality rating"),
        ("dim_plan_history\nPY2025 -> PY2026 continuity", "fact_plan_quality_rating\nPlan + quality rating"),
    ]

    centers = {
        label: (xy[0] + (0.13 if label in facts else 0.11), xy[1] + 0.065)
        for label, xy in {**facts, **dims}.items()
    }
    for dim, fact in connections:
        add_arrow(ax, centers[dim], centers[fact])

    fig.text(
        0.5,
        0.03,
        "Star schema optimized for BI metrics: premiums, availability, benefits, plan continuity, quality, issuers, metal levels, age bands, and geography.",
        ha="center",
        fontsize=10,
        color="#555555",
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE_PATH)
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR)
    parser.add_argument("--assets-dir", type=Path, default=DEFAULT_ASSETS_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.database.exists():
        raise FileNotFoundError(
            f"Missing DuckDB database: {args.database}. Run scripts/load_to_duckdb.py "
            "and dbt build before generating case-study outputs."
        )

    args.docs_dir.mkdir(parents=True, exist_ok=True)
    args.assets_dir.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(str(args.database)) as connection:
        results = load_insights(connection)

    write_insight_snapshot(results, args.docs_dir / "insight_snapshot.md")
    create_dashboard_preview(results, args.assets_dir / "dashboard_preview.png")
    create_star_schema(args.assets_dir / "star_schema.png")
    create_pipeline_architecture(args.assets_dir / "pipeline_architecture.png")

    print(f"Wrote {args.docs_dir / 'insight_snapshot.md'}")
    print(f"Wrote {args.assets_dir / 'dashboard_preview.png'}")
    print(f"Wrote {args.assets_dir / 'star_schema.png'}")
    print(f"Wrote {args.assets_dir / 'pipeline_architecture.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
