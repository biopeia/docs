#!/usr/bin/env python3
"""Reopen a closed local Observation archive read-only and verify its bounds."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from observation import ArchiveReader
from observation_v2_coverage import is_complete_closed_coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--page-size", type=int, default=4)
    args = parser.parse_args()
    output = args.output.resolve()
    db = output / "archive-dir/observations.sqlite"
    report = json.loads((output / "runtime-capture.json").read_text())
    before = hashlib.sha256(db.read_bytes()).hexdigest()
    if before != report["archive_sha256"]:
        raise RuntimeError("archive changed since capture closed")

    with ArchiveReader(db) as reader:
        integrity = reader.integrity_check()
        catalog = reader.capture_catalog()
        coverage_result = reader.capture_coverage(report["capture_id"])
        records = []
        page_sizes = []
        after_sequence = 0
        while True:
            page = reader.query_page(after_receipt_sequence=after_sequence, limit=args.page_size)
            if page.status not in {"results", "no_matching_publications"}:
                raise RuntimeError(f"unexpected query status: {page.status}")
            records.extend(page.records)
            page_sizes.append(len(page.records))
            if not page.has_more:
                break
            if not page.records or page.next_after_receipt_sequence <= after_sequence:
                raise RuntimeError("pagination failed to advance")
            after_sequence = page.next_after_receipt_sequence
        families = sorted({record.observation.family.qualified_name for record in records})
        filter_results = {}

        def read_filtered(filters):
            filtered = []
            cursor = 0
            while True:
                family_page = reader.query_page(
                    after_receipt_sequence=cursor,
                    filters=filters,
                    limit=args.page_size,
                )
                if family_page.status not in {"results", "no_matching_publications"}:
                    raise RuntimeError(f"unexpected exact-filter status: {family_page.status}")
                filtered.extend(family_page.records)
                if not family_page.has_more:
                    break
                if not family_page.records or family_page.next_after_receipt_sequence <= cursor:
                    raise RuntimeError("filtered pagination failed to advance")
                cursor = family_page.next_after_receipt_sequence
            return filtered

        # Select query values only from fields actually present in persisted
        # observations. This does not manufacture or infer identity metadata.
        filter_values = {
            "owner": records[0].observation.authority.value if records else None,
            "family": records[0].observation.family.qualified_name if records else None,
            "subject": records[0].observation.claim.subject if records else None,
            "revision": records[0].observation.family.contract.revision if records else None,
            "domain_time": next(
                (value for record in records for value in record.observation.domain_time), None
            ),
        }
        for name, value in filter_values.items():
            if value is None:
                filter_results[name] = {"status": "not_testable_identity_absent"}
                continue
            matching = read_filtered({name: value})
            filter_results[name] = {
                "status": "queried",
                "query_value": str(value),
                "record_count": len(matching),
                "receipt_sequences": [record.receipt_sequence for record in matching],
            }
        family_counts = {
            family: len(read_filtered({"family": family})) for family in families
        }
        unsupported = reader.query_page(filters={"run_id": report["run_id"]}, limit=10)

    after = hashlib.sha256(db.read_bytes()).hexdigest()
    coverage = coverage_result.coverage
    digest_valid = all(hashlib.sha256(record.original_payload).hexdigest() == record.content_sha256 for record in records)
    if integrity != "ok" or before != after or not digest_valid:
        raise RuntimeError("archive integrity, immutability, or payload digest check failed")
    if (
        catalog.status != "available"
        or not is_complete_closed_coverage(coverage)
    ):
        raise RuntimeError("capture is not complete with a verified closed interval")
    if unsupported.status != "unsupported_filter":
        raise RuntimeError("run_id must remain explicitly unsupported")

    result = {
        "verification": "separate-process-read-only-reopen-after-runtime-exit",
        "archive_sha256_before": before,
        "archive_sha256_after": after,
        "archive_unchanged": before == after,
        "integrity_check": integrity,
        "capture_status": catalog.sessions[0].status if catalog.sessions else None,
        "coverage_result_status": coverage_result.status,
        "coverage": {
            "status": coverage.status,
            "persisted_count": len(coverage.persisted_sequences),
            "received_not_persisted": list(coverage.received_not_persisted),
            "known_source_gaps": list(coverage.known_source_gaps),
            "unverifiable_intervals": list(coverage.unverifiable_intervals),
            "complete": coverage.complete,
            "closure_verified": coverage.closure_verified,
        },
        "record_count": len(records),
        "page_sizes": page_sizes,
        "receipt_sequences": [record.receipt_sequence for record in records],
        "source_sequences": [record.source_sequence for record in records],
        "payload_digests_valid": digest_valid,
        "exact_family_filter_counts": family_counts,
        "exact_filter_results": filter_results,
        "run_id_filter_status": unsupported.status,
        "run_id_filter_unsupported": list(unsupported.unsupported_filters),
        "limits": [
            "Capture receipt order is local order, not World causal order.",
            "Closure covers only the declared capture interval, not all producer publications.",
            "No World-cut join, browser history, shared access, or remote API is implied.",
        ],
    }
    (output / "read-only-reopen.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
