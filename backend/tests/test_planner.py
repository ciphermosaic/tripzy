from app.services.planner import infer_days, infer_destination


def test_infers_known_destination():
    assert infer_destination("Plan a 4 day trip to Goa", None) == "Goa"


def test_infers_days():
    assert infer_days("I want 5 days in Kerala", None, None) == 5

def test_parse_budget():
    from app.services.planner import parse_budget

    assert parse_budget("Budget ₹15k") == 15000
    assert parse_budget("Budget Rs 20,000") == 20000
    assert parse_budget("Budget 25k") == 25000


def test_infer_destination_returns_none_for_unknown_place():
    assert (
        infer_destination(
            "Plan a trip somewhere nice",
            None,
        )
        is None
    )