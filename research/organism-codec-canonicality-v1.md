# Organism checkpoint codecs: is the byte encoding of a state unique? (V-02, v1)

**Scope:** a read-only investigation for V-02 of
[the verification strategy](verification-strategy-v1.md). Implementation
belongs to Organism. Read at `organism` `779c097d21236cba0409f5fc52fbcd71bf2049d9` and `world` `8266b8968b4dd52231723564d833077675a316d2`.

## Why uniqueness matters

World stores an owner checkpoint under the SHA-256 of the bytes the owner
hands it (`world:src/world/owner_checkpoint_store.py:151`). Commit identity,
owner checkpoint references and declared dependencies all name a state by
that digest. If the same state can have two byte encodings, it can have two
digests, and nothing would notice.

## What the codecs do

Six Organism modules expose a byte codec: the longitudinal envelope
(`checkpoint.py`), the portable cognitive checkpoint
(`cognition/portable_checkpoint.py`), continuation metadata
(`continuation.py`), the competence and causal-model exports
(`actuation/competence.py`, `actuation/model.py`), and the compact action
history (`actuation/action_history.py`).

- **Encoding is canonical in all six:** `json.dumps(..., sort_keys=True,
  separators=(",", ":"))`. `action_history.py` also passes
  `ensure_ascii=False`; the others use the default `ensure_ascii=True`, so
  the two families escape non-ASCII text differently.
- **Decoding is not canonical in any of them.** Each rejects duplicate keys
  (`object_pairs_hook`) and validates fields. None re-encodes the decoded
  value and compares it with the input bytes.

## Probe (ad hoc, not kept as a test)

On an extracted copy of `organism` `779c097d21236cba0409f5fc52fbcd71bf2049d9`, one `OrganismCheckpoint` was
encoded and then re-supplied in four other byte forms:

| Variant | Accepted | Same state | Digest differs |
|---|---|---|---|
| Pretty-printed (`indent=2`) | yes | yes | yes |
| Keys reordered | yes | yes | yes |
| One character as a `\u` escape | yes | yes | yes |
| Trailing newline | yes | yes | yes |

Every variant decoded to a state equal to the original, and re-encoding gave
the canonical bytes back. The other five decoders follow the same pattern in
code (no re-encode comparison); they were not probed.

## Reading

In the normal path an owner produces bytes with its own `to_bytes`, so each
state World sees has one digest. The gap opens only where bytes come from
somewhere else: an imported or transferred checkpoint, tooling, or a
restore input that is not the stored blob. There, a decoder accepts a second
encoding of a state already known, under a different digest. This is a
**uniqueness gap, not an observed failure**. Recorded as finding F-0175.

## What would close it (for Organism)

- **Strict decoding:** `from_bytes` rejects input whose canonical
  re-encoding differs from it. That is one comparison per decoder.
- **Property tests** (V-02 as proposed): for generated states,
  `decode(encode(x)) == x`, and for any accepted `b`, `encode(decode(b)) == b`.
- **Consistency:** one `ensure_ascii` choice across the six encoders.

## Limits

Only the envelope was probed. Whether any current runtime path hands an
owner decoder bytes it did not produce was not traced.
