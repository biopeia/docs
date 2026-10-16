import sys
from pathlib import Path
from types import SimpleNamespace


OPERATOR_DIR = Path(__file__).parents[1] / "how-to/operator"
sys.path.insert(0, str(OPERATOR_DIR))
from observation_v2_coverage import is_complete_closed_coverage

sys.path.pop(0)


def test_reopen_acceptance_requires_complete_closed_coverage():
    coverage = SimpleNamespace(
        status="closed_verified", complete=True, closure_verified=True
    )

    assert is_complete_closed_coverage(coverage)


def test_reopen_rejects_closed_capture_with_persisted_loss_or_gaps():
    # Closure verification only means all observed source sequences are
    # accounted for; it does not mean the capture contains no loss or gaps.
    for status in ("closed_verified_with_persisted_loss", "closed_verified_with_gaps"):
        coverage = SimpleNamespace(
            status=status, complete=False, closure_verified=True
        )
        assert not is_complete_closed_coverage(coverage)


def test_reopen_rejects_unverified_or_missing_coverage():
    assert not is_complete_closed_coverage(None)
    assert not is_complete_closed_coverage(
        SimpleNamespace(status="active", complete=False, closure_verified=False)
    )
