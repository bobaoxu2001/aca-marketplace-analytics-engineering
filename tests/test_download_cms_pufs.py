from __future__ import annotations

from scripts.download_cms_pufs import PufDataset, load_datasets, score_candidate


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
