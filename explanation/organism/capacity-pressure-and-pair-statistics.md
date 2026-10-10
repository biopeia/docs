# Capacity pressure and pair statistics

Reviewed against `organism` at commit `ba0011797a6a3b4d48c7731651e50560c4043f18`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or neither. Searches were
repeated on 2026-10-11 over the source and tests of all seven repositories,
and the ad hoc run was repeated at that revision.

## What they are

Much of the Organism's private state is kept in bounded tables: when a table
is full, something is dropped to make room. Two small values recur inside
those tables. Neither is a store by itself; each is a few numbers that
another structure owns and updates.

The first, **capacity pressure**, counts what a bounded table does at its
limit: how many items came in, how many were dropped, and how many of the
dropped came back. It is a measurement of the table, kept beside it.

The second, the **pair accumulator**, summarises a stream of pairs of numbers
in six numbers, enough to give their correlation at any moment without
keeping the pairs.

They are documented together because they are small and shared, not because
they interact. They differ in one respect that matters: the first is meant
to be read by nobody inside the Organism, and the second feeds a decision.

## Capacity pressure

A table that wants to be measured creates one of these with its capacity
(`organism:src/organism/capacity.py::CapacityPressure`) and tells it two
things: after it has dropped items, which ones; after it has inserted a new
item, which one.

From those two reports the value keeps five counters: admissions, evictions,
promotions, demotions, and a count the module calls relearned after
eviction. The last is the interesting one. Each dropped item is remembered
as a fingerprint, the first 16 hexadecimal digits of a SHA-256 of its name.
If an item is later admitted whose fingerprint is among the remembered ones,
the count goes up by one and the fingerprint is forgotten. A high count
would mean the table keeps dropping things it then needs again.

Only the 256 most recent fingerprints are remembered. In an ad hoc run, after
300 drops, re-admitting the first dropped item was not counted and
re-admitting the last was.

The value can report a snapshot: capacity, occupancy as told by the caller,
their ratio, and the counters. The ratio is not limited to 1; an occupancy of
10 against a capacity of 4 gave 2.5 (ad hoc run).

### Measurement only, by declaration

The module opens with "Measurement only" and continues: "Nothing here is read
by any decision, so instrumenting a store never changes behaviour." It also
says of the fingerprints that they "are never used as functional memory".

A search supports the first claim as far as the repository goes. Five
structures hold one or two of these values: the executive outcome ledger, a
consolidation tracker in the generative cognition code, the sensorimotor
learner, the binding table and the effect table of the actuation code. Each
writes the value into its own exported state. One of them, the effect table,
offers a method returning the snapshot, and no code calls that method. No
code reads a counter back to choose anything.

Two of the five counters, promotions and demotions, are never changed by
anything: the value has no method for them and a search found no code that
sets them. They are exported as zero.

### Across a restart

The value exports its counters and its fingerprints with a schema version.
Reading back has become strict, and four statements made here at the earlier
revision no longer hold. The caller still states the capacity, but it must
now equal the exported one: a value exported with capacity 4 and read back
with 99 was refused, where it used to come back with capacity 99. Data that
is absent, or that lacks or adds a field, is refused, where it used to give
fresh counters; the docstring now says "fresh state uses the constructor". A
negative count is refused, where it used to be raised to zero. And the value
checks the schema version itself
(`test_capacity_pressure_checkpoint_requires_complete_matching_state`; each
case also by an ad hoc run). The fingerprints must be at most 256 distinct
strings of 16 hexadecimal digits.

The counters are not checked against one another. A payload with no
admissions, no evictions and 50 relearned after eviction was accepted (ad
hoc run). Recorded, with the accumulator's impossible combinations below,
in finding F-0147.

So a table's measurements survive a restart exactly when the table that owns
them is exported and restored. For the
[executive outcome ledger](executive-outcome-ledger.md) that document
describes the situation: the export exists and no checkpoint carries it.

## The pair accumulator

The accumulator (`organism:src/organism/statistics.py::PairAccumulator`)
receives pairs (x, y) one at a time and keeps a count, the two running
means, the two sums of squared deviations and the sum of cross deviations.
The update is the usual online one, in which each new pair adjusts the means
and adds to the sums, so the memory used does not grow with the number of
pairs.

Asked for the correlation, it answers with the cross sum divided by the
square root of the product of the two squared sums, limited to the range −1
to 1. It answers with nothing at all in three cases: fewer than three pairs,
no variation in x, or no variation in y. A pair in which either number is
not finite is ignored and not counted. All of this was seen in an ad hoc run:
no answer after two pairs, 1.0 after three collinear pairs, no answer for a
constant y, and a count unchanged by a pair containing a not-a-number.

