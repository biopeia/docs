"""Small, dependency-free checks for local Observation capture coverage."""


def is_complete_closed_coverage(coverage: object) -> bool:
    """Require accounted closure and no recorded loss or gap."""
    return bool(
        coverage is not None
        and getattr(coverage, "status", None) == "closed_verified"
        and getattr(coverage, "complete", False)
        and getattr(coverage, "closure_verified", False)
    )
