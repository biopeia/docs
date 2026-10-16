# Verification strategy v1: where tests, properties and proofs pay

**Scope:** documentary research and proposal. This report decides nothing,
changes no test suite, adds no CI gate and authorizes no refactoring. Each
proposal below needs the owning repository's agreement before it is carried
out, and cross-suite refactoring is out of scope while contracts are changing
concurrently (Organism checkpoint v5, World owner dependencies, Observation
V2).

Measured on 2026-10-16 at `organism@0ce7a031b6e9`, `world@d66ac6197c8e`,
`embodiment@8f9576a8cf5b`, `environment@4eb1f8c3393a`,
`observation@572c86f8fce6`, `lab@b47167a5b5e3` and `docs@172c1e6`. Counts come
from `git grep` over `origin/main` at those revisions; CI durations are medians
of the last successful `main` runs reported by the GitHub Actions API. Nothing
here is a measurement of scientific validity: a test is evidence about the
software contract it exercises and nothing more
([evidence status](../reference/evidence-status.md)).

## 1. What the suites look like

| Repository | `def test_` | Property-based (Hypothesis) | Tests named with a universal claim (`never`, `always`, `invariant`) | Median CI |
|---|---:|---:|---:|---:|
| organism | 921 | 0 | 23 | 21 s |
| world | 230 | 0 | 1 | 59 s |
| embodiment | 149 | 0 | 0 | 29 s |
| environment | 83 | 0 | 1 | 28 s |
| observation | 133 | 0 | 1 | 22 s |
| lab | 248 | 0 | 0 | 28 s |
| docs | 121 | 0 | 0 | 42 s (+178 s publication) |

No repository uses property-based testing or a formal tool. Execution cost
is not the problem: every CI run finishes in under a minute except the docs
publication build. What matters is **what the tests can and cannot show**,
and what it costs to maintain them.

## 2. Findings

### V-01. Universal claims are checked with a handful of examples

Twenty-three Organism tests are named for a property that holds for every
input. Four were inspected at `organism@0ce7a031b6e9`. Three exercise one to
seven inputs, and the fourth runs 1,024 ticks of a single configuration
(`test_exclusive_motor_groups_never_babble_antagonistic_channels_together`).
The other nineteen were not inspected:

- `test_extreme_inputs_never_produce_nan_or_inf` (`tests/source_unit/cognition/test_graph.py`)
  activates one graph with one input (`1e12`).
- `test_output_is_always_bounded_by_tanh` (`test_activation.py`) normalizes
  seven values.
- `test_oja_update_never_leaves_weight_range_under_repeated_extremes`
  (`test_learning.py`) repeats one positive extreme 2,000 times. It never tries
  negative or mixed signs, a negative learning rate, or non-finite values.

An ad hoc probe (not kept as a test) called `apply_oja_update`
(`src/organism/cognition/learning.py:98-119`) directly:

| Input | Result |
|---|---|
| 200,000 random finite inputs, activations in [−1, 1], rate in [0, 1], modulation in [−1, 1] | 0 range or finiteness violations |
| `learning_rate=nan`, `modulation=nan`, `source_activation=nan` or `target_activation=inf` | accepted; weight set to `2.0` |
| `learning_rate=-5.0` | accepted; weight set to `-2.0` |

