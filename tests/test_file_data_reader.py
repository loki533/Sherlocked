import struct
from pathlib import Path

from sherlocked.filesystem.mft_parser import MFTParser
from sherlocked.filesystem.file_data_reader import FileDataReader


def test_data_run_parser_decodes_relative_lcn():
    # header 0x11 = 1-byte length + 1-byte signed LCN delta
    # run 1: length 3, LCN 10
    # run 2: length 2, LCN delta +5 => LCN 15
    encoded = bytes([0x11, 0x03, 0x0A, 0x11, 0x02, 0x05, 0x00])
    assert MFTParser.parse_data_runs(encoded) == [
        {"vcn": 0, "lcn": 10, "length": 3, "sparse": False},
        {"vcn": 3, "lcn": 15, "length": 2, "sparse": False},
    ]


def test_data_run_parser_handles_sparse_run():
    encoded = bytes([0x11, 0x02, 0x05, 0x01, 0x02, 0x00])
    runs = MFTParser.parse_data_runs(encoded)
    assert runs[0]["lcn"] == 5
    assert runs[1]["sparse"] is True
    assert runs[1]["length"] == 2


def test_resident_data_is_returned_directly(tmp_path):
    image = tmp_path / "evidence.dd"
    image.write_bytes(b"unused")
    reader = FileDataReader(image, 0, 4096)
    assert reader.read_attribute({
        "resident": True,
        "content_length": 5,
        "content": b"helloEXTRA",
    }) == b"hello"


def test_nonresident_data_is_reconstructed_from_runs(tmp_path):
    image = tmp_path / "evidence.dd"
    cluster_size = 4
    image.write_bytes(b"____AAAA____BBBB____")
    reader = FileDataReader(image, 0, cluster_size)
    data = {
        "resident": False,
        "real_size": 8,
        "data_runs": [
            {"vcn": 0, "lcn": 1, "length": 1, "sparse": False},
            {"vcn": 1, "lcn": 3, "length": 1, "sparse": False},
        ],
    }
    assert reader.read_attribute(data) == b"AAAABBBB"


def test_nonresident_sparse_run_is_zero_filled(tmp_path):
    image = tmp_path / "evidence.dd"
    image.write_bytes(b"____AAAA____")
    reader = FileDataReader(image, 0, 4)
    data = {
        "resident": False,
        "real_size": 8,
        "data_runs": [
            {"vcn": 0, "lcn": 1, "length": 1, "sparse": False},
            {"vcn": 1, "lcn": None, "length": 1, "sparse": True},
        ],
    }
    assert reader.read_attribute(data) == b"AAAA\x00\x00\x00\x00"
