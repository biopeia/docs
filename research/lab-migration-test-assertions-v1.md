# Lab migration record tests: what they assert (V-04 groundwork, v1)

**Scope:** a read-only count for V-04 of
[the verification strategy](verification-strategy-v1.md). Owner direction of
2026-10-17: replace the literal per-row tests with a validator only after the
disposition series closes **and equivalence is demonstrated**. This note
gives the basis for that demonstration. It proposes no change now.

Read at `lab` `e7bb66c44517` (main on 2026-10-17). The 142
`tests/unit/test_migration_*.py` files hold 157 tests and 2,210 `assert`
statements. Each assertion was put into the first matching class, by pattern,
in this order:

| Class | Count | Typical form | What a validator would need to keep it |
|---|---:|---|---|
| Substring present | 931 | `"No scientific … claim is made." in row["rationale_and_caveat"]`, or a heading `in MIGRATION.md` | The non-claim clauses as **structured fields** or closed-vocabulary flags (for example `NOT_ADMITTED`, `NO_EQUIVALENCE_CLAIM`), checked on every row, not as prose substrings in some rows |
| Literal field value | 562 | `row["disposition"] == "SPLIT"`, blob SHAs, symbol lists | Either one reviewed **golden snapshot** of the rows that carry owner decisions, or acceptance that git history protects them. A schema check alone does not preserve exact values |
| Other equality | 352 | identities, paths, owners | Referential integrity across TSVs, plus the snapshot above |
| Count | 106 | `len(rows) == 1172` | Validator totals, with the expected counts recorded once |
| Absence or negation | 77 | `not in`, `is None` | Closed-vocabulary checks (a value not allowed) |
| Other | 182 | mixed | Case by case |

## What "equivalence demonstrated" could mean

A validator replaces the per-row tests without loss if, for the record files
at a fixed revision:

1. **Every invariant the tests express still fails when broken.** The
   demonstration: mutate each asserted field, or remove each asserted
   phrase, in a copy of the TSVs. Then show that the validator, or the
   snapshot check, fails on each mutation the old tests caught. This is a
   mutation-equivalence check, not a line-by-line port.
2. **Values tied to owner decisions are still pinned.** Most of the 562
   literal values are disposition outcomes. Dropping them without a snapshot
   loses protection.
3. **What gets stronger is stated.** Non-claim invariants checked on every
   row, not only on rows that have a test.

## Limits

Classification is by regular expression over assertion text, and the order
of classes decides ties. Counts are approximate to that extent. No Lab file
was changed.
