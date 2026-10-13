"""Integration regression coverage for staging CLI, API and legacy parsing."""
import csv

import pytest
from fastapi import HTTPException

from cli import _parse_csv_bool
from tnm8_breast import process_stage_batch
from agents.api import api_stage, api_audit_logs, StageRequest


def test_batch_staging(tmp_path):
    source = tmp_path / "cases.csv"
    output = tmp_path / "staged.csv"
    source.write_text("case,T,N,M\n1,T1,N0,M0\n2,T2,N1mi,M0\n3,T3,N3,M0\n", encoding="utf-8")
    process_stage_batch(str(source), str(output))
    with output.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    assert [record["anatomic_stage"] for record in records] == ["IA", "IIB", "IIIC"]


def test_batch_staging_rejects_invalid_and_no_partial_output(tmp_path):
    source = tmp_path / "cases.csv"
    output = tmp_path / "staged.csv"
    source.write_text("case,T,N,M\n1,T1,N0,M0\n2,T0,N0,M0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="CSV line 3"):
        process_stage_batch(str(source), str(output))
    assert not output.exists()


@pytest.mark.parametrize("text,expected", [
    ("TRUE", True), ("1", True), ("yes", True),
    ("FALSE", False), ("0", False), ("no", False), ("", False),
])
def test_legacy_boolean_parsing(text, expected):
    assert _parse_csv_bool(text) is expected


def test_legacy_boolean_rejects_ambiguous_values():
    with pytest.raises(ValueError):
        _parse_csv_bool("maybe")


def test_api_staging_endpoint():
    assert api_stage(StageRequest(t="T2", n="N0", m="M0"))["anatomic_stage"] == "IIA"
    with pytest.raises(HTTPException) as exc:
        api_stage(StageRequest(t="T0", n="N0", m="M0"))
    assert exc.value.status_code == 422


def test_audit_logs_require_admin_token(monkeypatch):
    monkeypatch.delenv("API_ADMIN_TOKEN", raising=False)
    with pytest.raises(HTTPException) as exc:
        api_audit_logs(None)
    assert exc.value.status_code == 403