The class describes itself as "Bounded online bivariate statistics used by
actuator effect evidence." A correlation between two streams is a statement
about the numbers. Whether one stream is an action and the other its effect
is decided by whoever feeds it.

### The one user

One module imports it
(`organism:src/organism/actuation/candidate.py`): a candidate actuator keeps
longitudinal aggregate relations and also keeps relations partitioned by an
exact body/episode/morphology/surface context. The aggregate evicts its
weakest relation when the 256-percept bound is reached. A context holds up to
256 relations and refuses additions at its bound; the candidate retains up
to 128 contexts and refuses a new one rather than evicting prior context
evidence. Promotion reads only the current context's effect strength and
sample count; the pooled longitudinal aggregate cannot promote applicability
for a new physical context. The candidate's tests exercise the accumulator
through both layers. Four tests in
`organism:tests/source_unit/test_statistics_checkpoint.py` now address the
accumulator directly, all of them about reading it back; none addresses the
update or the correlation.

Other modules in the repository import a module named `statistics`. That is
the standard library's, not this one.

### Across a restart

The six numbers are exported and read back exactly
(`test_pair_accumulator_checkpoint_round_trip`). Reading back refuses a
missing field, and now also an unknown one and data that is not a mapping
(`test_pair_accumulator_checkpoint_rejects_missing_field`,
`test_pair_accumulator_checkpoint_rejects_unknown_field`,
`test_pair_accumulator_checkpoint_rejects_non_mapping_payload`), a negative
or non-integer count, a non-finite number and a negative sum of squares. It does not check that the six numbers
are possible together: a count of zero with non-zero sums was accepted, and
so was a cross sum far larger than the squared sums allow, for which the
correlation answered 1.0 because of the limit (ad hoc run).

## Time and randomness

Neither value reads a clock or draws a random number. The fingerprint is a
SHA-256, the same in every process. The accumulator's result depends on the
order of the pairs only through floating-point rounding.

## At each lifecycle boundary

Both values live and die with the structure that holds them, so the table
states what the values themselves do.

| Boundary | What happens | Support |
|---|---|---|
| Birth | Counters at zero; an accumulator with no pairs | Code |
| Checkpoint | Each exports all its numbers when its owner asks | Code and ad hoc run |
| Restart | Each is rebuilt from a complete export and refused otherwise; the capacity stated by the caller must equal the exported one; impossible combinations of accumulator numbers, and of capacity counters, are accepted | Code, tests and ad hoc run |
| Re-embodiment | Nothing in either value reacts; what an owner does is the owner's matter | Code |
| Reproduction | No operation exists | Search of the repository |

## Whose state this is

Both values sit inside structures that
[ADR-0092](../../technical/adr/ADR-0092-organism-owns-the-meaning-of-its-private-longitudinal-state.md)
places under the Organism's authority. The capacity counters are described by
their module as measurement that no decision reads; an observer outside the
Organism would be their natural reader, and no path from them to one exists
in the repository. The decision says that internal conditions are exposed
outward as signals the Organism emits, not read from its internals by
another authority. How these counters are meant to leave, if at all, is not
recorded in the code.

## What supports this description

| Claim | Support |
|---|---|
| What the two values keep and compute; the bound on fingerprints; what reading back refuses | Code of `organism:src/organism/capacity.py` and `organism:src/organism/statistics.py`; for reading back, tests in `organism:tests/source_unit/test_checkpoint_fail_closed.py` and `organism:tests/source_unit/test_statistics_checkpoint.py` |
| The counts after drops and re-admissions; the unlimited ratio; a mismatched capacity, absent data and a negative count refused; the accumulator's answers and its three silences; impossible combinations accepted | Code, and one ad hoc run of the modules at `organism` `ba0011797a6a3b4d48c7731651e50560c4043f18`; no test addresses the counting, the snapshot, the update or the correlation |
| Use of the accumulator by a candidate actuator | Code of `organism:src/organism/actuation/candidate.py` and its tests, read for that use only |
| Which structures hold a capacity value; no code reads a counter to decide; the snapshot method of the effect table has no caller; promotions and demotions are never set; one importer of the accumulator | Searches of `src` and `tests` at that revision, repeated on 2026-10-11, for the class names, the counter names and imports of the two modules |
| That no decision reads the capacity counters | The module's own declaration, and the search above |

No exported counters or accumulators from a run of an Organism were
examined, because none can exist at this revision.

## Open questions

- Who is meant to read the capacity counters, and by what path.
- What promotions and demotions were meant to count.
- Whether an accumulator read back from impossible numbers should be
  refused.
