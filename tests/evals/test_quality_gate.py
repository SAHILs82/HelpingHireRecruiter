from app.models.schemas import DecisionLabel


def test_decision_label_enum_contract() -> None:
    expected = {
        "strong_fit",
        "borderline",
        "reject",
        "fast_track",
        "needs_human_review",
    }
    assert set(item.value for item in DecisionLabel) == expected
