# How a repeated motor pattern becomes a competence

Reviewed against `organism` at commit `2f051b029018a30f10acddaedc70d2b7edd3325c`; first written against `6543188`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or an accepted decision.

## What it is

The Organism package contains one class that turns a stream of numbers into a
list of named motor patterns. At every tick it is told what the body's signals
were and which activations were delivered on which channels. It answers with
the activations it proposes next. Over time it keeps statistics about short
patterns of activation that recurred and were followed by a similar change in
the body's signals, and it marks some of those patterns as usable.

The code calls such a pattern a motor primitive and, once it passes a gate, a
competence. Those are names of records. What is kept is a four-step sequence
of quantised activations and a few running statistics about it. Nothing
reviewed here shows that an Organism can do anything with a body; the class
has never been run against one in this repository, and no code in any Biopeia
repository constructs it outside its own tests (search of the seven
repositories at their `origin/main`, 2026-10-09).

The class is `organism:src/organism/actuation/sensorimotor.py::CompetenceDevelopmentEngine`.
It says of itself: "It never authorizes physical action: ActionDomain
is the sole owner of commitments and MotorCommands." No `ActionDomain` exists
in the repository (already recorded as finding F-0038), so the engine's
proposals are values that a caller may or may not turn into commands along
[the action path](action-path.md).

## The loop it expects

```text
caller: observe(tick, body signals, activations delivered last tick)
engine: update statistics
caller: motor_intents(tick)
engine: activations it proposes for this tick
```

The engine holds no reference to a body, a surface or a clock. The tick, the
signals and the delivered activations are all handed in. Body signals are a
mapping from an opaque name to a number; the engine never interprets the
names.

## Where the activations come from

Unless a learned pattern is being replayed, the proposed activations come from
what the code calls exploration. It is not random. Time is cut into bouts of
24 ticks. For each bout the engine picks a set of channels and a target level
for each, between 0.15 and 0.85, and moves each channel's level toward its
target by a fixed fraction per tick. Which channels, how many and which levels
are all derived from SHA-256 digests of the organism identifier, the channel
identifier and the bout number. Channels used least so far are preferred.

