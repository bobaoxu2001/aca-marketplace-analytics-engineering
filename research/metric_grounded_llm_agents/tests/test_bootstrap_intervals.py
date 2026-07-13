from evaluation.bootstrap_intervals import bootstrap, paired_difference


class FirstChoice:
    def choice(self, values):
        return values[0]


def test_bootstrap_reports_question_cluster_count():
    result = bootstrap({"Q1": 1.0, "Q2": 0.0}, 5, FirstChoice())
    assert result["question_clusters"] == 2
    assert result["estimate"] == 0.5


def test_paired_difference_uses_shared_questions():
    result = paired_difference({"Q1": 1.0, "Q2": 0.5}, {"Q1": 0.0, "Q3": 1.0}, 5, FirstChoice())
    assert result["question_clusters"] == 1
    assert result["estimate"] == 1.0
