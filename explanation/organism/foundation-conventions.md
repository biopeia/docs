# Foundation conventions: thresholds, an evidence count and limits

Reviewed against `organism` at commit `fc8a91c61d865663ba6f9468216171506fd29e7a`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, an ad hoc run, or neither. Searches of the
repository were made on 2026-10-10 at that revision.

## What it is

A small directory of the Organism package, `foundation`, holds three things
that are not state and do nothing by themselves: a table of constants for
turning counts and durations into classes, a type for a count, and a table
of ceilings. Its header calls them "Foundational organism conventions
independent of runtime composition."

They are worth a short document for two reasons. Their names (epistemic,
evidence, maturity, confidence) could be read as claims about what the
Organism knows, and they are not. And most of what is in them is used by
nothing in the repository, which a reader looking for the source of a
threshold should know before relying on it.

## The conventions

One immutable value
(`organism:src/organism/foundation/epistemic.py::EpistemicConventions`) holds:

| Constant | Default | Read by |
|---|---|---|
| samples before a signal counts as established | 5 | the sensory normaliser in the cognition code |
| smoothing factor of a moving average | 0.06 | the same normaliser |
| numbers of classes for health, confidence, cost and activity | 16 each | nothing |
| number of maturity classes, and the support needed to enter each | 8; 0, 1, 2, 4, 8, 16, 32, 64 | nothing |
| idle ticks at which recency changes class | 10, 40, 120, 400 | nothing but the method below |
| a representative idle duration for each recency class | 0, 10, 40, 120, 400 | nothing |

The value checks itself at construction: thresholds must increase, the
number of maturity thresholds must equal the number of maturity classes, and
so on (ad hoc run for one such refusal).

It has one method, which maps a number of idle ticks to one of five recency
classes named current, short idle, idle, long idle and dormant. In an ad hoc
run 9 ticks were current, 10 short idle, 399 long idle and 400 dormant; a
negative number was current.

The column on the right is the result of a search. One module outside the
directory imports the conventions
(`organism:src/organism/cognition/activation.py`), and it reads the first two
rows. The class counts, the maturity thresholds and the recency
classification have no reader in source or tests. In particular the
confidence class of an
[experience record](experience-record-and-ledger.md) runs from 0 to 7 by a
rule of its own, and does not refer to the sixteen confidence classes here.

The word epistemic in the name describes the intent of the constants. What
exists is two numbers used to smooth and to gate a running average.

## The evidence count

A second module defines a type
(`organism:src/organism/foundation/evidence.py::EvidenceCount`) that is a
non-negative integer and nothing more. Its docstring is careful about this:
the count "tracks empirical samples/evidence arrivals, not scheduler cycles,
physical duration, or host wall time. It carries no evidence content or
factual authority by itself."

The type refuses a negative value, a boolean, a floating-point number and a
string, and accepts a plain integer or another count
(`test_evidence_count_rejects_negative_values`,
`test_evidence_count_rejects_non_plain_integer_scales`,
`test_evidence_count_accepts_an_existing_evidence_count`). It is written to
JSON as a bare number
(`test_evidence_count_is_a_primitive_non_negative_sample_count`).

The distinction the type is for, a count of evidence as against a count of
ticks, holds only at construction. Arithmetic on a count gives a plain
integer: one count plus one was an ordinary integer in an ad hoc run. And no
module in source uses the type; a search found it only in its own directory
and its test. The estimators it was written for were not copied, as the
migration record states.

This bears on
[ADR-0090](../../technical/adr/ADR-0090-host-wall-clock-time-is-never-implicit-causal-authority.md),
which asks that causal times be "explicit and distinct". A type that names
one such scale exists. Nothing is yet typed with it.

## The limits

The third module defines a table of 25 positive integers
(`organism:src/organism/foundation/limits.py::OrganismLimits`), each a
ceiling: bytes of a host checkpoint, numbers of sensory parts, body
dependencies, action kinds, capabilities, knowledge claims, epigenetic
priors and others. It checks only that each is a positive integer, and
derives two sums.

**Nothing reads it.** A search found the name in its own module, in the
directory's export list and in a docstring. No bounded table in the
repository takes its capacity from here; the tables documented elsewhere
carry capacities of their own. The ceiling of 64 epigenetic priors, for
instance, is unrelated in code to the eight marks that the
[germline record](genome-and-inheritance.md) keeps by default.

The table describes itself as "Hard resource and security ceilings for
somatic and host runtime state." Several of its entries are named for things
that the accepted architecture does not give to the Organism: the body's
parts and dependencies, and host checkpoints.
[ADR-0094](../../technical/adr/ADR-0094-somatic-state-ownership-body-holds-organism-regulates-and-feels.md)
assigns somatic state to the body. The repository's migration record says
of this directory that "broader foundation ownership remains open to later
mapping". The table is reported here as it is: present in the Organism
package, unused, and partly about state that is not the Organism's. That is
an observation about names in an unused table, not a finding that any
authority is crossed.

## Nothing to keep

None of the three holds state. The conventions and the limits are immutable
and created with their defaults; a count is a number. There is nothing to
checkpoint, restore, rebind at re-embodiment or inherit, and no clock or
random source is involved.

## What supports this description

| Claim | Support |
|---|---|
| The constants, their defaults and their self-checks; the recency method; the list of limits | Code of the three modules |
| What the count accepts and refuses, and how it is written to JSON | Code and tests in `organism:tests/foundation/test_evidence_count.py` |
| Class boundaries of recency; arithmetic on a count gives a plain integer; one refusal of inconsistent conventions | Code, and one ad hoc run of the modules at that revision. The conventions and the limits have no test |
| Two constants are read by the sensory normaliser; the rest, the count type and the whole table of limits have no reader | Searches of `src` and `tests` at that revision, made on 2026-10-10, for the class names, the field names and imports of the directory |
| That ownership of this directory is unsettled | The repository's own migration record |

## Open questions

- Whether the unused constants are meant to be read by code still to be
  extracted, or are remnants.
- Whether the ceilings named for body and host state belong in the Organism
  package.
