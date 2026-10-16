# The observation plane

Reviewed against `observation` at commit `2f4751f53678f2210930770605844cac766b1da4` (main on
2026-10-15); first written against `397c0b4`. Everything below describes the
later revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run of the module, or an
accepted decision. A decision is intent, not a result.

## What it is

Something has to stand between whoever states a fact about a running World
and whoever wants to look at it. A viewer may connect late and need to know
what holds now. It may be slow, or drop its connection and come back. None of
that should be able to slow the producer down, and none of it should be
mistaken for a change in the thing observed.

The observation plane (`observation:src/observation/plane.py::ObservationPlane`)
is a small in-memory object that does this for
[semantic observations](semantic-claim-model.md). It keeps the last
observation published for each subject, hands every new one to the consumers
that are listening, lets a consumer that reconnects catch up on a bounded
recent history, and tells a consumer explicitly when it cannot.

Every one of those four things is bounded, and the plane is explicit about
what falls outside the bound. That is the idea worth understanding: the plane
never blocks a producer and never silently pretends to completeness. When it
loses something for a consumer, it sends a rebase request, and what a consumer must
not do is read the loss as a fact about the source.

It lives in memory only. The code says: "This plane is not durable and cannot
resume across process restarts."

In production sensorimotor execution, World constructs an in-memory
`ObservationPlane` during bootstrap (`world:src/world/m1_profile.py`) and
publishes post-commit owner observation projections into it. Consumers read
the current plane snapshot through the bounded local read bridge
(`observation:src/observation/http_bridge.py::LocalObservationReadBridge`).

## Publishing

`publish` takes one observation and returns a number. Under one lock it:

1. increases the plane's counter by one and wraps the observation with that
   number as a `PlaneMessage`;
2. appends the message to the replay history, which holds a fixed number of
   most recent messages (2048 by default);
3. stores the message as the current one for its key, and evicts the oldest
   keys if more than the allowed number are held (4096 by default);
4. offers the message to each open stream.

Before publication changes any sequence or retained state, the plane validates
claim values as built-in scalar/container trees and deep-copies the
observation. Unsupported custom values and recursive containers fail before
publication side effects. Current views, replay/bootstrap and each live
subscriber receive detached snapshots. The source must still remain stable
while the initial copy is captured; the plane cannot synchronize an owner.

Publishing never waits for a consumer and returns nothing from one. The
module imports only the Python standard library and the claim model.

## The delivery sequence is not a clock

The number assigned at publication is the plane's **delivery sequence**. It
counts publications to this plane instance, across all families, starting
from one. It says in what order the plane received things. It does not say
when they held.

The code states it: "Delivery sequence is globally increasing within the
plane, not domain time." The sequence is carried on the message, outside the
observation, and the claim model refuses `delivery_sequence` as a kind of
domain time. The time at which a claim holds stays inside the observation,
in the terms of its own authority.

In an ad hoc run with eight threads publishing two thousand observations
each, the sixteen thousand sequence numbers were distinct and contiguous. No
test exercises concurrent use.

### Publication sequence, republication, and late delivery

Two delivery characteristics are verified by tests (`observation:tests/test_plane.py`):

1. **Republication is not deduplicated.** Publishing an identical observation
   twice delivers two distinct messages with incremented delivery sequence
   numbers (`test_identical_observation_republication_is_delivered_again`). The
   plane does not suppress repeated source publications.
2. **Arrival order governs delivery sequence.** If an observation for causal
   tick 2 is published and followed by one for causal tick 1, the plane delivers
   tick 2 as sequence 1 and tick 1 as sequence 2
   (`test_late_older_domain_time_is_delivered_in_publication_sequence`). The
   plane does not reorder messages into domain-time order.

## What current means

The plane keeps one message per key. The key
(`observation:src/observation/plane.py::observation_key`) is built from the
family's qualified name, the contract identifier and revision, the epistemic
kind, and the subject: its kind, its local key, and every identity and
participant with issuer, scope and lifetime.

So two observations replace one another only when all of that is equal. A
different contract revision, a different epistemic kind, or the same body
identity under a different scope or lifetime each keep their own entry
(`test_incompatible_semantic_revision_does_not_overwrite_materialization`,
`test_materialization_key_includes_contract_id_and_identity_scope_and_lifetime`,
`test_materialization_key_separates_epistemic_kinds`).

