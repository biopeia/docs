# The in-memory World runtime

Reviewed against `world` at commit `e423a04a113e6015a7eca0986d303129eebaceaa`.
Everything below describes that revision.

## What it is

The simplest thing in the repository that can be called a World: an
identity, one presence, a tick counter and a
[causal journal](causal-journal.md), all in memory
(`world:src/world/runtime.py::WorldRuntime`). It exists to show the shape of a
causal tick without any persistence. The
[durable runtime](durable-runtime.md) is the one that makes a tick survive
the process; this one does not, and says so.

The same module defines the two identities the rest of World uses:
`WorldId`, the canonical identifier of a World, and `PresenceId`, the
identity of a presence, which the code keeps "distinct from any semantic
owner identity". Both refuse an empty value
(`test_invalid_world_and_presence_ids_are_rejected`).

## What a tick does

The caller supplies a transition: a function that receives the number of the
tick being attempted and may return a JSON object. The runtime runs it, and
only if it returns does it append one record to the journal and advance the
counter. The object returned, if any, is carried inside the record without
interpretation
(`test_successful_ticks_publish_one_record_after_transition_in_tick_order`,
`test_transition_json_payload_is_included_opaquely_in_committed_record`).

The counter starts at zero and counts committed transitions, so the first
record carries tick one.

Only one tick runs at a time. A call made while another is running, from
another thread or from inside the transition itself, fails immediately, does
not run its transition, and leaves the runtime as it was
(`test_concurrent_tick_fails_fast_without_starting_or_poisoning_runtime`,
`test_reentrant_tick_fails_fast_without_preventing_outer_commit`).

## When a tick fails

If the transition raises, returns something that is not a JSON object, or the
record cannot be appended, the runtime remembers the failed tick and the
error, and refuses every later tick
(`test_transition_failure_requires_recovery_and_publishes_no_failed_record`,
`test_invalid_transition_payload_fails_closed_without_publishing_record`). A
`KeyboardInterrupt` from the callback is handled the same way: the proposed tick
is recorded as failed, the runtime becomes recovery-required, and the interrupt
is re-raised. This closes the runtime against reuse after a callback may have
partially changed owner state. No record is published for the failed tick. The regression test in
`world:tests/test_runtime.py` checks that the interrupt is re-raised, no record
is published, and a later tick is refused.

Two limits, both stated by the module itself:

- The transition runs before publication and is opaque. If it changed
  anything before failing, that change stays; the runtime rolls nothing back.
- The refusal lives in memory. There is no call that recovers this runtime,
  and a new process starts clean. The module describes this as "not durable
  recovery" that "does not by itself satisfy the TARGET post-failure
  contract".

## What supports this description

Code and the tests in `world:tests/test_runtime.py`, named above. The
integration test `world:tests/integration/test_first_biopeia_causal_tick.py`
uses this runtime with an Organism, an Embodiment and passive Observation;
its own description limits it to "a bounded discrete causal path" and
disclaims solver integration and durable recovery.