Two consequences, confirmed by running the class: two engines built with the
same organism identifier and the same channels produced identical activations
for 600 ticks, and an engine with another identifier produced different ones.
The package imports no clock and no random number generator (see
[Time and determinism](#time-and-determinism)).

How many channels are driven at once is drawn on a logarithmic scale, so that
small sets are common and large sets remain possible
(`test_default_exploration_prefers_low_dimensional_coordination_without_forbidding_broad_patterns`,
`test_exploration_covers_all_actuators_without_single_channel_monopoly`,
`test_exploration_holds_channel_set_within_short_epoch`). A caller may declare
groups of channels that must never be driven together; within a group one
channel is chosen per bout
(`test_exclusive_motor_groups_never_babble_antagonistic_channels_together`).

An optional second mode, off by default, replaces a share of the bouts by
probing: one channel is pulsed during two windows of six ticks and nothing at
all is proposed for the other twelve ticks of the bout. With the share set to
one, an ad hoc run of 240 ticks gave 120 ticks with no activation and never
more than one channel at a time
(`test_probing_is_off_by_default_and_exploration_is_unchanged`,
`test_probing_epoch_pulses_one_channel_with_quiet_windows`,
`test_probed_unit_repeats_for_several_epochs_then_moves_on`).

## From activations to a candidate

Each delivered activation is quantised to one of eight levels; values below
0.08 count as absent. Four consecutive ticks of non-empty quantised
activations form a candidate sequence. The effect attributed to it is one
number: the mean absolute change, over the four ticks, of the eight body
signals that changed most. The code explains the choice in a comment: a
top-eight statistic gives local and distributed actions the same opportunity,
where an average over all signals would favour body-wide motion
(`test_body_delta_does_not_reward_global_motion_over_strong_local_effect`).

Three things are subtracted or filtered before the number is counted.

- **Change that happens anyway.** When four consecutive ticks carried no
  activation, the same statistic is recorded as a passive baseline, and its
  running mean is subtracted from every later effect
  (`test_passive_drift_is_subtracted_from_motor_controllability`). Without
  probing, exploration seldom leaves four silent ticks: in the 600-tick run
  the baseline had no samples at all, so nothing was subtracted.
- **Overlap.** A sequence is counted again only if it ends at least four ticks
  after its previous count and falls in a different block of eight ticks
  (`test_adjacent_windows_from_same_exploration_block_do_not_count_as_recurrence`,
  `test_same_sequence_in_disjoint_exploration_block_counts_as_recurrence`).
- **Near duplicates.** A new sequence within a distance of 0.10 of a known one
  is counted as that one
  (`test_similar_natural_chunks_count_as_recurrence_not_new_skill`).

A sequence seen once is kept as statistics only. The code says: "One episode
is a hypothesis, not a learned motor primitive."
(`test_single_episode_remains_candidate_until_independent_recurrence`).

## From a candidate to a primitive, and the gate

From the second count on, three numbers are computed for a sequence:

```text
reproducibility         = 1 / (1 + 25 * variance of the effect)
directional consistency = mean over signals of |mean change| / (|mean change| + its standard deviation)
controllability         = mean effect * reproducibility * directional consistency
```

If controllability exceeds 0.002 the sequence becomes a motor primitive: a
record holding the sequence, the sample count and those numbers. If a later
count brings it back under 0.002 the primitive is removed again
(`test_inconsistent_repetition_retracts_false_motor_primitive`).

Controllability here is therefore an effect size times two consistency
measures. It is in the units of the body signals, and so is the threshold. A
different quantity under the same name, a difference of rates, is described
under [causal evidence and controllability](causal-evidence-and-controllability.md).

Whether a primitive counts as usable is read from a maturity label, computed
each time from its numbers and never stored
(`organism:src/organism/actuation/competence.py::CompetenceEvidence`: "Evidence
projection only; no separately mutable maturity truth."):

| Label | Condition |
|---|---|
| candidate | fewer than 2 samples, or controllability of zero |
| emerging | at least 2 samples and positive controllability, but one of the next conditions fails |
| established | samples at least the gate's minimum (2 by default), controllability above 0.002, reproducibility at least two thirds, directional consistency at least the gate's minimum (0.60 by default) |
| robust | established, with at least 8 samples, reproducibility at least 0.85, directional consistency at least 0.80 and few failures |

The table was confirmed by constructing the evidence record with values on
each side of each line. Established and robust primitives are the ones the
engine lists as available
(`test_reproducible_temporal_sequence_can_mature_motor_competence`,
`test_natural_recurrence_surfaces_competence_without_forced_replay`).

Two observations from the ad hoc run put the gate in proportion. In a
synthetic body where two signals each rose by one hundredth of the activation
of one channel, the first primitive was established at tick 20, after two
counts. And the failure count that the robust label depends on is always zero
for a primitive: the engine does not count failures.

The engine keeps at most 512 sequences with statistics and 256 primitives.
When over the bound, established primitives are kept in preference to others
(`test_bounded_primitive_pool_preserves_proven_competence`).

## Replaying a primitive

A caller may ask the engine to activate an available primitive by identifier.
The engine then proposes that primitive's four steps on the next four ticks
instead of exploring, and returns to exploration
(`test_cognitive_primitive_replays_only_learned_motor_pattern`,
`test_cognitive_primitive_execution_preserves_full_temporal_duration`). If the
caller reports, with each observation, that the delivered activations were a
replay of that primitive, the effect is counted for it regardless of how the
delivered values quantise. The engine never starts a replay by itself.

## What leaves the engine, and where it stops

The engine exposes the identifiers of available primitives and withholds
their sequences. One function in the agency package consumes that view:
`organism:src/organism/agency/candidates.py::motor_competence_candidates`
takes objects with an identifier and a maturity, keeps those that are
established or robust and for which the caller supplies a readout, and returns
at most eight of them as candidates for
[prospective deliberation](prospective-deliberation.md), in order of
identifier (`test_only_competent_primitives_included`,
`test_order_is_deterministic_by_primitive_id`, `test_max_candidates_enforced`,
`test_zero_readout_included`). It never imports the engine: the two agree only
on those two attribute names. In the ad hoc run the engine listed 24 available
primitives and the function returned the first 8 by identifier, not the 8 with
the most support.

**That is the only connection.** The rest of the package speaks of a different
record, `organism:src/organism/actuation/competence.py::MotorCompetence`,
which names a controller and an effect and carries the same kind of evidence.
[Execution bindings](execution-binding-and-affordances.md) and the affordance
resolver take that record. Nothing in the repository, source or tests,
constructs one, and nothing constructs the library meant to hold them
(`CompetenceLibrary`; search for the two constructors on 2026-10-09). A
primitive carries no effect identifier and no controller, and no function
derives a competence record from a primitive. So what this engine learns
cannot, at this revision, reach a binding, an affordance or an admission. This
is recorded as finding F-0100.

Two neighbouring modules are also unconnected. One counts, for an ordered pair
of competences and an effect, successes and failures, and calls the pair
established after four successes with a success share of two thirds
(`organism:src/organism/actuation/composition.py::CompositionEngine`; after
four successes and one failure an ad hoc run gave a share of 0.8 and
established). The other orders exploration opportunities by a fixed sequence
of criteria, lowest risk first
(`organism:src/organism/actuation/exploration.py::ExplorationPolicy`; offered
a safe opportunity with nothing to learn and a slightly risky one with
everything to learn, it chose the safe one). Neither is constructed anywhere,
neither has a test, and the engine uses neither.

## Across a restart

The engine exports its whole state to plain data: levels, use counts, the
position in the current bout, the last 70 observations in full, all
statistics, the primitives and an unfinished replay. Restoring gave an equal
snapshot and equal primitives
(`test_sensorimotor_checkpoint_roundtrip_preserves_learning_state`,
`test_probing_is_deterministic_and_survives_checkpoint_mid_series`). In the
600-tick run the export was about 150 kilobytes of JSON.

Restoring is strict. Earlier schema versions are refused, as are missing
fields, non-finite numbers, primitives without two counts behind them and
timestamps out of order
(`test_pre_current_sensorimotor_schemas_are_rejected`,
`test_sensorimotor_restore_rejects_coerced_or_nonfinite_skill_state`,
`test_sensorimotor_restore_rejects_corrupted_primitive_lifecycle`).

When this document was first written, three things did not come back from an
export: the limit on simultaneous channels, a non-default gate, and the
organism identifier. Since `organism@2f051b0` two of them do. The export
carries the organism identifier and the effective limit, and restoring
refuses another identifier or a limit that disagrees with the one expected
(`test_checkpoint_restore_preserves_identity_and_effective_concurrency_output`,
`test_restore_rejects_max_concurrent_mismatch_and_invalid_checkpoint_value`).

One still does not: a non-default gate. It is described in the code as
organism configuration and is not exported, so a restored engine applies the
default until the caller sets it again (confirmed by running the class at the
revision first reviewed; the change since does not touch the gate).

No checkpoint in the repository includes this export. The composed cognitive
payload described under
[identity and the checkpoint envelope](identity-and-checkpoint.md) does not
mention it (search of `organism:src/organism/checkpoint.py` and
`organism:src/organism/cognition/portable_checkpoint.py`, 2026-10-09). This is
part of finding F-0102.

## Across a change of body

The engine is built for one body, named by a string the caller supplies and
the engine never interprets (`test_sensorimotor_requires_an_explicit_embodiment_fingerprint`).
Every primitive carries that string.

- **An export cannot be restored for another body.** Restoring with a
  different string fails with "sensorimotor embodiment scope mismatch", and
  with a different list of channels it fails as well
  (`test_current_checkpoint_rejects_different_body_scope`).
- **There is one door for earlier patterns, and it is narrower than its
  description.** A method accepts exported primitives as historical
  candidates: they keep their identifier, have no statistics and are not
  available until two fresh counts support them
  (`test_historical_primitive_requires_fresh_evidence_before_cognitive_reuse`).
  Its docstring reads "Register prior-body motor hypotheses without granting
  competence." The method skips, without error, every entry whose body string
  differs from the engine's own. In the ad hoc run the 24 primitives learned
  under one string were offered to an engine built with another: none was
  accepted. The same entries with the string overwritten by hand were all
  accepted. The test uses the engine's own string.

So at this revision a change of body leaves two possibilities to a caller:
build a new, empty engine, or rewrite the body string in the old entries.
Nothing in the repository does either.

### Beside the decision on body schema and competence

[ADR-0104](../../technical/adr/ADR-0104-body-schema-and-competence.md) is set
beside the code here without a ruling on conformance. It defines a target and
says so of itself.

| The decision says | The code at this revision |
|---|---|
| "Re-embodiment may invalidate active commitments/calibration but must not silently erase longitudinal learning." | No operation performs a re-embodiment. An export is refused for another body, loudly. Historical candidates from another body are dropped silently. |
| "Competence may require reacclimation or become temporarily unusable while remaining learned Organism state." | A historical candidate that is accepted needs two fresh counts before it is available again. An engine holds primitives of one body only; there is no place where primitives of an earlier body remain while unusable. |
| Learned knowledge about bodies and prior embodiments is the Organism's. | The engine lives in the Organism package and imports nothing from another domain. Its body string and channel list are supplied by the caller. |

The mismatch between the method's description and its behaviour, and the
absence of any path that carries primitives to another body, are recorded as
finding F-0101.

The repository's own migration notes say that a further module of the
historical package was left out: "is deferred because it writes to Embodiment
body-schema state". No `acquisition.py` exists under
`organism:src/organism/actuation/` at this revision (listing of the tree,
2026-10-09).

## At each lifecycle boundary

| Boundary | What happens | Support |
|---|---|---|
| Birth | A new engine has no statistics and no primitives | Code |
| Checkpoint | The whole state can be exported, except the gate | Code, tests and ad hoc run |
| Restart | An export can be restored for the same body string and channels; no checkpoint carries it | Code and tests; search of the repository |
| Re-embodiment | No operation exists. Restoring for another body is refused; historical candidates from another body are dropped | Code, test and ad hoc run |
| Reproduction | No operation exists. The genome carries no motor genes | `test_genome_v2_has_no_motor_genes`; search of the genetics code for the engine, 2026-10-10 |

## Time and determinism

[ADR-0090](../../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md)
says: "Host wall-clock time is never implicit causal authority." The two
packages `organism:src/organism/actuation/` and `organism:src/organism/agency/`
import only `math`, `hashlib`, `statistics`, `dataclasses`, `enum`, `typing`
and `collections` from the standard library (listing of every import
statement, 2026-10-09). No clock, no random number generator, no process
identifier and no salted built-in hash is used. Every tick is an argument.
Whatever looks random in exploration is a digest of the organism identifier
and a bout number.

The engine does assume that ticks advance by one. Observations whose ticks are
not consecutive are ignored for sequence statistics, without error
(`test_noncontiguous_temporal_window_is_ignored_without_error`).

## A byte export of the competence library

> Section added on 2026-10-17 against `organism` `c26d0072ba9312a2ce7e7b47d3580e5be71fa48f` (organism#180).
> Sources examined: `src/organism/actuation/competence.py` and
> `tests/source_unit/actuation/test_competence_checkpoint.py`. The rest of
> this document keeps the review revision stated at its top.

`CompetenceLibrary.to_bytes` writes the library's checkpoint as canonical
JSON (sorted keys, compact separators). `CompetenceLibrary.from_bytes`
refuses input that is not bytes, has duplicate fields or does not decode to
a valid library (`test_competence_library_checkpoint_roundtrip`). As with
Organism's other byte codecs, decoding does not require canonical form:
other encodings of the same library are accepted (finding F-0175).

## What supports this description

| Claim | Support |
|---|---|
| Exploration is deterministic and keyed by organism identifier | Code, and an ad hoc run of the class at that revision |
| Bouts, channel choice, exclusive groups, probing | Code and tests in `organism:tests/source_unit/actuation/test_sensorimotor.py` and `organism:tests/source_unit/actuation/test_causal_probing.py` |
| How an effect is measured; the passive baseline; overlap and near-duplicate rules | Code and the tests named above |
| The three formulas and the threshold of 0.002 | Code |
| The maturity table | Code, and the ad hoc run |
| First primitive established at tick 20 in a synthetic body; no passive samples without probing; failures always zero | The ad hoc run only; the body was two lines of arithmetic, not an Embodiment |
| Replay | Code and tests |
| The candidate function and its limit of eight | Code and tests in `organism:tests/source_unit/agency/test_candidates.py`; that it returns the first eight by identifier, from the ad hoc run |
| Nothing constructs a competence record or the library; nothing outside tests constructs the engine; composition and exploration ordering are unused | Search of the seven repositories at `origin/main`, 2026-10-09 |
| Export and strict restore | Code and tests |
| The gate does not survive a restore; the concurrency limit and the organism identifier do, and are checked | The ad hoc run for the gate; tests for the other two |
| Refusal for another body | Code and test |
| Historical candidates from another body are skipped | Code and the ad hoc run; the test covers only the same body |
| What re-embodiment must not do | Accepted decision ADR-0104; a statement of intent |
| No host time | Search described above; accepted decision ADR-0090 for the rule |

No run of the engine against an Embodiment was examined, because none exists.
That primitives found this way correspond to anything a body can usefully do
is not supported by anything reviewed here.

## Open questions

- Which component turns an available primitive into a competence record with
  an effect and a controller, and so into a binding and an affordance.
- What the body string is meant to be: the actuator surface fingerprint of
  [the action path](action-path.md), an Embodiment identity, or something
  else. The engine accepts any non-empty string.
- Whether primitives of an earlier body are meant to remain in Organism state
  while unusable, and where.
- Whether the thresholds, which are in the units of whatever signals the
  caller supplies, are meant to be independent of those units.
