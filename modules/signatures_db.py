SIGNATURES = {
    b"\xFF\xD8\xFF": ("JPEG Image", "Image"),
    b"\x89PNG\r\n\x1A\n": ("PNG Image", "Image"),
    b"%PDF": ("PDF Document", "Document"),
    b"PK\x03\x04": ("ZIP Archive / DOCX / XLSX", "Archive"),
    b"MZ": ("Windows Executable", "Executable"),
    b"GIF87a": ("GIF Image", "Image"),
    b"GIF89a": ("GIF Image", "Image"),
    b"SQLite format 3": ("SQLite Database", "Database")
}