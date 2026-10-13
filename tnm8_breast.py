#!/usr/bin/env python3
"""
AJCC 8th Ed. Breast Cancer Stage Calculator
Provides anatomic stage CLI plus a backward-compatible, NON-CLINICAL legacy score.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT
"""

import argparse
import csv
import json
import os
import re
import sys
from typing import Dict, Any


def _validate_input_path(filepath: str) -> str:
    """Validate input file path to prevent path traversal."""
    # Check for path traversal attempts before normalization
    parts = filepath.replace("\\", "/").split("/")
    if ".." in parts:
        raise ValueError(f"Invalid file path: path traversal detected in '{filepath}'")
    normalized = os.path.normpath(os.path.abspath(filepath))
    return normalized


def calculate_metrics(**kwargs) -> Dict[str, Any]:
    """
    Deprecated numeric demonstration only, NOT an AJCC8 staging calculation.
    Use staging.anatomic_stage(t, n, m) for anatomic stage grouping.
    """
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            try:
                params[k] = float(v)
            except (ValueError, TypeError):
                # Sanitize string inputs - strip control characters
                cleaned = re.sub(r'[\x00-\x1f\x7f]', '', str(v))
                params[k] = cleaned

    # Deterministic domain logic
    numeric_vals = [val for val in params.values() if isinstance(val, (int, float))]
    primary_val = numeric_vals[0] if numeric_vals else 1.0

    score = primary_val
    for idx, nv in enumerate(numeric_vals[1:], start=2):
        score += nv * (1.0 / idx)

    rounded_score = round(score, 2)

    # Classification / tiering
    if rounded_score < 10.0:
        tier = "Low / Standard"
        action = "Legacy numerical tier; no clinical recommendation"
    elif rounded_score < 25.0:
        tier = "Moderate / Intermediate"
        action = "Legacy numerical tier; no clinical recommendation"
    else:
        tier = "High / Severe"
        action = "Legacy numerical tier; no clinical recommendation"

    return {
        "tool": "legacy-nonclinical-composite",
        "is_clinical_stage": False,
        "score": rounded_score,
        "classification": tier,
        "clinical_recommendation": action,
        "inputs_evaluated": len(params),
    }


def process_single(args) -> None:
    kwargs = vars(args)
    kwargs.pop("func", None)
    res = calculate_metrics(**kwargs)
    print(json.dumps(res, indent=2))


def process_batch(input_csv: str, output_csv: str) -> None:
    # Validate input path for security
    safe_input = _validate_input_path(input_csv)
    safe_output = _validate_input_path(output_csv)

    with open(safe_input, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    out_fields = fieldnames + ["score", "classification", "clinical_recommendation"]
    out_rows = []

    for r in rows:
        calc_res = calculate_metrics(**r)
        row_dict = dict(r)
        row_dict["score"] = calc_res["score"]
        row_dict["classification"] = calc_res["classification"]
        row_dict["clinical_recommendation"] = calc_res["clinical_recommendation"]
        out_rows.append(row_dict)

    with open(safe_output, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {safe_output}")


def process_stage(args) -> None:
    from staging import anatomic_stage
    print(json.dumps(anatomic_stage(args.t, args.n, args.m), indent=2))


def process_stage_batch(input_csv: str, output_csv: str) -> None:
    from staging import anatomic_stage
    with open(_validate_input_path(input_csv), newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        if not {"T", "N", "M"}.issubset(fieldnames):
            raise ValueError("CSV must contain T,N,M columns")
        rows = []
        for index, row in enumerate(reader, start=2):
            try:
                result = anatomic_stage(row["T"], row["N"], row["M"])
            except ValueError as exc:
                raise ValueError(f"CSV line {index}: {exc}") from exc
            rows.append({**row, "anatomic_stage": result["anatomic_stage"]})
    with open(_validate_input_path(output_csv), "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*fieldnames, "anatomic_stage"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Staged {len(rows)} records -> {output_csv}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="AJCC 8th Ed. Breast Cancer Stage Calculator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    stage_parser = subparsers.add_parser("stage", help="AJCC8 ANATOMIC stage (not prognostic)")
    stage_parser.add_argument("--t", required=True, help="Primary tumor category, e.g. T2")
    stage_parser.add_argument("--n", required=True, help="Regional nodal category, e.g. N1mi")
    stage_parser.add_argument("--m", required=True, help="Distant metastasis, M0 or M1")
    stage_parser.set_defaults(func=process_stage)

    stages_parser = subparsers.add_parser("stage-batch", help="Anatomic staging of CSV T,N,M records")
    stages_parser.add_argument("-i", "--input", required=True)
    stages_parser.add_argument("-o", "--output", default="staged.csv")
    stages_parser.set_defaults(func=lambda args: process_stage_batch(args.input, args.output))

    # Single parser
    single_parser = subparsers.add_parser("single", help="Legacy nonclinical numeric demo (NOT AJCC staging)")
    single_parser.add_argument("--v1", type=float, default=10.0, help="Primary parameter")
    single_parser.add_argument("--v2", type=float, default=5.0, help="Secondary parameter")
    single_parser.add_argument("--v3", type=float, default=2.0, help="Tertiary parameter")
    single_parser.set_defaults(func=process_single)

    # Batch parser
    batch_parser = subparsers.add_parser("batch", help="Legacy nonclinical numeric demo CSV")
    batch_parser.add_argument("-i", "--input", required=True, help="Input CSV file path")
    batch_parser.add_argument("-o", "--output", default="results.csv", help="Output CSV file path")
    batch_parser.set_defaults(func=lambda args: process_batch(args.input, args.output))

    args = parser.parse_args(argv)
    if args.command in ("single", "batch"):
        print("WARNING: legacy numeric scoring is NOT an AJCC breast stage.", file=sys.stderr)
    args.func(args)


if __name__ == "__main__":
    main()
