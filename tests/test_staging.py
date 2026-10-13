"""Reference-table and input-validation regression cases for AJCC8 anatomy."""
import pytest
from staging import anatomic_stage


@pytest.mark.parametrize("t,n,m,stage", [
    ("Tis", "N0", "M0", "0"),
    ("T1mi", "N0", "M0", "IA"),
    ("T1b", "N0", "M0", "IA"),
    ("T0", "N1mi", "M0", "IB"),
    ("T1", "N1mi", "M0", "IB"),
    ("T0", "N1", "M0", "IIA"),
    ("T1", "N1", "M0", "IIA"),
    ("T2", "N0", "M0", "IIA"),
    ("T2", "N1", "M0", "IIB"),
    ("T2", "N1mi", "M0", "IIB"),
    ("T3", "N0", "M0", "IIB"),
    ("T0", "N2", "M0", "IIIA"),
    ("T1", "N2", "M0", "IIIA"),
    ("T2", "N2", "M0", "IIIA"),
    ("T3", "N1", "M0", "IIIA"),
    ("T3", "N1mi", "M0", "IIIA"),
    ("T3", "N2", "M0", "IIIA"),
    ("T4d", "N0", "M0", "IIIB"),
    ("T4", "N1", "M0", "IIIB"),
    ("T4", "N1mi", "M0", "IIIB"),
    ("T4", "N2", "M0", "IIIB"),
    ("T1", "N3b", "M0", "IIIC"),
    ("T4", "N3", "M0", "IIIC"),
    ("T2", "N0", "cM1", "IV"),
    ("TX", "NX", "M1", "IV"),
    ("cT2", "pN1a", "cM0", "IIB"),
    ("T1", "N0(i+)", "M0(i+)", "IA"),
])
def test_reference_table(t, n, m, stage):
    res = anatomic_stage(t, n, m)
    assert res["anatomic_stage"] == stage
    assert res["prognostic_stage"] == "not calculated"


@pytest.mark.parametrize("t,n,m", [
    ("T0", "N0", "M0"), ("Tis", "N1", "M0"),
    ("TX", "N0", "M0"), ("T1", "NX", "M0"),
    ("ypT0", "ypN0", "M0"), ("T2", "N1", "pM0"),
    ("T7", "N1", "M0"), ("T2", "N4", "M0"),
    ("T2", "N1", "M2"), ("", "N1", "M0"),
    ("<script>", "N1", "M0"),
])
def test_invalid_combinations(t, n, m):
    with pytest.raises(ValueError):
        anatomic_stage(t, n, m)
