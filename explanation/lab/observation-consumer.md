# The Lab observation consumer

Reviewed against `lab` at commit `e7bb66c44517e279ca3180d929377682e251d796`
(main on 2026-10-16). Statements are marked by what supports them: the code,
the tests, or an accepted decision.

## What it is

Lab observes simulation phenomena only through the passive Observation plane.
The observation consumer (`lab:src/lab/observation_consumer.py`) provides the
association layer between Lab's scientific study execution context and the
volatile messages emitted by Observation.

It adds no producer, persistence, transport, authorization, or
evidence-admission behaviour. It reads what Observation retained, checks
whether each message belongs to an exact committed World cut, and labels the
result.

## The execution association

A read requires a `LabObservationAssociation`:

- `experiment_id` and `run_id`: Lab-owned execution identifiers.
- `world_id`, `causal_tick`, and `commit_id`: the World cut coordinates.

The constructor `LabObservationAssociation.for_committed_cut` derives this
association directly from a World-issued `CommittedWorldCut` receipt.

## Association rules

When evaluating messages from `current_messages` or an active stream
subscription, `_context_matches` (lines 87-142) enforces five invariants:

1. The association coordinates (`world_id`, `causal_tick`, `commit_id`) match
   the cut exactly.
2. The observation claim's `authority` matches the observation family's
   declared authority.
3. The observation's lineage parents reference exactly one owner checkpoint
   SHA-256 matching that authority in the cut's `owner_checkpoint_references`.
4. The observation's `context_time` contains a `world_target_causal_tick` or
   `world_causal_tick` equal to the cut's causal tick.
5. The lineage transformation's effective configuration contains the matching
   `world_id`.

## Reading modes

### Current messages (`associate_current_messages`)

Queries `ObservationPlane.current_messages(family=family)`.

- If one or more messages match, returns status `ASSOCIATED`.
- If no messages match, returns status `UNASSOCIATED` with reason
  `"no matching message in current volatile view; not source absence"`.

The view is bounded and volatile. An unassociated read is **not** evidence that
the source was absent or that the observation failed.

### Stream messages (`associate_stream_messages`)

Drains up to `max_messages` (default 512) from an `ObservationPlane`
subscription queue. The caller manages the subscription lifecycle.

The consumer requires the caller to rebase (`REBASE_REQUIRED`) whenever:

- A stream item reports an explicit rebase reason (`item.reason` and
  `item.sequence`).
- An item sequence is duplicate, out of order, or non-increasing
  (`sequence <= previous_sequence`).
- The queue is not empty after draining `max_messages`
  (`"consumer_batch_limit_exceeded"`). A truncated prefix is never silently
  treated as a complete batch.

## What supports this description

| Claim | Support |
|---|---|
| Association matching, validation, and rebase rules | Code and tests in `lab:tests/unit/test_observation_consumer.py` |
| End-to-end integration with World commit and ObservationPlane | Integration tests in `lab:tests/observation_integration/test_lab_observation_publication.py` |
| Consumption of owner projections from production World causal cycle | Integration tests in `lab:tests/observation_integration/test_lab_production_world_cycle.py`, at Lab's pinned World revision; at the heads of 2026-10-16 it fails (finding F-0173) |
| Architectural role of Lab and passivity of observation | Accepted decisions ADR-0078, ADR-0100, ADR-0102 |
