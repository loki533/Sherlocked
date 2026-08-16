from sherlocked.scanner.evidence_scanner import EvidenceScanner


def test_scanner_finds_files(tmp_path):
    evidence = tmp_path / "evidence"
    evidence.mkdir()

    file1 = evidence / "test1.txt"
    file2 = evidence / "test2.txt"

    file1.write_text("test 1")
    file2.write_text("test 2")

    files = EvidenceScanner.scan(evidence)

    assert len(files) == 2

    assert file1 in files
    assert file2 in files

def test_scanner_finds_nested_files(tmp_path):
    evidence = tmp_path / "evidence"
    nested = evidence / "nested"

    nested.mkdir(parents=True)

    test_file = nested / "test.txt"
    test_file.write_text("nested test")

    files = EvidenceScanner.scan(evidence)

    assert test_file in files