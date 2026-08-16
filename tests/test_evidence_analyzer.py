from sherlocked.core.case import Case
from sherlocked.core.evidence_analyzer import EvidenceAnalyzer


def test_evidence_analysis(tmp_path):
    evidence = tmp_path / "evidence"
    evidence.mkdir()

    test_file = evidence / "test.png"

    test_file.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        b"test image data"
    )

    case = Case(
        case_id="TEST001",
        investigator="tester",
        description="Automated test",
        evidence_path=evidence
    )

    analyzer = EvidenceAnalyzer()

    result = analyzer.analyze(case)

    assert result is case

    assert len(result.metadata) == 1

    file_info = result.metadata[0]

    assert file_info["name"] == "test.png"
    assert file_info["category"] == "PNG image"
    assert file_info["suspicious"] is False

    assert "hashes" in file_info
    assert "signature" in file_info