"""Hand-authored metric query templates for the NYC 311 second domain.

Analogous to :func:`agent.metric_sql.generate_metric_sql` for CMS: an oracle-routed
deterministic compiler that turns a question's registry metric plus its natural
grain (read from keywords) into canonical SQL derived from the metric definitions
in ``configs/metrics.nyc311.yaml``. It does not read gold SQL or gold answers; it
is the transparent rule-based upper bound for this domain. Queries are unqualified
and run against the ``marts`` schema (set by the caller).
"""

from __future__ import annotations

from typing import Any

_CLOSED = "response_hours is not null"
_RESOLVED = "avg(case when status = 'Closed' then 1.0 else 0.0 end)"


def _grain(text: str) -> str | None:
    if "agenc" in text:
        return "agency"
    if "borough" in text:
        return "borough"
    if "complaint type" in text or "complaint types" in text:
        return "complaint_type"
    if "channel" in text:
        return "open_data_channel_type"
    return None


def generate_nyc311_metric_sql(question: dict[str, Any]) -> str:
    metrics = question.get("metrics") or [""]
    metric = metrics[0]
    text = question.get("question", "").lower()

    # --- per-capita (join borough population, exclude Unspecified) ---
    if metric == "requests_per_1k_residents":
        where = "where f.complaint_type like 'Noise%'" if "noise" in text else ""
        if "resolution" in text or "low" in text:  # N024 combined
            return f"""select f.borough, count(*) * 1000.0 / b.population_2020 as requests_per_1k,
{_RESOLVED} as resolution_rate, count(*) as request_count
from fact_service_request as f join dim_borough as b on f.borough = b.borough
group by f.borough, b.population_2020
order by requests_per_1k desc, resolution_rate asc"""
        return f"""select f.borough, count(*) as request_count, b.population_2020,
count(*) * 1000.0 / b.population_2020 as requests_per_1k
from fact_service_request as f join dim_borough as b on f.borough = b.borough
{where}
group by f.borough, b.population_2020 order by requests_per_1k desc"""

    # --- agency share (window denominator) ---
    if metric == "agency_share":
        return """select agency, count(*) as request_count,
count(*) * 1.0 / sum(count(*)) over () as request_share
from fact_service_request group by 1 order by request_share desc, agency limit 15"""

    # --- unresolved share by borough (N030) ---
    if metric == "resolution_rate" and "unresolved" in text and "share" in text:
        return """select borough,
sum(case when status <> 'Closed' then 1 else 0 end) as unresolved_count,
count(*) as request_rows,
sum(case when status <> 'Closed' then 1 else 0 end) * 1.0 / count(*) as unresolved_share
from fact_service_request group by 1 order by unresolved_share desc"""

    # --- resolution rate ---
    if metric == "resolution_rate" and "unresolved" not in text:
        grain = _grain(text) or "borough"
        having = "having count(*) >= 1000" if grain in ("agency", "complaint_type") else ""
        order = "resolution_rate desc" + (f", {grain}" if having else "")
        limit = "limit 20" if grain == "complaint_type" else ("limit 15" if grain == "agency" else "")
        return f"""select {grain}, {_RESOLVED} as resolution_rate, count(*) as request_rows
from fact_service_request group by 1 {having} order by {order} {limit}"""

    # --- response time: mean/median ---
    if metric in {"median_response_hours", "mean_response_hours"}:
        # N023 noise vs heat category comparison
        if "noise" in text and ("heat" in text or "hot" in text):
            return f"""select case when complaint_type like 'Noise%' then 'Noise'
when upper(complaint_type) like '%HEAT%' then 'Heat/Hot Water' end as category,
median(response_hours) as median_response_hours, count(*) as closed_rows
from fact_service_request
where {_CLOSED} and (complaint_type like 'Noise%' or upper(complaint_type) like '%HEAT%')
group by 1 order by median_response_hours"""
        # N028 widest mean-median gap by complaint_type
        if "gap" in text or ("mean" in text and "median" in text and "complaint" in text):
            return f"""select complaint_type, avg(response_hours) as mean_response_hours,
median(response_hours) as median_response_hours,
avg(response_hours) - median(response_hours) as skew_gap, count(*) as closed_rows
from fact_service_request where {_CLOSED}
group by 1 having count(*) >= 1000 order by skew_gap desc, complaint_type limit 20"""
        # N025 top-5 highest-volume complaint types, median by borough
        if "five" in text or "top" in text or "highest-volume" in text or "highest volume" in text:
            return f"""with top5 as (select complaint_type from fact_service_request
group by 1 order by count(*) desc, complaint_type limit 5)
select f.borough, median(f.response_hours) as median_response_hours, count(*) as closed_rows
from fact_service_request as f where f.{_CLOSED} and f.complaint_type in (select complaint_type from top5)
group by 1 order by median_response_hours desc, f.borough"""
        # N026 agency x borough slowest median
        if "agenc" in text and "borough" in text:
            return f"""select agency, borough, median(response_hours) as median_response_hours,
count(*) as closed_rows from fact_service_request where {_CLOSED}
group by 1, 2 having count(*) >= 500 order by median_response_hours desc, agency, borough limit 20"""
        grain = _grain(text) or "borough"
        agg = "avg(response_hours)" if metric == "mean_response_hours" else "median(response_hours)"
        name = "mean_response_hours" if metric == "mean_response_hours" else "median_response_hours"
        both = ""
        if "mean" in text and "median" in text:  # N014 report both
            both = ", median(response_hours) as median_response_hours, avg(response_hours) as mean_response_hours"
            select = f"select {grain}{both}, count(*) as closed_rows"
            return f"""{select}
from fact_service_request where {_CLOSED} group by 1 order by median_response_hours desc"""
        having = "having count(*) >= 1000" if grain in ("agency", "complaint_type") else ""
        # mean questions (N015) also surface the median for context
        extra = ", median(response_hours) as median_response_hours" if metric == "mean_response_hours" else ""
        order = f"{name} desc" + (f", {grain}" if having else "")
        limit = "limit 20" if grain == "complaint_type" else ("limit 15" if grain == "agency" else "")
        return f"""select {grain}, {agg} as {name}{extra}, count(*) as closed_rows
from fact_service_request where {_CLOSED} group by 1 {having} order by {order} {limit}"""

    # --- channel mix ---
    if metric == "channel_mix" or (metric == "request_volume" and "channel" in text):
        if "online" in text or "share" in text:  # N019
            return """select borough, count(*) as request_count,
sum(case when open_data_channel_type = 'ONLINE' then 1 else 0 end) * 1.0 / count(*) as online_share
from fact_service_request group by 1 order by online_share desc"""
        return """select open_data_channel_type, count(*) as request_count
from fact_service_request group by 1 order by request_count desc"""

    # --- request volume (many grains) ---
    if metric in {"request_volume", "resolution_rate"}:
        # N017 unresolved by complaint_type
        if "unresolved" in text:
            return """select complaint_type,
sum(case when status <> 'Closed' then 1 else 0 end) as unresolved_count, count(*) as request_rows
from fact_service_request group by 1 order by unresolved_count desc, complaint_type limit 20"""
        # N009 distinct complaint types per agency
        if "distinct complaint" in text:
            return """select agency, count(distinct complaint_type) as distinct_complaint_types,
count(*) as request_rows from fact_service_request group by 1
order by distinct_complaint_types desc, agency limit 15"""
        # N021 most common complaint per borough
        if "each borough" in text or ("most common" in text and "borough" in text):
            return """with ranked as (select borough, complaint_type, count(*) as request_count,
row_number() over (partition by borough order by count(*) desc, complaint_type) as rn
from fact_service_request group by 1, 2)
select borough, complaint_type, request_count from ranked where rn = 1
order by request_count desc, borough"""
        # N029 repeat incident addresses
        if "address" in text or "repeat" in text:
            return """select incident_address, borough, count(*) as request_count
from fact_service_request where incident_address is not null
group by 1, 2 order by request_count desc, incident_address limit 20"""
        # N016/N027 monthly volume / month-over-month change
        if "month" in text:
            if "change" in text:
                return """with monthly as (select date_trunc('month', created_at) as month,
count(*) as request_count from fact_service_request group by 1)
select month, request_count,
request_count - lag(request_count) over (order by month) as mom_change
from monthly order by month"""
            return """select date_trunc('month', created_at) as month, count(*) as request_count
from fact_service_request group by 1 order by month"""
        # N004 status distribution
        if "status" in text:
            return """select status, count(*) as request_count
from fact_service_request group by 1 order by request_count desc"""
        grain = _grain(text) or "complaint_type"
        limit = "limit 10"
        return f"""select {grain}, count(*) as request_count
from fact_service_request group by 1 order by request_count desc, {grain} {limit}"""

    raise ValueError(f"No NYC 311 metric template is available for {metric!r}.")
