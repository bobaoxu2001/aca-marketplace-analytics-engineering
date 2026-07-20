from __future__ import annotations

from scripts.download_cms_pufs import DATASETS, PufDataset, score_candidate


def test_score_candidate_prefers_2026_csv_urls() -> None:
    dataset = DATASETS[0]
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
        cms_zip_url="https://example.com/rate.zip",
        search_terms=("2026", "rate", "puf"),
    )
    assert score_candidate("https://example.com/page.html", dataset) == -1


def test_all_datasets_have_unique_filenames() -> None:
    filenames = [dataset.filename for dataset in DATASETS]
    assert len(filenames) == len(set(filenames))
