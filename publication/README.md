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

## Three layers

1. **Projection** (`tools/publication/projection.py`): what is published.
   It knows nothing about appearance.
2. **Style** (`style.yaml`): typefaces, sizes, colours, the logo and the
   layout limits. Data only. Changing it changes how a publication looks and
   nothing about what it says.
3. **Rendering** (`tools/publication/docx.py`, `pdf.py`): lays the projection
   out with the style. It decides no typeface, size or colour.

The style follows the Architecture Owner's decision of 2026-10-10
(biopeia/docs#80): scientific publication with technical specification,
restrained identity, high density, strong navigation. The document names
Aptos and Consolas; the PDF is always rendered in their fallbacks, Liberation
Sans and Liberation Mono, whether or not a machine has the named typefaces,
so that page breaks are the same everywhere. The build fails if the PDF ends
up set in any other typeface, if a page is empty, or if too many are sparse.

`assets/biopeia-logo.png` is the Biopeia mark, accepted by the Architecture
Owner on 2026-10-10, and it is the publisher's only source for it. A build
never fetches the mark from anywhere, and the build manifest records the
hash of the file and of `style.yaml`, so a past build keeps its identity
whatever changes elsewhere. The accent colour is the mark's dark blue.

## Links

A reference in a chapter becomes a link (`tools/publication/references.py`):

- code (`world:src/world/journal.py`), with the line when it names a symbol
  (`…::CausalJournal`), cited tests, commits, the source line of each
  chapter, decision records, designs, findings that have an issue, and
  issues, to GitHub;
- a component identifier to its sheet in the catalog, and a link with an
  anchor to that section, inside the document.

Code is linked at the revision the chapter was reviewed against
(`review.basis` in the registry), because that is the code the text
describes. A file that did not exist then is linked at the revision of the
build. Every link is checked against the local checkouts, without network:
a reference that exists at neither revision fails the build. Without a
checkout a link is still made and counted as unverified; a published
edition allows none, which is why its build clones the domain repositories
with their history. The Biopeia repositories are private, so the links open
only for a reader with access; the reader guide says so.

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

- **The style is approved in direction, with refinements open.** The
  generated DOCX has not been opened in Microsoft Word, which the owner
  requires once before the style issue (#80) closes.
- **No revision history.** The decided front matter includes one. It needs
  numbered releases, and none has been cut (#92). The executive architecture
  is `explanation/biopeia/what-biopeia-is.md`, derived from the accepted
  decision records.
- **Pages that are too full are measured, not judged.** The manifest reports
  the fullest page; no limit fails the build.
- **Parts have no scope statement and chapters no abstract**: the corpus
  holds neither.
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