Three properties of this view are easy to get wrong.

**It is the last published, not the latest in time.** The key does not
include domain time, and replacement follows publication order. In an ad hoc
run, publishing an observation for causal tick 10 and then one for tick 3 of
the same subject left the tick 3 observation as current.

**It does not distinguish who said it.** Asserter, producer and acquisition
are not part of the key. In an ad hoc run, an observation with a different
asserter replaced the earlier one for the same subject.

**It is not a census.** When the limit is exceeded the least recently
published keys are dropped
(`test_current_view_is_a_bounded_subset_not_a_complete_subject_census`). The
code describes `current_messages` as returning "the currently retained
bounded subset, not a source census", and adds that an absent subject "does
not imply source absence, unavailability, or non-existence".

`current()` and `current_messages()` return whatever is held, optionally for
one family. The set carries no statement of how its members relate in time.

### Adversarial boundary guarantees: not a data lake

The plane is an ephemeral, bounded buffer. Boundary tests
(`observation:tests/test_observational_boundary_adversarial.py`) enforce three limits:

- **Snapshot isolation against consumer mutation:** A consumer modifying the
  `value` mapping inside a returned message does not alter the plane's
  retained snapshot (`test_mutating_read_projection_cannot_rewrite_plane_history`).
- **Explicit rebase on replay eviction:** When a consumer attempts to resume
  with a watermark that has been evicted from the bounded replay buffer, the
  plane does not truncate or invent history; it emits `PlaneRebaseRequired`
  with reason `replay_expired` (`test_bounded_replay_eviction_requires_rebase`).
- **Explicit clear signaling:** Invoking `clear()` resets retained state and
  emits `PlaneRebaseRequired` with reason `run_boundary`
  (`test_explicit_clear_rebases_stream_without_causal_context`).

The plane provides no durable storage, no cross-restart resumption, and no
cross-owner causal cut synchronization.

## Streams

A consumer opens a stream with `open_stream` and reads from a bounded queue
(512 entries by default). What it finds first depends on how it opened it.
The plane registers the stream and fills its queue under the same lock that
publication takes, so no message can fall between the two.

**With no watermark**, the stream starts with the current view, then
continues live. If the current view is larger than the queue, the plane does
not send part of it. It sends one rebase request
(`test_bootstrap_overflow_signals_rebase_instead_of_truncating_materialized_state`).

**With a watermark**, the last sequence the consumer has seen, the stream
starts with every retained message after it:

| Situation | What the stream starts with | Support |
|---|---|---|
| The watermark is still within the retained history | the messages after it, then live | ad hoc run |
| The watermark equals the latest sequence | nothing, then live | ad hoc run |
| Messages after the watermark have left the history | rebase, `replay_expired` | `test_expired_resume_requires_explicit_rebase` |
| The watermark is beyond the latest sequence | rebase, `future_watermark` | ad hoc run |
| The history is empty and the watermark is behind | rebase, `replay_unavailable` | ad hoc run |
| The messages to replay exceed the queue | rebase, `replay_exceeds_subscriber_bound` | ad hoc run |

A watermark must be a non-negative integer; a boolean, a fraction or a text
is refused (`test_stream_rejects_non_integer_resume_watermark`,
`test_stream_rejects_negative_resume_watermark`,
`test_stream_accepts_non_negative_integer_resume_watermark`).

A stream may be limited to one family. The sequence stays global, so a
filtered consumer sees gaps that are simply other families' messages. In an
ad hoc run a filtered stream received sequences 1 and 3 while 2 went to
another family. A consumer cannot detect a loss by looking for gaps; it can
only rely on the rebase signal. A family name that matches nothing is
accepted and yields an empty stream.

### When a consumer is too slow

If a stream's queue is full when a message arrives, the plane empties that
queue, puts a single rebase request in it with the reason
`consumer_overflow`, counts the event, and moves on to the next stream
(`test_stream_overflow_signals_rebase_instead_of_silent_loss`). The message
that found the queue full is not delivered to that stream. The stream stays
open, and in an ad hoc run the next publication was delivered to it normally.

### Rebase

A `PlaneRebaseRequired` carries a reason and the plane's latest sequence at
the moment it was issued. It means: what you hold may be incomplete; fetch
the current view and continue from this sequence. The code puts the
obligation on the reader: "consumers must rebase rather than infer
source-state absence". Fetching the current view may return messages the
consumer has already processed, and the code tells consumers to "deduplicate
by sequence".

