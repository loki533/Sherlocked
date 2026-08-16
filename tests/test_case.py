from sherlocked.core.case import Case


def test_case_creation():
    case = Case(
        case_id="TEST001",
        investigator="tester",
        description="Test investigation",
        evidence_path="tests/fixtures"
    )

    assert case.case_id == "TEST001"
    assert case.investigator == "tester"
    assert case.description == "Test investigation"
    assert case.evidence_path == "tests/fixtures"

    assert case.hashes == {}
    assert case.metadata == []
    assert case.timeline == []
    assert case.recovered_files == []


def test_case_to_dict():
    case = Case(
        case_id="TEST001",
        investigator="tester",
        description="Test investigation",
        evidence_path="tests/fixtures"
    )

    data = case.to_dict()

    assert data["case_id"] == "TEST001"
    assert data["investigator"] == "tester"
    assert data["description"] == "Test investigation"
    assert data["evidence_path"] == "tests/fixtures"
    assert "created_at" in data


def test_case_from_dict():
    data = {
        "case_id": "TEST001",
        "investigator": "tester",
        "description": "Test investigation",
        "evidence_path": "tests/fixtures",
        "created_at": "2026-08-15 12:00:00",
        "metadata": []
    }

    case = Case.from_dict(data)

    assert case.case_id == "TEST001"
    assert case.investigator == "tester"
    assert case.description == "Test investigation"
    assert case.evidence_path == "tests/fixtures"
    assert case.created_at == "2026-08-15 12:00:00"