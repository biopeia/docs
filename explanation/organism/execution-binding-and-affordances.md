# Execution bindings, availability and the affordance resolver

Reviewed against `organism` at commit `637bc21a7e2a1aa9e0870f55f134e839657687f4` (main on
2026-10-16); first written against `3cc0f319`. Everything below describes the
later revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

Knowing a motor pattern and being able to use it with the body one has now
are kept apart in the Organism package. A competence record says that a
pattern was learned. A second record, the execution binding, says that the
competence was confirmed on one particular actuator surface, and whether that
confirmation still holds. A function combines the two into a set of yes-or-no
answers, and a resolver turns competences that pass into the affordances from
which [the action path](action-path.md) starts.

The registry of bindings calls itself "Bounded current-embodiment authority,
separate from competence knowledge." What it holds is a table with one row
per competence. It grants nothing: [the action path](action-path.md) shows
that a commitment and a command can be made without consulting it, and nothing
in the repository consults it (search of the seven repositories at
`origin/main`, 2026-10-09: the registry is constructed only in one test
module, the resolver nowhere).

The inputs are also missing. A binding is made for a competence record, and no
code constructs a competence record (see
[competence development](competence-development.md), finding F-0100).

## A binding

A binding (`organism:src/organism/actuation/binding.py::CompetenceExecutionBinding`)
is an immutable row: a competence identifier, a surface fingerprint, an effect
identifier, references to evidence, two numbers in the unit interval
(reliability and controllability), the tick of the last confirmation, a status
with an optional reason, two further ticks and a revision number. It must
carry at least one evidence reference; the refusal reads "execution binding
requires current factual evidence". The references are strings and are not
resolved against anything.

The status is one of three:

```text
VALID ◀──▶ STALE ──▶ INVALIDATED
  │                      ▲
  └──────────────────────┘
INVALIDATED ──(new evidence only)──▶ VALID
```

A stale binding carries one of four reasons (surface not current, embodiment
not current, controller unavailable, evidence aged); an invalidated one
carries one of three (causal relation revised, effect superseded, evidence
contradicted). The row refuses a status without the matching kind of reason
(`test_binding_status_invariants`).

## The registry

The registry
(`organism:src/organism/actuation/binding.py::CompetenceExecutionBindingRegistry`)
has two ways in.

- **Evidence.** A caller reports that a competence produced an effect on a
  surface. The row is created or replaced, its status becomes valid, and the
  new evidence references are appended to the old ones. The two numbers are
  whatever the caller passes, limited to the unit interval: values of 1.7 and
  -3 were stored as 1.0 and 0.0.
- **A status change.** A caller sets a status and reason. The revision number
  rises and the change is appended to a list of transitions for the caller to
  collect (`test_lifecycle_transitions_are_traced_and_evidence_revalidates`).
  A stale binding can be set valid again this way. An invalidated one cannot:
  the method's description says "Leaving INVALIDATED requires new evidence",
  and an attempt returned nothing and changed nothing.

To manage transitions across physical bodies and surfaces, `CompetenceExecutionBindingRegistry.mark_stale_for_surface`
(`organism:src/organism/actuation/binding.py:343-367`) checks all bindings against the active
`surface_fingerprint`. Any binding confirmed on a different surface is transitioned to
`STALE` with `StalenessReason.SURFACE_NOT_CURRENT`.

Bindings carry an explicit `applicability_fingerprint`. When `derive_availability`
(`organism:src/organism/agency/availability.py:87-119`) evaluates a binding against the
current embodiment context:

- If either the query or the binding lacks an applicability fingerprint, the scope is
  `PredictionScope.UNCERTAIN_CURRENT` and the reason is `AvailabilityReason.APPLICABILITY_UNKNOWN`.
  Missing current or stored context is treated as unknown, not proof of historical embodiment.
- If both fingerprints are present but do not match, the scope is `PredictionScope.HISTORICAL`
  and the reason is `AvailabilityReason.APPLICABILITY_MISMATCH`. Prior-body motor hypotheses are
  preserved as historical knowledge without allowing them to execute on an incompatible new body.

Furthermore, motor competence records are derived directly from causal evidence via
`organism:src/organism/actuation/derivation.py::derive_motor_competence_from_evidence`,
registering the competence in `CompetenceLibrary` and generating verified execution bindings.

## Four questions and their answers

The function
(`organism:src/organism/agency/availability.py::derive_availability`)
takes a competence, its binding or none, and four facts supplied by the
caller: whether the effect is known, the current surface fingerprint, whether
a controller is available and whether the competence is suppressed. Its module
calls the result "A projection, never an authority"; nothing is stored.

