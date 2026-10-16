# The study utilities

Reviewed against `lab` at commit `e7bb66c44517e279ca3180d929377682e251d796`
(main on 2026-10-16). Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, or an ad hoc run.

## What they are

Three small sets of functions that a study could call around its runs: checks
on lists of random seeds, arithmetic on lists of measurements, and hashes of
an event stream and of a configuration. They hold no state, read no clock,
import nothing from any other Biopeia domain, and are called by nothing else
in the Biopeia repositories at the revisions examined. They were copied from
the historical repository as utilities; the studies that used them were not.

The repository states their reach: "They do not run experiments, own simulated
life, or carry scientific artifacts."

This document says what each function computes, and, because the names
suggest more than the arithmetic does, what none of them establishes.

## Seed checks

`lab:src/lab/studies/common/pairing.py` holds three assertions over lists of
seeds. Each returns nothing or raises an error.

- **Unique.** No value appears twice in one list (`test_unique_seeds_enforcement`).
- **Disjoint.** No value appears in both of two lists
  (`test_disjoint_seeds_enforcement`).
- **Paired.** Two lists are equal, element by element and in the same order
  (`test_paired_seeds_enforcement`).

These are comparisons of numbers. They do not generate seeds, do not know
what a seed was used for, and do not check that a run actually used the seed
it was listed under. A pair of lists that passes the paired check is two
equal lists; whether the two conditions of a study were otherwise comparable
is outside the function.

Confirmed by running the module:

- the paired check accepts lists that contain repeated seeds, and the
  disjoint check accepts a list that repeats a seed within itself. Uniqueness
  must be asked for separately;
- the paired check refuses the same seeds in a different order;
- values are compared as Python compares numbers, so `1`, `1.0` and `True`
  count as the same seed.

## Scalar summaries

`lab:src/lab/studies/common/statistics.py` holds four functions over lists of
numbers in which a missing measurement is written as `None`.

- **Mean of what is present** (`test_safe_mean`). Missing values are left out;
  a list with none present gives `None`.
- **Paired differences** (`test_paired_deltas`). The two lists are walked
  together and the difference is taken wherever both values are present.
- **Mean paired difference** (`test_mean_delta`).
- **Aggregate** (`test_aggregate_metric`): the mean, the median, a standard
  deviation and the count of the values present.

These are descriptive. There is no test of significance, no interval, no
effect size and no correction of any kind. A mean difference returned by
these functions is a number, not a finding that a treatment had an effect.

The details that change how a result should be read, confirmed by running
the module:

- **Pairs are positional.** The functions pair by position in the list and
  know nothing of seeds. Pairing by seed is the caller's arrangement.
- **Unequal lists are cut short without notice.** Three treatment values
  against one baseline value give one difference.
- **Dropped pairs are not counted.** A pair with a missing side disappears
  from the result; the number dropped is not reported.
- **The standard deviation is the sample one**, dividing by one less than the
  count. For a single value it is reported as zero, not as absent. No test
  covers the standard deviation.
- **Values that are not numbers are not handled.** A not-a-number value passes
  through the mean as not-a-number and makes the aggregate raise an error
  unrelated to the cause.

## Digests

`lab:src/lab/studies/common/digests.py` holds two functions that return a
SHA-256 hash as text. Both use canonical JSON serialization (UTF-8, sorted keys,
compact separators `("," , ":")`, ASCII unescaped, non-finite floats rejected
and numeric types preserved without coercion) prefixed by a domain separator:
`biopeia.lab.world-digest.v2\0` for the event stream and
`biopeia.lab.config-digest.v2\0` for configuration dictionaries.

### The event stream digest

The function is named for a world, and the name needs care. It has nothing to
do with the World domain, its journal or its digests. It hashes a sequence of
events of one particular shape: a step, a host index, a truth label and a
threat flag, optionally with a phase, a drift state and an observation that
can give a vector of numbers. That shape comes from the historical
repository. No code in the Biopeia repositories produces such events at the
revisions examined; the tests build them by hand.

