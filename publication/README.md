# Publication

How the documentation is assembled into one ordered work.

Three things are kept apart:

- the **corpus** (`explanation/`, `technical/`, `reference/`) says what is known;
- the **registry** (`registry/`) says where it comes from and what state it is in;
- the **publication** (this directory) says in which order it is presented.

`biopeia-master.yaml` is the composition of the main publication. It holds no
documentary text. It lists parts and appendices; each names chapters, which
are documents of this repository in reading order, and generated sections,
which are rendered from the registry. A published document therefore never
decides what the canonical documentation is: it presents sources that stay
canonical where they are.

The order starts with the system view (the domains, and how one step crosses
them today), then goes down into the domains: Organism, Embodiment,
Environment, World, Modality and Observation, Lab. The contracts that bind
one domain to another come last, followed by the
appendices. `registry/findings.yaml` is audit material and is not published.

## Editions

A build is a **working edition** unless it is built with `--release`. A
working edition is built from whatever state the sources are in and says on
its front page that it must not be cited. A **published edition** requires
this repository and every domain repository to be resolved to a clean
revision, and the build fails otherwise. The build manifest records which
one a file is. The `Publication` workflow builds the published edition on
`main`.

## Rules

- A chapter that does not exist, a document listed twice or an unknown
  generated section fails the build.
- Every document under `explanation/` is either a chapter or listed under
  `excluded` with a reason. A new document that nobody placed fails the
  build; nothing is left out silently. `README.md` files are navigation
  indexes and are never chapters.
- A part with no explanatory document of its own is not padded with new text
  here. Writing that document is documentation work, done in the corpus.

```bash
python tools/publication/model.py   # check the manifest
```

## Known gaps

- **Biopeia has no visual style.** The earlier documentation design system was
  deprecated and not carried over, and no replacement has been decided. Until
  one exists, published documents use neutral defaults only and choose no
  colours, typefaces or cover.
- **No document says what Biopeia is.** Nothing in `explanation/` yet states
  its purpose, its principles, or why its domains and authorities are
  separated. The first part shows what the registry holds about the domains
  and how one step crosses them today.
- **One publication, in the order of the domains.** Two publications from the
  same sources (an architecture overview and a technical reference), system
  diagrams generated from the registry, a maturity table per capability and
  the editorial design are recorded as work for after the migration
  (issues #78, #79, #80).
- **Notation, parameters and metrics are empty registries.** Their appendices
  say so instead of being omitted.

## Provenance

The publication capabilities (deterministic build, intermediate semantic
projection, editable DOCX, PDF with a real table of contents, build manifest
with hashes) follow those of the publication pipeline of the historical
source repository. Its code was not migrated: it was built around that
repository's component identifiers, books and registries. Everything here is
written against the Biopeia registries, which are the only source.
