from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).parents[1] / "how-to/operator/observation-v2-reopen.py"
SPEC = spec_from_file_location("observation_v2_reopen", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_reopen_acceptance_requires_complete_closed_coverage():
    coverage = SimpleNamespace(
        status="closed_verified", complete=True, closure_verified=True
    )

    assert MODULE.is_complete_closed_coverage(coverage)


def test_reopen_rejects_closed_capture_with_persisted_loss_or_gaps():
    # Closure verification only means all observed source sequences are
    # accounted for; it does not mean the capture contains no loss or gaps.
    for status in ("closed_verified_with_persisted_loss", "closed_verified_with_gaps"):
        coverage = SimpleNamespace(
            status=status, complete=False, closure_verified=True
        )
        assert not MODULE.is_complete_closed_coverage(coverage)


def test_reopen_rejects_unverified_or_missing_coverage():
    assert not MODULE.is_complete_closed_coverage(None)
    assert not MODULE.is_complete_closed_coverage(
        SimpleNamespace(status="active", complete=False, closure_verified=False)
    )