The plane's own summary of the guarantee is: "Within one healthy
subscription, each sequence is delivered at most once."

## Clearing, and the run boundary

`clear` empties the current view and the replay history and sends every open
stream a rebase request with the reason `run_boundary`. It does not reset the
sequence counter. Since `observation@faa85b7` it also reserves one delivery
sequence for the boundary and remembers it
(`test_run_boundary_reaches_active_stream_and_reserves_delivery_watermark`).

That closes a gap recorded when this document was first written. A consumer
that was disconnected across a clear and came back with its last watermark
used to be given no sign that the view it held had been discarded. Now a
stream resumed with a watermark older than the last boundary receives a
rebase request with the reason `run_boundary`, even when new observations
have been published since, and after several clears an older watermark is
rebased at the latest boundary
(`test_late_resume_before_run_boundary_requires_rebase_even_with_new_history`,
`test_each_clear_advances_boundary_and_older_watermark_rebases_at_latest`).
A run of the module at that revision showed the counter standing at 3 after
two publications and a clear.

The boundary is kept in memory like everything else in the plane. The code
states that it is "not durable; a new process cannot recover it or resume
this plane".

## What it holds, and whose it is

The plane holds three things, all in the memory of one process: the counter,
the bounded history, and the bounded current view. A new plane starts its
counter again, so a watermark means something only to the plane instance
that issued it.

The counter and the bookkeeping belong to nobody but the plane. The
observations it holds are references to values whose meaning belongs to the
authority named in each claim. The plane decides how long it keeps a
reference. It decides nothing about the value.

A stream that is never closed stays registered. The plane visits every
registered stream on each publication.

## The plane and the decisions that govern it

These are statements of intent. They are set beside the code; conformance is
recorded in `registry/designs.yaml`.

[ADR-0078](../../technical/adr/ADR-0078-observation-is-causally-passive.md)
allows Observation to "read, project, transport, buffer, aggregate, visualize
and record", with "no authority to modify observed causal state". The plane
buffers and transports. It has no call into a producer and no reference to
one. It does hand the producer's own objects to consumers, uncopied.

The [Observation Architecture for Biopeia v1](../../technical/design/observation/observation-architecture-biopeia-v1.md)
decides that the live plane "belongs to Observation, not to Lab", and draws
authorities exposing their own boundaries, then "Observation adapters", then
the plane.

At this revision, Observation defines typed domain adapters in
`observation:src/observation/embodiment.py` and
`observation:src/observation/environment.py`. They adapt Embodiment BodyPose
(`embodiment.body_pose` v1), Embodiment reserve snapshots
(`biopeia.embodiment.reserve_state_snapshot` 1), Environment scalar fields
(`biopeia.environment.finite-scalar-field` 1), and Environment resource
snapshots (`biopeia.environment.resource_state_snapshot` 1). The adapters
validate structural shapes, units, reference frames, and owner checkpoint
digests without claiming authority or establishing World commit durability.

The same design says that the plane's delivery sequence "is not causal time
and must not be presented as such", and that a set of claims presented
together "declares its coherence scope". The plane keeps sequence and domain
time apart. Its current view declares no coherence scope.

It also says: "Bounded replay inside the plane serves consumers that
reconnect. It is not a record of what happened for scientific purposes." The
replay history is a fixed-length in-memory queue and nothing in the
repository writes it anywhere.

The [Observation Semantic Model v1](../../technical/design/observability/observation-semantic-model-v1.md)
asks any delivery contract to declare "its ordering scope, duplication
semantics, gap detection, completeness, and resume/replay capability". The
documentation of `open_stream` addresses each. The model also says that for
reliable streaming "the default target is at-least-once capability", and that
"Delivery loss is never reinterpreted as source-state absence." The plane
delivers at most once and signals loss; the gap described above is a case
where it does not signal.

[ADR-0101](../../technical/adr/ADR-0101-operator-control.md) keeps operator
control out of observation. The package contains no control path of any kind.

## The bounded local current read bridge

To allow local presentation viewers and development proxies to inspect the
latest committed observations without giving them active access or mutating
runtime state, the package provides a loopback HTTP bridge
(`observation:src/observation/http_bridge.py::LocalObservationReadBridge`,
`LocalObservationHTTPServer`).

