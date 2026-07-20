from evaluation.aggregate_human_review import categorical_kappa, weighted_kappa


def test_weighted_kappa_is_one_for_identical_ratings():
    assert weighted_kappa([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 1.0


def test_weighted_kappa_penalizes_reversed_ratings():
    assert weighted_kappa([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) < 0


def test_categorical_kappa_reports_exact_agreement():
    agreement, kappa = categorical_kappa(["yes", "no", "yes"], ["yes", "no", "no"])
    assert agreement == 0.666667
    assert kappa is not None
