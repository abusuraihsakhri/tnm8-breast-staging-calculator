"""AJCC 8th-edition breast cancer *anatomic* stage groups.

Based on NCI PDQ Breast Cancer Treatment, Table 8:
https://www.cancer.gov/types/breast/hp/breast-treatment-pdq

This does not calculate clinical/pathological *prognostic* stage, which also
requires grade, ER/PR/HER2 and sometimes other information. This software is
an educational reference and is not a substitute for formal staging.
"""
from __future__ import annotations

import re


def _category(value: str, kind: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{kind} must be a TNM category string")
    text = value.strip()
    # Strip clinical/pathological prefixes but do not accept post-treatment
    # (yc/yp) categories: yp stage groups cannot be inferred from this table.
    if text.lower().startswith(("yc", "yp")):
        raise ValueError("Post-neoadjuvant categories need dedicated staging rules")
    if text[:1].lower() in ("c", "p") and len(text) > 1:
        text = text[1:]
        if kind == "M" and value.strip().lower().startswith("pm0"):
            raise ValueError("pM0 is not a valid category; use cM0")
    text = text.upper()
    if kind == "T":
        if text in ("TIS", "T0", "T1MI", "T1", "T2", "T3", "T4", "TX"):
            return "T1" if text == "T1MI" else ("Tis" if text == "TIS" else text)
        if re.fullmatch(r"T1[ABC]|T4[ABCD]", text):
            return text[:2]
    elif kind == "N":
        if text in ("N0", "N1MI", "N1", "N2", "N3", "NX"):
            return "N1mi" if text == "N1MI" else text
        if re.fullmatch(r"N[123][ABC]", text):
            return text[:2]
        if text in ("N0(I+)", "N0(MOL+)"):
            return "N0"
    elif kind == "M":
        if text in ("M0", "M0(I+)", "M1"):
            return "M0" if text == "M0(I+)" else text
    raise ValueError(f"Unsupported {kind} category: {value!r}")


def anatomic_stage(t: str, n: str, m: str) -> dict[str, str]:
    """Return a verified AJCC8 anatomic stage group or raise ValueError.

    Rejects unknown/unsupported combinations instead of guessing. N1mi with
    T2-T4 follows the N1 table entries. Distant metastatic disease is stage IV.
    """
    tcat, ncat, mcat = (_category(t, "T"), _category(n, "N"), _category(m, "M"))

    if mcat == "M1":
        stage = "IV"
    elif tcat == "TX" or ncat == "NX":
        raise ValueError("Anatomic stage cannot be assigned with TX or NX and M0")
    elif ncat == "N3":
        stage = "IIIC"
    else:
        effective_n = "N1" if ncat == "N1mi" and tcat in ("T2", "T3", "T4") else ncat
        groups = {
            ("Tis", "N0"): "0",
            ("T1", "N0"): "IA",
            ("T0", "N1mi"): "IB", ("T1", "N1mi"): "IB",
            ("T0", "N1"): "IIA", ("T1", "N1"): "IIA", ("T2", "N0"): "IIA",
            ("T2", "N1"): "IIB", ("T3", "N0"): "IIB",
            ("T0", "N2"): "IIIA", ("T1", "N2"): "IIIA",
            ("T2", "N2"): "IIIA", ("T3", "N1"): "IIIA", ("T3", "N2"): "IIIA",
            ("T4", "N0"): "IIIB", ("T4", "N1"): "IIIB", ("T4", "N2"): "IIIB",
        }
        stage = groups.get((tcat, effective_n))
        if stage is None:
            raise ValueError(f"No AJCC8 anatomic stage group for {tcat} {ncat} {mcat}")

    return {
        "t": tcat, "n": ncat, "m": mcat,
        "anatomic_stage": stage,
        "edition": "AJCC 8th edition",
        "prognostic_stage": "not calculated",
    }