### Wire protocol and endpoints

- **Route:** `GET /v1/current`. Rejects all query parameters with `404 not_found`
  and rejects any request carrying a body with `400 request_body_not_supported`.
  All non-GET methods (`HEAD`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`) are
  rejected with `405 method_not_allowed`.
- **Envelope declaration:** The endpoint responds with JSON conforming to
  `biopeia.observation.current.v1`. The response declares explicit boundaries:

  ```json
  {
    "schema": "biopeia.observation.current.v1",
    "availability": "available",
    "absence_semantics": "not_evidence_of_source_absence",
    "scope": "bounded_in_memory_current_subset",
    "freshness": "not_established_by_snapshot",
    "coherence": "per_message_only_no_cross_owner_snapshot_guarantee",
    "messages": [...]
  }
  ```

  If no approved observations are present in the plane, the bridge returns
  status `200` with `availability: "current_view_empty"`, reminding consumers
  that empty views are not evidence of source absence.

### Approved family validation

The bridge does not expose raw internal objects. It filters and validates
payloads against an explicit allowlist of approved M1 families:

1. `embodiment.body_pose` (contract `embodiment.body_pose`, revision `v1`):
   validates 3D position vector in meters, XYZW unit quaternion orientation
   conforming to right-handed Hamilton conventions, reference frame, body
   frame, causal tick under World authority, and parent lineage hash
   `embodiment_state_sha256`.
2. `environment.finite_scalar_field` (contract `biopeia.environment.finite-scalar-field`, revision `1`):
   validates dimensionless scalar value in range `[0.0, 1.0]`, sample point
   in meters, source and target ticks under World authority, and parent
   lineage hash `owner_checkpoint_sha256`.

Unapproved families are skipped silently. Any approved family with invalid
payload or corrupted envelope fails closed, emitting `503 current_view_unavailable`.

### Security and passivity guarantees

- **Loopback isolation:** The bridge binds strictly to loopback addresses
  (`127.0.0.1` / `::1`). Attempts to bind public or wildcard addresses fail.
- **Host and Origin enforcement:** The incoming `Host` header must exactly match
  the server's bound host and port (`127.0.0.1:<port>`), and the `Origin` header
  must match the authorized caller (`http://127.0.0.1:4173` by default). Mismatches
  return `400 invalid_host` or `403 origin_denied`.
- **Response byte limit:** Capped at 1,000,000 bytes (1 MB). If the encoded
  view exceeds this limit, the bridge returns `413 current_view_exceeds_response_limit`.
- **Security headers:** Every response sets `Cache-Control: no-store`,
  `X-Content-Type-Options: nosniff`, and `Connection: close`.
- **Non-mutating read:** Reading `plane.current_messages()` does not advance the
  plane's sequence counter or modify retained state (`observation:tests/test_http_bridge.py`).

## What supports this description

| Claim | Support |
|---|---|
| Bounded current view and live delivery; separation of entries by contract, revision, identity scope and lifetime, and epistemic kind; eviction; rebase on expired replay, on a bootstrap larger than the queue and on a slow consumer; validation of watermarks | Code and tests in `observation:tests/test_plane.py` (16 test cases, passing in an extraction of that revision) |
| Detached publication/current/replay/live snapshots; rejection of unsupported custom and recursive values before sequence changes; semantic-key behavior; bounded current/replay and explicit rebase cases | Code and tests in `observation:tests/test_plane.py` at the reviewed revision |
| No use of the plane outside its tests; no adapter | Text search of the main branches of the other repositories on the day of review |
| No persistence; standard-library imports only | Code reading |
| Passivity, ownership of the plane, replay not being evidence, delivery guarantees as intended | ADR-0078, ADR-0100, ADR-0101 and the two designs: intent, not results |

No test examined uses more than one thread. Nothing
here is evidence about cost: the plane was not measured.

## Open questions

- Whether current should mean last published or latest in domain time, and
  whether the asserter belongs in the key.
- Whether the accepted built-in value tree is broad enough for every future family adapter; richer domain values must be explicitly projected before publication.
- What publishes to the plane, and from which boundary of each authority.
- How, and whether, plane-origin conditions are meant to be attached to
  observations, given that losses are signalled by rebase.
