from __future__ import annotations

from scripts import download_cms_pufs
from scripts.download_cms_pufs import PufDataset, candidate_urls, load_datasets, score_candidate


def test_score_candidate_prefers_2026_csv_urls() -> None:
    dataset = load_datasets()[0]
    good = score_candidate(
        "https://download.cms.gov/marketplace-puf/2026/rate-puf.csv",
        dataset,
    )
    bad = score_candidate("https://example.com/old/2019/rate.txt", dataset)
    assert good > bad
    assert good >= 10


def test_score_candidate_rejects_non_data_urls() -> None:
    dataset = PufDataset(
        key="rate",
        label="Rate PUF",
        filename="rate_puf_py2026.csv",
        socrata_view_id="",
        cms_zip_url="https://example.com/rate.zip",
        datafile_url="https://example.com/rate.csv",
        search_terms=("2026", "rate", "puf"),
        landing_urls=(),
    )
    assert score_candidate("https://example.com/page.html", dataset) == -1


def test_all_datasets_have_unique_filenames() -> None:
    filenames = [dataset.filename for dataset in load_datasets()]
    assert len(filenames) == len(set(filenames))


def test_candidate_urls_include_data_healthcare_api_results(monkeypatch) -> None:
    dataset = load_datasets()[0]
    api_url = (
        f"https://data.healthcare.gov/resource/{dataset.socrata_view_id}.csv"
        "?$limit=50000000"
    )

    monkeypatch.setattr(
        download_cms_pufs,
        "discover_socrata_asset_metadata",
        lambda *_args: set(),
    )
    monkeypatch.setattr(
        download_cms_pufs,
        "discover_catalog_data_gov",
        lambda *_args: set(),
    )
    monkeypatch.setattr(
        download_cms_pufs,
        "discover_data_healthcare_api",
        lambda *_args: {api_url},
    )
    monkeypatch.setattr(
        download_cms_pufs,
        "discover_page_urls",
        lambda *_args: set(),
    )
    assert api_url in candidate_urls(object(), dataset, [])
    assert score_candidate(api_url, dataset) > 0
    assert (
        score_candidate(
            "https://data.healthcare.gov/resource/wxyz-9876.csv?$limit=50000000",
            dataset,
        )
        == -1
    )
