# World genesis, rosters and participant closure

Reviewed against `world` at commit `cb4bd6b0506b554bf4187b36c23095a7521c4504`.
Everything below describes that revision. Statements are marked by what
supports them: the code, the tests, or neither.

## What this is about

A causal cut is only meaningful if it accounts for everyone whose state it is
supposed to bind. Three questions follow. Who is in this World when it
starts? How does that membership change? And how does World know, at each
tick, that the cut it is about to publish covers everyone it should?

This document follows those three questions through the
[durable runtime](durable-runtime.md) and the
[causal manifest](causal-manifest.md). It adds no component; it describes a
mechanism that the two implement together.

## Two rosters, and a third list

World keeps two different kinds of membership and does not confuse them.

- **Presences.** Who is active in the World. A presence is an identity of its
  own (`world:src/world/runtime.py::PresenceId`), "distinct from any semantic
  owner identity".
- **Registered owners.** Whose state takes part in every causal cut. Each is a
  pair: the owner (for example an organism, a body, an environment) and the
  identity of the particular subject. The code describes these as "resource
  identities, not World presence IDs".

A third list is not a roster: **step participants**, owners whose state takes
part in one tick only and are not registered afterwards.

All three are stored in the manifest of each cut, so they are durable and
part of what a cut means.

## How a World starts

A World begins from a genesis specification
(`world:src/world/durable_runtime.py::WorldGenesisSpec`), which names the
World, at least one initial presence, the registered owners, one initial
checkpoint reference per owner and one checkpoint contract per owner.

It may also declare which owner stands behind each presence
(`PresenceOwnerLink`). If any link is given, the links must cover every
initial presence exactly once and each must point at a registered owner.

Initialisation refuses a genesis in which the active presence is not among
the initial presences, an owner lacks a contract, or the references do not
match the registered owners exactly. It then publishes the cut of tick zero.
Covered by `test_genesis_spec_is_authoritative_input_for_tick_zero_roster`
and `test_complete_cut_requires_nonempty_stable_owner_identity_closure`.

## How membership changes

Only a tick changes membership. The caller of a tick may ask to register or
unregister owners, to register or unregister presences, and to name step
participants. There is no other way: no call adds a member outside a tick,
and the manifest store accepts no roster that differs from the one prepared
when the transition opened.

A tick rejects, before writing anything: duplicates in a request; registering
an owner already registered; unregistering one that is not; a step
participant that is also a registered owner; a tick that would leave no owner
at all; and unregistering the very presence the runtime is acting as. A newly
registered owner and every step participant must come with its checkpoint
contract. When an owner is unregistered its contract is dropped, and a step
participant's contract is not kept after the tick.

Covered by
`test_world_owner_registry_changes_only_through_explicit_lifecycle_tick`,
`test_new_owner_cannot_register_without_owner_checkpoint_contract`,
`test_lifecycle_registration_and_step_participants_are_explicit_and_exact`
and `test_presence_roster_is_published_only_through_world_lifecycle_tick`.

A failed registration does not half-apply. The previous cut stays, with the
proposed roster recorded as pending for the recovery to see
(`test_failed_registration_keeps_prior_cut_and_pending_roster_for_recovery`).

## What closure means here

At each tick World computes the set of owners that must be covered: the
registered owners after the requested changes, plus the step participants.
The owners' callback must return a checkpoint reference for exactly that set,
no more and no fewer. The manifest enforces the same equality when it is
constructed, and again when the cut is committed. A cut with no owner at all
cannot be published.

So closure, in this code, is an exact match between three things: what was
declared for the tick, what the owners returned, and what the manifest
records.

## What closure does not mean

Each of these is read from the code. None is a test result.

- **World does not discover participants.** The required set is built from
  the durable roster and from what the caller of the tick declares. Nothing
  derives it from the World's contents. The genesis specification is, in the
  code's words, "not a discovery mechanism for authorities external to the
  accepted specification". If an authority that ought to take part is never
  declared, no check notices.
- **The link between a presence and an owner is not kept.** It is validated
  at genesis and then discarded: the code states that the durable manifest
  "does not preserve it for later lifecycle transitions or restoration".
  After genesis, World knows who is present and whose state is in the cut,
  and holds no record of which is which.
- **Registering a presence does not require an owner**, and registering an
  owner does not require a presence. The two rosters change independently.

## How this stands against the accepted contract

[ADR-0073](../../technical/adr/ADR-0073-biopeia-migration-causal-and-physical-contracts.md)
states that World "derives and validates the required participant set from
active World presence, registered causal owners, step-specific participants,
and explicit lifecycle transitions", and that callers "cannot establish
roster completeness by supplying an arbitrary list".

The implementation validates exactly and durably against the roster. It does
not derive the roster from presence, because it keeps no relation between
presences and owners, and the step participants and lifecycle changes of a
tick are supplied by the caller. Whether that satisfies the contract or falls
short of it is a question of interpretation that this document does not
settle; it is recorded as a finding.

## What supports this description

| Claim | Support |
|---|---|
| Genesis validation; roster and presence changes only through a tick; contracts required; exact match of references and roster; failed registration keeps the previous cut | Code and tests in `world:tests/test_durable_runtime.py` |
| The manifest's own equality between references and rosters | Code in `world:src/world/manifest.py`, and an ad hoc run recorded in [the manifest document](causal-manifest.md) |
| The limits under "What closure does not mean" | Code and its documentation |