What it does: each event is encoded as a canonical JSON payload and hashed
with 64-bit big-endian length prefixing (framing). An event object is encoded
as an eight-element list:
`["event", step, host_index, truth_label, is_threat, phase, drift_state, observation_data]`.
An absent phase or drift state is encoded as `{"absent": True}`. If an observation
is present and exposes a `vector()` callable, its vector elements must be int or
float and are stored as a list; an explicit `None` observation is encoded as
`None`, while an absent observation attribute is encoded as `{"absent": True}`.
A plain string `ev` is encoded as `["str", ev]`. Anything else is refused, so that
an object's default text form, which may contain a memory address, never reaches
the hash (`test_digest_rejects_objects_with_process_specific_default_repr`).
Field types are checked strictly: a boolean is not accepted as a step, non-string
phase or drift state is rejected, non-finite floats are refused, and keys must be strings.

Tests cover that equal streams give equal digests and that a difference in
the observation, the phase or the drift state changes the digest
(`test_digest_is_stable_for_identical_event_streams`,
`test_digest_differs_when_only_the_observation_vector_differs`,
`test_digest_differs_when_phase_differs`,
`test_digest_differs_when_drift_state_differs`,
`test_digest_accepts_deterministic_plain_string_events`).

The function's documentation says it "Never includes anything the agent itself
decided". That is a property of what a caller puts into the events; the
function hashes what it is given.

In earlier revisions, fields were joined with colons and events with line breaks
without escaping, which caused separator collisions (finding F-0064). Under the
v2 canonical JSON framing:

- framing and structured lists prevent separator collisions between fields or
  across event boundaries (`test_digest_frames_strings_and_event_fields_without_separator_collisions`);
- integer and floating-point representations remain distinct in JSON numbers
  (`test_digest_preserves_numeric_type_and_observation_availability`);
- absent observations, empty observation vectors, and unavailable observations
  (`None`) produce distinct payloads (same test).

The repository's migration notes bound the claim: the helper "does not
acquire World state ownership or assert causal equivalence beyond the supplied
event representation."

### The configuration digest

The hash of a configuration dictionary, prefixed with `biopeia.lab.config-digest.v2\0`
and encoded as canonical JSON. The argument must be a Python `dict` with string
keys (`test_config_digest_preserves_json_number_types_and_rejects_coercions`).
Key order does not matter; integer and floating-point numbers remain distinct
(`1` and `1.0` differ in JSON); non-finite numbers (`NaN`, `Infinity`) raise a
`ValueError`; and non-string dictionary keys raise a `TypeError`.

## State and time

None. Every function is a pure computation over its arguments.

## What supports this description

| Claim | Support |
|---|---|
| The three seed checks; the four summaries on the cases exercised; digest stability and sensitivity to observation, phase and drift state; refusal of unsupported events; v2 framing and type preservation; config digest validations | Code and tests in `lab:tests/unit/test_pairing.py`, `lab:tests/unit/test_statistics.py` and `lab:tests/unit/test_digests.py`; the 24 unit tests of the repository passed when run for this document |
| Repeated seeds accepted by the paired and disjoint checks; numeric equality of seeds; truncation and uncounted drops; standard deviation of one value; behaviour on not-a-number | Code, and ad hoc run of the modules at that revision |
| No caller and no producer of the event shape in Biopeia | A search of the seven domain repositories at their main branches on the day of review |
| The reach of the utilities | `lab:README.md` and `lab:MIGRATION.md`; statements by the repository |

Nothing here is scientific evidence. Passing tests show that the arithmetic
does what is written above on the inputs tried.

## Open questions

- Whether the event stream digest is to be kept, given that the events it
  hashes have no producer in Biopeia, and what would replace it for a study
  over a Biopeia World.
- Whether the summaries should report how many values or pairs they left out.
