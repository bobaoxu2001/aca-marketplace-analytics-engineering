import hashlib

from evaluation.verify_provenance_manifest import verify_entries


def test_verify_entries_reports_ok_mismatch_and_missing(tmp_path):
    payload = b"frozen research artifact\n"
    artifact = tmp_path / "artifact.json"
    artifact.write_bytes(payload)
    manifest = {
        "files": [
            {
                "path": "artifact.json",
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            },
            {
                "path": "changed.json",
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            },
            {
                "path": "missing.json",
                "bytes": 1,
                "sha256": hashlib.sha256(b"x").hexdigest(),
            },
        ]
    }
    (tmp_path / "changed.json").write_bytes(b"different research artifact")

    assert verify_entries(manifest, tmp_path) == [
        {"path": "artifact.json", "status": "ok"},
        {"path": "changed.json", "status": "size-mismatch"},
        {"path": "missing.json", "status": "missing"},
    ]
