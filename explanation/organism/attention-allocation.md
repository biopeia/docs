# Allocating a bounded budget of attention

Reviewed against `organism` at commit `2f051b029018a30f10acddaedc70d2b7edd3325c`.
Everything below describes that revision.

## What it is

A small, self-contained calculation: given some named candidates, each with
an uncertainty and a cost, and a fixed budget, choose which candidates to
spend the budget on. Nothing more is in the module, and the module says so:
it "does not observe sensors, infer threats, inspect outcomes, or execute a
choice".

The word attention is the module's name for the thing being budgeted. The
code does not attend to anything. It ranks numbers supplied by a caller and
returns a list of names. Whether the result is ever used to direct anything
is outside it, and at this revision nothing uses it.

## How the choice is made

Each candidate
(`organism:src/organism/cognition/attention.py::AttentionCandidate`) has a
name, an uncertainty, a cost, a ranking cost and a count of past
observations. Costs must be positive and finite; the uncertainty may be
infinite, which stands for "unknown", but not negative or undefined
(`test_candidate_validation_preserves_infinite_unknown_uncertainty`,
`test_candidate_rejects_non_finite_ranking_costs`).

The allocator scores each candidate as uncertainty divided by cost times
ranking cost, reduced as the count of observations grows, sorts by score with
ties broken by name, and takes candidates in that order while they still fit
in what is left of the budget
(`test_allocates_by_uncertainty_per_cost_then_fits_budget`,
`test_unknown_uncertainty_wins_and_ties_are_deterministic`,
`test_observation_count_applies_diminishing_return`,
`test_candidate_over_budget_is_not_selected`). The ranking cost changes the
order only; the budget is consumed by the cost
(`test_rank_cost_reorders_without_changing_consumed_cost`).

The result is the same for the same input. No clock and no random source is
read.

## What it is not

The module is exact about its own limits. The method is "the source
implementation's greedy uncertainty per cost heuristic, not an optimal
knapsack solver or a scientific claim". A greedy choice can leave budget
unused that a different selection would have filled.

It holds no state between calls: nothing is learned, remembered or adapted.
The count of observations is an input, not something the allocator keeps.

## Who uses it

Nobody. A search of the source of all seven repositories at their main
branches on 2026-10-10 found no import of this module outside its own tests.

## What supports this description

Code and the tests in `organism:tests/source_unit/cognition/test_attention.py`,
named above. The absence of a user rests on the search just described.
