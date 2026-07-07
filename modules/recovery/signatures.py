FILE_SIGNATURES = {

    "jpg": {
        "header": b"\xff\xd8\xff",
        "footer": b"\xff\xd9"
    },

    "png": {
        "header": b"\x89PNG\r\n\x1a\n",
        "footer": b"IEND\xaeB`\x82"
    },

    "pdf": {
        "header": b"%PDF",
        "footer": b"%%EOF"
    },

    "zip": {
        "header": b"PK\x03\x04",
        "footer": None
    }
}