| Answer | True when |
|---|---|
| predictable now | the effect is known, the competence names an effect, and the binding is valid or stale |
| executable now | the binding is usable, its surface is the current one, the competence is established or robust, and a controller is available |
| admissible now | executable and not suppressed |
| testable now | predictable and executable |

Usable means valid, or stale for a reason that describes a condition the caller
has just supplied anyway (surface not current, controller unavailable). The
intent, in the code's words, is that executability "reads the condition
itself, so a status never lags it within a tick"
(`test_executability_reads_live_conditions_not_a_lagging_status`). A
prediction also gets a scope: current for a valid binding, historical for one
stale because the surface or embodiment is not current, uncertain otherwise
(`test_historical_knowledge_survives_a_non_current_surface`,
`test_uncertain_current_scope_and_invalidated_bindings`,
`test_suppressed_competence_stays_predictable_and_executable_but_not_admissible`).
One reason is reported, the first that applies of: not mature, unbound,
invalidated, stale, surface mismatch, controller unavailable, suppressed.

The suppressed flag is where the
[executive outcome ledger](executive-outcome-ledger.md) would come in; the
caller has to carry it across.

**The package answers the question of executability in two places that disagree.** The
registry has its own method, which requires a valid status. For a binding
marked stale because its surface was not current, presented with that same
surface as the current one, the registry's method answered no and the
function answered yes, with a prediction scope of historical. Confirmed by
running both on the same row. Neither calls the other.

## The resolver

The resolver
(`organism:src/organism/agency/affordances.py::AffordanceResolver`) is built
from a competence library, a prediction function, a controllability model, a
binding registry, an effect space with its matcher, a callback that says
whether a competence is executable, a surface fingerprint and an embodiment
identifier. It keeps no state of its own: "Affordances are derived — never
stored".

For each competence in the library it produces an affordance when all of the
following hold: the embodiment identifier in the query equals its own; the
callback says yes; the registry has a row for the competence; the prediction
function returns an effect that the effect space knows; and both the resolver
and the binding possess non-None applicability fingerprints that match
(`self._applicability_fingerprint is not None` and
`binding.applicability_fingerprint == self._applicability_fingerprint`).
If applicability is missing or differs, the resolver refuses to expose an
executable action (`organism:tests/source_unit/agency/test_affordance_resolver.py`).
The affordance takes

- its prediction confidence from the prediction;
- its controllability from the controllability model's estimate for that
  competence, effect and context, or, if there is none, from the binding;
- its executability confidence from the binding's reliability;
- its evidence references from the last eight of the binding's.

It offers two queries: everything currently afforded, and what is afforded
that matches a given effect. Results are ordered by controllability, then
prediction confidence, then executability confidence.

[The action path](action-path.md) notes that the resolver was not exercised.
For this document it was built once from real parts (a library with one
competence written by hand, an effect space, a ledger with eight transitions
and eight passive windows, the models of
[causal evidence and controllability](causal-evidence-and-controllability.md)
and a registry with one binding) and queried. It returned one affordance with
prediction confidence 1.0, controllability 1.0 from the model and
executability confidence 0.8 from the binding. For an unseen context the
prediction pooled contexts and, there being no estimate for that context, the
controllability was the binding's 0.3. A query with another embodiment
identifier returned nothing.

Three things the run made visible:

- **The resolver does not check the binding.** It reads the row's numbers and
  references and ignores its status and its surface. Whether a competence is
  executable is entirely the callback's answer. The resolver never calls the
  function of the previous section.
- **Its own surface fingerprint is unused.** It was built with a fingerprint
  that matched no binding and returned the affordance all the same. The value
  is stored and never read.
- **The embodiment identifier and the surface fingerprint are unrelated
  strings.** Nothing ties the identifier the resolver compares to the
  fingerprint a binding carries.

The module states what the resolver does not do: "The resolver never reads
actuators, never commits and never emits commands." That holds: it imports
nothing that could.

## Across a restart

The registry uses schema version 3. Its checkpoint includes rows, capacity,
execution counts, pressure counters, revision history, and ordered pending
lifecycle transitions. Restore refuses an earlier schema or missing required
fields (`test_binding_restore_rejects_old_schema_and_missing_current_fields`);
the pending transitions survive checkpoint/restore in order
(`test_all_pending_lifecycle_transitions_survive_checkpoint_restore`).

