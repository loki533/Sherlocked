from pathlib import Path
from sherlocked.recovery.file_carver import FileCarver

def test_scan_finds_png_signature(tmp_path):
    image=tmp_path/'image.dd'; payload=b'A'*31+b'\x89PNG\r\n\x1a\n'+b'fake'+b'IEND\xaeB`\x82'+b'Z'*10; image.write_bytes(payload)
    candidates=FileCarver(image).scan(); assert {c['extension'] for c in candidates}=={'png'}; assert candidates[0]['offset']==31

def test_carve_png_writes_validated_candidate(tmp_path):
    image=tmp_path/'image.dd'; png=b'\x89PNG\r\n\x1a\n'+b'012345'+b'IEND\xaeB`\x82'; image.write_bytes(b'X'*100+png+b'Y'*20)
    result=FileCarver(image).carve_candidate(100,'png',tmp_path/'carved'); assert result is not None; assert result['size']==len(png); assert Path(result['output_path']).read_bytes()==png

def test_invalid_png_is_rejected(tmp_path):
    image=tmp_path/'image.dd'; image.write_bytes(b'\x89PNG\r\n\x1a\n'+b'incomplete'); assert FileCarver(image).carve_candidate(0,'png',tmp_path/'out') is None

def test_pdf_carving_uses_eof_marker(tmp_path):
    image=tmp_path/'image.dd'; pdf=b'%PDF-1.7\nhello\n%%EOF'; image.write_bytes(b'A'*7+pdf+b'trailing bytes'); result=FileCarver(image).carve_candidate(7,'pdf',tmp_path/'out'); assert result is not None; assert result['size']==len(pdf); assert Path(result['output_path']).read_bytes()==pdf
