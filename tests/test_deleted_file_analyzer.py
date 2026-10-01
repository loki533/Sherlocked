from sherlocked.filesystem.deleted_file_analyzer import DeletedFileAnalyzer


def record(number, in_use, directory=False, filename="sample.txt"):
    return {
        "record_number": number,
        "sequence_number": 7,
        "record_offset": number * 1024,
        "flags_decoded": {
            "in_use": in_use,
            "directory": directory,
        },
        "file_names": [
            {
                "filename": filename,
                "parent_record": 5,
                "created": "2026-01-01 00:00:00",
                "modified": "2026-01-02 00:00:00",
                "mft_modified": "2026-01-03 00:00:00",
                "accessed": "2026-01-04 00:00:00",
                "allocated_size": 4096,
                "real_size": 1234,
                "namespace": 1,
            }
        ],
    }


def test_only_unused_records_become_candidates():
    analyzer = DeletedFileAnalyzer()

    candidates = analyzer.analyze([
        record(10, True),
        record(11, False),
    ])

    assert len(candidates) == 1
    assert candidates[0]["record_number"] == 11
    assert candidates[0]["filename"] == "sample.txt"
    assert candidates[0]["status"] == "deleted_or_unused"


def test_directory_candidate_is_identified_separately():
    analyzer = DeletedFileAnalyzer()

    candidates = analyzer.analyze([
        record(12, False, directory=True, filename="old-folder"),
    ])

    assert candidates[0]["is_directory"] is True
    assert candidates[0]["type"] == "directory"


def test_multiple_file_names_are_preserved():
    analyzer = DeletedFileAnalyzer()
    item = record(13, False, filename="first.txt")
    item["file_names"].append({
        "filename": "second.txt",
        "parent_record": 8,
        "real_size": 10,
    })

    candidates = analyzer.analyze([item])

    assert len(candidates) == 2
    assert {c["filename"] for c in candidates} == {"first.txt", "second.txt"}


def test_summary_counts_files_and_directories():
    analyzer = DeletedFileAnalyzer()
    candidates = analyzer.analyze([
        record(1, False),
        record(2, False, directory=True, filename="folder"),
    ])

    assert analyzer.summary(candidates) == {
        "total": 2,
        "files": 1,
        "directories": 1,
    }