No checkpoint in the repository includes the export (search of
`organism:src/organism/checkpoint.py` and
`organism:src/organism/cognition/portable_checkpoint.py`, 2026-10-09; part of
finding F-0102). The competence library, which the resolver reads, has no
export at all. Availability and affordances are computed and never kept.

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A new registry is empty | Code |
| Checkpoint | Rows, counts, capacity, revision history and ordered pending transitions can be exported | Code and tests |
| Restart | Pending transitions survive in the registry export, but no composed Organism checkpoint carries that export | Code and tests; repository search |
| Re-embodiment | Nothing reacts. A row for another surface is reported not executable; no code marks it stale; new evidence on the new surface replaces it | Code and ad hoc run; no operation performs a re-embodiment |
| Reproduction | No operation exists | Search of the genetics code, 2026-10-10 |

## Beside the decision on body schema and competence

[ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md) is set
beside the code without a ruling on conformance.

| The decision says | The code at this revision |
|---|---|
| Distinguish learned knowledge from "active applicability of learned motor/sensor competence (validated against current Embodiment)". | Two records exist for the two things. Applicability is compared with a surface fingerprint string supplied by the caller; nothing in the package obtains it from an Embodiment. |
| "Competence may require reacclimation or become temporarily unusable while remaining learned Organism state." | A stale status with a reason, and a prediction scope of historical, express exactly this for one row. No code sets them. |
| "Re-embodiment may invalidate active commitments/calibration but must not silently erase longitudinal learning." | The competence record is untouched by anything here. The binding row for the earlier surface is overwritten by the first evidence on a new one, without a transition. |

[ADR-0095](../../technical/adr/ADR-0095-surviving-semantic-authorities.md)
assigns competence and agency to the Organism. The registry and the resolver
live in the Organism package and import nothing from another domain.

## Time

Every tick is an argument. The registry stores ticks as given and compares
none of them; the search for clocks is described under
[competence development](competence-development.md#time-and-determinism).

## Byte serialization for owner checkpoints

To participate cleanly in owner longitudinal checkpoints without external format leaks,
both the competence model and library provide self-contained byte codecs:

- `CompetenceEffectModel.to_bytes()` and `.from_bytes()` (`organism:src/organism/actuation/model.py`)
- `CompetenceLibrary.to_bytes()` and `.from_bytes()` (`organism:src/organism/actuation/competence.py`)

Both serializers use canonical sorted-key JSON and strictly reject duplicate JSON keys fail-closed
(`organism:tests/source_unit/actuation/test_competence_checkpoint.py`).

## What supports this description

| Claim | Support |
|---|---|
| The fields of a binding, its three statuses and their reasons | Code and tests in `organism:tests/source_unit/agency/test_competence_availability.py` |
| Transitions are recorded and evidence revalidates; restore refuses an earlier schema | Code and the same tests |
| Applicability fingerprint matching vs missing: UNCERTAIN_CURRENT on missing context, HISTORICAL on mismatch | Code and tests in `organism:tests/source_unit/agency/test_competence_availability.py` |
| Resolver requires matching applicability context to expose executable affordance | Code in `organism:src/organism/agency/affordances.py` and tests in `organism:tests/source_unit/agency/test_affordance_resolver.py` |
| Byte serialization of competence library and effect models with duplicate-key rejection | Code in `organism:src/organism/actuation/model.py` and `competence.py`, tests in `organism:tests/source_unit/actuation/test_competence_checkpoint.py` |
| Numbers are limited to the unit interval; an invalidated binding cannot be set valid; eviction order; the listing method changes nothing | Code and one ad hoc run of the module at that revision |
| One row per competence: a second surface replaces the first, keeps its evidence references, valid-from tick and revision, and records no transition | Code and the ad hoc run; no test |
| The four answers, the scope and the reason | Code and tests in `test_competence_availability.py` |
| The registry's and the function's answers on executability differ for a stale binding with a live reason | Code and the ad hoc run |
| Pending lifecycle transitions round-trip in order | Code and `test_all_pending_lifecycle_transitions_survive_checkpoint_restore` |
| What applicability and re-embodiment must respect | Accepted decision ADR-0104; a statement of intent |

## Open questions

- Which component reports evidence to the registry, decides that a binding is
  stale or invalid, and collects the transitions.
- Whether one row per competence is intended, given that a competence may have
  been confirmed on more than one body.
- Which of the two answers on executability is meant to stand, and whether the
  resolver should use it.
- What the resolver's embodiment identifier is, relative to a surface
  fingerprint and to the body string of the competence development engine.