The clamp `max(lo, min(hi, x))` maps NaN to the upper bound because
`min(2.0, nan)` returns `2.0`. The named property ("never leaves the weight
range") is true, and that is exactly what hides the defect: a non-finite
update saturates the weight silently instead of failing closed. The only
production caller, `compose_cognition_transition` (`src/organism/cognition/composition.py:200`),
receives its rate and modulation through `EdgeLearningInstruction`, which
rejects non-finite values and a negative rate, and its activations are
tanh-bounded. So the defect is reachable only by direct callers of the
primitive. It is **low severity**. It still matters as a demonstration: a
float strategy that includes non-finite values would reach these inputs, and
the existing example cannot. Recorded as finding F-0171.

**Proposal.** For these 23 tests and for the bounded numeric primitives they
cover, add Hypothesis properties beside the examples, not in place of them.
Generators should include non-finite values and boundary values. Whether a
primitive validates its own inputs or relies on its caller is Organism's
decision. The property should state whichever contract Organism chooses.
*Benefit:* high defect-finding power for low effort. Each property is a few
lines and replaces sampling that cannot cover the domain. *Cost:* S. Adds
`hypothesis` as a dev dependency.

### V-02. Codec round trips are example-based while digests depend on canonical bytes

Organism has 19 encode/decode/canonical functions in `src` and 65 tests named
for round trips or codecs. Commit identity in World, owner checkpoint
references and the v5 action history all rest on one property: an accepted
payload has exactly one byte encoding, `decode(encode(x)) == x`, and
`encode(decode(b)) == b` for every accepted `b`. Example tests show this for
the states they build. They cannot show that no other accepted byte string
decodes to the same state. If one could, a second encoding would pass every
digest check while naming a different object.

**Proposal.** Hypothesis round-trip and canonical-uniqueness properties for
the checkpoint codecs: build states from strategies and assert both
directions; mutate accepted bytes and assert rejection or a different digest.
*Benefit:* high. This is the property every durable digest relies on.
*Cost:* M. Strategies for nested states take work. *Timing:* after Organism
checkpoint v5 settles (organism#183).

### V-03. The commit and recovery protocol is a finite state machine tested at chosen points

World states a universal guarantee: a process that stops at any point of a
transition leaves either the previous committed cut or an explicit
`RECOVERY_REQUIRED`, never a silently advanced cut
(`TransitionCommitState`, `ManifestStatus` in `src/world/durable_runtime.py`).
Fourteen tests inject termination, partial-write or fsync failures at
selected points, and 27 tests exercise recovery. They are well chosen. But the
guarantee covers every write, flush and rename call site crossed with every
manifest state, and finite selection cannot show that coverage. Since
`world 9f65707` changed the journal to append-only deltas, the set of crash
points the tests name no longer matches the set the documentation described
(finding F-0169).

**Proposal, in two steps.**

1. **Systematic crash-point enumeration (engineering, M).** Wrap each
   filesystem effect on the commit path (write, `fsync`, rename, directory
   `fsync`) so that a test can terminate at the *n*-th effect for every *n*.
   Then assert the guarantee after each termination. This replaces the
   hand-picked points with all of them, and it fails when a new call site is
   added without coverage.
2. **A small formal model (formal, M).** Write a model in Lean 4 or TLA+ of
   the abstract protocol only: manifest states, journal prefix and digest,
   pending and committed cut, recovery. State the safety property and prove
   it, or model-check it, over every interleaving of crash and recovery. This
   is the one place in Biopeia where a proof replaces repetitive verification:
   the state space is finite but combinatorial, and the property is exactly
   one the tests sample. The model verifies the design, not the Python code.
   The gap between them is closed by step 1: the enumerated crash traces from
   the code are checked against the model's transition relation, so the
   comparison is differential.

*Benefit:* high. The recovery guarantee is constitutional in weight (ADR-0083,
ADR-0093) and its failure modes are rare in sampling. *Owner:* World.
*Timing:* after world#90/#173–#177 settle.

### V-04. Lab's suite is mostly change-detector tests over migration records

Of Lab's 154 test files, 142 (6,056 lines) assert the literal content of rows
in `migration/*.tsv` and headings in `MIGRATION.md`. A typical one
(`tests/unit/test_migration_body_pose_disposition.py`) finds one inventory row
and asserts the exact strings of six of its fields. Each new disposition adds
a file, and changes in the record count force reconciliation commits (for
example `lab e0746c4`, "reconcile disposition count for #169"). These tests
protect against accidental edits, but they do it by restating the data.
Whole-table invariants already exist in places:
`tests/unit/test_study_disposition_consistency.py` requires every one of the
477 custody rows to carry one of two review statuses, and both contain
`NOT_ADMITTED`. A scan of all twelve `migration/*.tsv` files at `lab@b583717a51ab`
found `admitted` only in negated prose ("not ... admitted", "Do not treat ...
as admitted"). Other tables, such as the study disposition register, are
checked row by row.

**Proposal.** Generalize that existing consistency test into one record
validator, as `docs/tools/validate_registry.py` does for the documentation
registry, and retire the per-row literal restatements it makes redundant. The
validator would check closed vocabularies for each disposition and custody
column, referential integrity across the TSVs, and the non-claim invariants
**over every row of every table**, extending what the test already does for
custody. Examples: every `SCIENTIFIC_EVIDENCE` custody row is also
`NOT_ADMITTED`, unless an admission record names it; every `DEFER` and
`HISTORICAL_PROTOCOL` row cites an owner decision; no row is `ADMITTED`
without one. Per-row tests are kept only where a row carries an owner
decision that must never change silently. *Benefit:* high maintenance saving,
and stronger guarantees on the invariant that matters scientifically,
non-admission. *Cost:* M. *Timing:* only after the active disposition series
(lab#169–#177, PR #518) closes; doing it during that series would collide with
it.

### V-05. Documentation citations are reported, not enforced

The docs cross-repository job resolves code references but only *reports*
tests that are cited and not found. It does not check that a document's
declared review revision exists. A nonexistent SHA,
`environment@d09e45c47fe8…`, stood in six headers until it was found by hand
(F-0170, docs#209). Two explanations cited tests that never existed, one of
them in support of a "bit-identical" continuation claim.

**Proposal.** In the cross-repository job, block when (a) a header's review
SHA does not resolve in the named repository, or (b) a cited test is absent
**at the document's declared review revision**. Keep reporting when a test is
absent only at the current head, which is ordinary staleness. *Benefit:* high
integrity gain at low cost. Every case found on 2026-10-16 would have been
caught. *Cost:* S. *Coordination:* `tools/validate_registry.py` is being
extended by the Diátaxis work in progress (ADR-0114). Raise this there rather
than in a parallel change.

### V-06. Differential testing already has a precedent

`organism:tests/source_unit/actuation/test_action_history_prototype.py`
compares the compact v5 action history with the behaviour it replaces. The
same shape fits every incremental-versus-full computation in the codebase:
incremental journal prefix verification in World against full recomputation
(`world 9b2011f`), incremental history validation in Organism against full
validation, and owner checkpoint closure. As Hypothesis stateful tests
(`RuleBasedStateMachine`), these become generated operation sequences rather
than fixed ones. *Benefit:* medium to high. These are exactly the
optimizations that introduce rare divergences. *Cost:* S–M each.

### V-07. Integration evidence is tied to pins that trail the heads

World's and Lab's integration fixtures run at pinned revisions of the other
repositories, and those pins trail the heads (F-0164, F-0165). This is
declared and deliberate: a pin is the revision the evidence is about.
Whether two heads work together is not checked anywhere until the pin moves.
**Proposal.** A scheduled, non-blocking job runs the integration suites with
all repositories at their heads and publishes the result. Nothing gates on it.
*Benefit:* medium. It gives early warning without changing what a pin means.
*Cost:* S.

### V-08. Keep engineering tests from making scientific claims

`organism b674450` (#174) is a model to follow. It renamed
`test_a_predictor_measurably_learns_a_periodic_signal_over_many_ticks` to
`test_alternating_signal_oja_loop_does_not_beat_zero_output_baseline`,
compared against zero-output and persistence baselines, and stated in a
comment that the loop "is not evidence of predictive learning". A test name
that asserts a capability gets quoted as evidence for it (finding F-0071).
**Proposal**, a convention and not a gate: name a test for the behaviour it
checks, and compare against a trivial baseline whenever a test computes a
loss or a score. Leave capability claims to Lab protocols, with their
controls and admission rules.

## 3. Where formal verification does and does not pay

| Candidate | Formal tool worth it? | Why |
|---|---|---|
| World commit/recovery protocol (V-03) | **Yes**: Lean 4 or TLA+ model of the abstract protocol, tied to the code by enumerated traces | Finite, combinatorial state space; universal safety property; failures rare under sampling |
| Canonical encoding uniqueness (V-02) | Not yet; property-based first | The property is checkable by generation. A proof needs a formal model of the serializer, and that is costly to keep in sync while schemas change |
| Bounded numeric primitives (V-01) | No | Clamping lemmas are trivial; what fails is the floating-point edge (NaN), which generation finds and a real-number proof would miss |
| Cognition, plasticity, physics | No | Their questions are empirical or numerical. Formal proofs would verify an idealization, not the behaviour Lab must measure |
| Lab record invariants (V-04) | No | A validator over finite data is already a complete check |

Do not translate tests into proofs wholesale. The proof proposed here
replaces sampled checks of one protocol whose correctness everything else
depends on.

## 4. Order of work

| # | Item | Owner | Benefit | Cost | Can start |
|---|---|---|---|---|---|
| 1 | V-05: block on unresolved review SHAs and on citations absent at the declared revision | Docs | High | S | With the ADR-0114 tooling work |
| 2 | V-01: Hypothesis properties for the 23 universal-claim tests | Organism | High | S | Now; independent of the checkpoint work |
| 3 | V-06: stateful differential tests for incremental validators | Organism, World | Medium–high | S–M | After organism#183 / world#90 merge |
| 4 | V-03 (1): exhaustive crash-point enumeration | World | High | M | After world#90 settles |
| 5 | V-03 (2): formal model of commit/recovery | World, reviewed by the Architecture Owner | High | M | After item 4 |
| 6 | V-02: codec round-trip and canonical-uniqueness properties | Organism | High | M | After checkpoint v5 settles |
| 7 | V-04: Lab record validator replacing per-row tests | Lab | High (maintenance) | M | After the disposition series closes |
| 8 | V-07: scheduled heads integration run | World, Lab | Medium | S | Now |

The estimates are relative (S = hours, M = a few days for one agent). They
are not commitments, and they do not count review.

## 5. Limits of this report

The counts are name-based: a test called `test_*_never_*` that checks a full
domain would be miscounted, and a universal property under another name is
missed. The Oja probe is an ad hoc run against an extracted copy of
`organism@0ce7a031b6e9`. It is not kept as a test, and its result describes
that revision only. No test suite was modified, and no claim is made about
the scientific adequacy of any mechanism.
