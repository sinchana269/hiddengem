"""
HiddenGem - NLP Query Parser Tests

Small manual test suite for the deterministic tourism
query parser.

No external AI/LLM API is used.
"""

from query_parser import parse_query


def run_test(query: str, expected: dict) -> None:
    """Run one parser test and print the result."""

    result = parse_query(query)

    print("=" * 60)
    print("QUERY:")
    print(query)

    print("\nRESULT:")
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\nCHECK:")

    passed = True

    for key, expected_value in expected.items():

        actual_value = result.get(key)

        if actual_value != expected_value:
            passed = False

            print(
                f"FAIL - {key}: "
                f"expected={expected_value!r}, "
                f"actual={actual_value!r}"
            )

    if passed:
        print("PASS")


def main() -> None:

    tests = [
        {
            "query": (
                "I want a peaceful 2-day trip from Mysuru "
                "with waterfalls and local food under ₹4,000"
            ),
            "expected": {
                "location": "Mysuru",
                "duration_days": 2,
                "budget": 4000,
                "interests": ["waterfalls"],
                "activities": [],
                "travel_style": ["peaceful"],
                "food_preferences": ["local food"],
                "trip_type": [],
                "group_type": [],
            },
        },
        {
            "query": (
                "I want an adventure trip with rafting and wildlife"
            ),
            "expected": {
                "location": None,
                "duration_days": None,
                "budget": None,
                "interests": ["wildlife"],
                "activities": ["rafting"],
                "travel_style": ["adventure"],
                "food_preferences": [],
                "trip_type": [],
                "group_type": [],
            },
        },
        {
            "query": "Suggest a 3 day heritage trip",
            "expected": {
                "location": None,
                "duration_days": 3,
                "budget": None,
                "interests": ["heritage"],
                "activities": [],
                "travel_style": [],
                "food_preferences": [],
                "trip_type": [],
                "group_type": [],
            },
        },
        {
            "query": "I want a quiet nature trip",
            "expected": {
                "location": None,
                "duration_days": None,
                "budget": None,
                "interests": ["nature"],
                "activities": [],
                "travel_style": ["peaceful"],
                "food_preferences": [],
                "trip_type": [],
                "group_type": [],
            },
        },
        {
            "query": (
                "Plan a weekend road trip with friends "
                "for photography and trekking"
            ),
            "expected": {
                "location": None,
                "duration_days": None,
                "budget": None,
                "interests": ["photography"],
                "activities": ["trekking"],
                "travel_style": [],
                "food_preferences": [],
                "trip_type": ["road_trip", "weekend"],
                "group_type": ["friends"],
            },
        },
        {
            "query": (
                "I want a romantic trip with my partner "
                "and local vegetarian food"
            ),
            "expected": {
                "location": None,
                "duration_days": None,
                "budget": None,
                "interests": [],
                "activities": [],
                "travel_style": ["romantic"],
                "food_preferences": ["vegetarian food"],
                "trip_type": [],
                "group_type": ["couple"],
            },
        },
    ]

    print("=" * 60)
    print("HiddenGem NLP Query Parser Test Suite")
    print("=" * 60)

    passed_count = 0

    for test in tests:

        run_test(
            test["query"],
            test["expected"],
        )

        result = parse_query(test["query"])

        if all(
            result.get(key) == value
            for key, value in test["expected"].items()
        ):
            passed_count += 1

    print("\n" + "=" * 60)
    print(
        f"TEST SUMMARY: {passed_count}/{len(tests)} tests passed"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()