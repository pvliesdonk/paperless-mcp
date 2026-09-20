# Paperless MCP roadmap

This is agent-authored synthesis, not a record of decisions. Tag each
argument `stated` (the user's words), `derived` (synthesis), or
`evidenced` (with a durable locator). Read the
[`roadmapping` skill](../../.agents/skills/roadmapping/SKILL.md) before
charting or refining work.

Epics are parent issues for stories; packages are milestones for single
release cuts. GitHub holds membership, dependencies and progress. This
index holds the argument for the direction and order.

## Direction

The server wraps the Paperless-NGX REST API as MCP tools and resources.
Everything below turns on one distinction: work that makes *this wrapper*
sound, and work that widens *what a model can do with the archive*. The
first is nearly finished; the second has not started, and its shape depends
on answers nobody has yet.

### Platform: template v8.2.0 and fastmcp-pvl-core 7 — [#100](https://github.com/pvliesdonk/paperless-mcp/issues/100)

`derived`. Moving onto the current template and library generation, absorbing
the operator-visible breaks in one cut rather than spreading them over
several. The story is not "upgrade a dependency": it is that every later
capability below is reachable only through what the new library generation
exposes, so this comes first whether or not it is interesting on its own.

**Done when** an operator running this server gets the current platform's
behaviour without knowing which library version produced it: health and
readiness routes under HTTP, container logs a machine can parse, a quick-start
compose file that runs, instructions shaped by the operator's own description,
and a server that can say which build it is and which Paperless it fronts.
Frozen; see [Revisions](#revisions) for when it was written down and why that
is later than the skill wants.

### Candidate themes, not yet epics

`derived`. Five feature requests were filed in one pass
([#110](https://github.com/pvliesdonk/paperless-mcp/issues/110)–[#114](https://github.com/pvliesdonk/paperless-mcp/issues/114)),
and the older backlog holds a sixth issue that belongs to one of them. None has
been decomposed into an epic. They cluster into four candidate stories, listed
with what would promote one rather than with an order, because the ordering
argument still does not exist — what changed at the triage pass is that two of
them became research issues with appetites, and one shipped into a package
without ever becoming an epic.

- **Getting bytes out of the context window** —
  [#111](https://github.com/pvliesdonk/paperless-mcp/issues/111) (files),
  [#112](https://github.com/pvliesdonk/paperless-mcp/issues/112) (content as a
  file), [#35](https://github.com/pvliesdonk/paperless-mcp/issues/35) (the same
  problem for inline text). `stated`: scanned PDFs are consistently larger than
  a context window can take, so the file endpoints are unusable for the
  documents they exist for
  ([#111](https://github.com/pvliesdonk/paperless-mcp/issues/111)). Promoted by
  a delivery path that keeps file bytes outside model context. `evidenced`:
  [document transfers](document-transfers.md) resolves the wiring choice in
  favor of core's generic link tools with validated domain references for
  document IDs, representations and upload metadata. File-size measurement
  remains useful
  for server-memory sizing, but does not determine the transfer API. #111 and
  #112 share one subsystem, so
  they are one story or neither; #35 is `derived` as the same story's inline
  half and needs neither that subsystem nor that decision, which is why it
  could be committed to `020` on its own. `evidenced`, for the text half only:
  the *text* half of the size distribution this story wants now exists in
  `inline-content-size.md` — 76.2% of the deployed archive's OCR text exceeds
  the current 20,000-character preview and its top decile exceeds a whole
  context window. That number prices inline text and
  nothing else: it says nothing about PDF bytes, so it is not evidence toward
  #111's file-size distribution. The wiring decision is recorded in
  [document transfers](document-transfers.md).
- **What Paperless 3.x offers that this server does not** —
  [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113). `stated`: the
  client was written against the 2.x API and Paperless has since shipped a
  major with AI-backed capabilities. This index previously said the theme
  "plausibly needs a research issue with an appetite before any feature issue
  is honest". It now has one: #113 was relabelled `research` with a two-day
  appetite, which buys querying a 3.x instance rather than reading behaviour
  off `main`. Promoted by that inventory; until it exists there is nothing to
  sequence, because which capabilities are worth exposing is exactly what is
  unknown.
- **Telling the model what instance it is on** —
  [#114](https://github.com/pvliesdonk/paperless-mcp/issues/114). `stated`: the
  composed instructions never name the Paperless instance, although the server
  knows it. `derived`: the predicted outcome — "it joins a package without ever
  becoming one" — is what happened; it is committed to `020` below.
- **Calls that outlast a client's patience** —
  [#110](https://github.com/pvliesdonk/paperless-mcp/issues/110). `stated`,
  including its own doubt: "not sure there is anything (yet)". Answered inside
  its one-day appetite, and the doubt turned out to be misplaced: `evidenced`,
  one of the three candidate calls blocks long enough to need a job, and the
  throwaway spike that priced the integration passed every local gate. The
  verdict, the distribution it rests on and the cost table are in
  `long-running-calls.md`. `derived`: this theme does not become a package of
  its own. Adopting jobs for a single tool is one pull request, and the calls
  that will need the machinery by design belong to the AI surface
  ([#137](https://github.com/pvliesdonk/paperless-mcp/issues/137),
  [#138](https://github.com/pvliesdonk/paperless-mcp/issues/138)), so it
  sequences with them rather than ahead of them.

## Packages

- **[`010 template-v8-adoption`](https://github.com/pvliesdonk/paperless-mcp/milestone/2) (major)** —
  `derived`. The platform move and the follow-ups that finish it. It is a major
  because the update breaks things an operator has to act on, not because the
  follow-ups do: the shipped compose file stops carrying the reverse-proxy
  labels and stops building from the checkout, the container pins its port, and
  anything parsing the old log layout matches nothing afterwards
  (`evidenced`: [#100](https://github.com/pvliesdonk/paperless-mcp/issues/100)
  names them in full). It is one cut rather than two because the update has
  already merged to trunk: releasing anything at all now releases it, so the
  only question was ever whether the follow-ups ride along. They do, and the
  package was since widened to hold the whole platform move rather than the
  follow-ups alone, plus two corrections the cut should not ship without — the
  version mislabel in [#123](https://github.com/pvliesdonk/paperless-mcp/issues/123)
  and this index's own drift in
  [#126](https://github.com/pvliesdonk/paperless-mcp/issues/126).

- **[`020 surface-legibility`](https://github.com/pvliesdonk/paperless-mcp/milestone/3) (minor)** —
  `derived`. The server describing itself accurately to the model: the instance
  URL and URI patterns in the composed instructions
  ([#114](https://github.com/pvliesdonk/paperless-mcp/issues/114)), a title on
  every tool ([#107](https://github.com/pvliesdonk/paperless-mcp/issues/107)),
  and a cap on inline content
  ([#35](https://github.com/pvliesdonk/paperless-mcp/issues/35)). Minor because
  each is additive: nothing an operator configured or a library consumer
  imported changes.

  `derived`: [#107](https://github.com/pvliesdonk/paperless-mcp/issues/107) is a
  `decay` item, and committing debt to a cut deserves saying out loud rather
  than being inferred from the milestone. It earns its place because the debt
  compounds on a schedule: a title is per-tool, the five shared annotation dicts
  cannot express one, and until the enforcement test exists every tool added
  lands untitled too. Doing it for 49 tools later is strictly worse than doing
  it once now, which is the argument for a cut rather than for the backlog.

`derived`: `020` before anything from the bytes theme is a **readiness**
argument, not an information-gain one, and it is worth naming the difference
rather than dressing it up. Nothing in `020` teaches us anything about
`#111`/`#112`; the three issues in it are simply shaped enough to hand to an
implementer today,
while the bytes work required a choice of transfer wiring. That choice is now
recorded in [document transfers](document-transfers.md): domain tools supply
Paperless parameters over the shared route. `derived`: #111 and #112 form one
implementation because file and OCR delivery use the same sink, configuration
and retry contract.

No package beyond `020` exists. `derived`: the horizon rule says create
packages only as far ahead as you can genuinely see them, and the next
candidate, #111 with #112, has a shared design in
[document transfers](document-transfers.md). A design decision alone does not
assign the work to a release cut. An issue
with no milestone is backlog, sitting under its epic or on its own; that
includes [#110](https://github.com/pvliesdonk/paperless-mcp/issues/110),
[#111](https://github.com/pvliesdonk/paperless-mcp/issues/111),
[#112](https://github.com/pvliesdonk/paperless-mcp/issues/112),
[#113](https://github.com/pvliesdonk/paperless-mcp/issues/113) and the older
backlog that predates this index.

## Known unknowns

- **How much of the deployed archive is too large to reach through the current
  file endpoints.** `derived`. Resolved by
  [#111](https://github.com/pvliesdonk/paperless-mcp/issues/111), whose own
  text records the gap. No file-size distribution was measured during the
  transfer implementation; it remains unknown for server-memory sizing. This
  does not change the delivery API or block the user-requested implementation.
- **Which of the library's two transfer wirings fits this server.** `evidenced`:
  [document transfers](document-transfers.md) selects core's Path 1 generic
  tools with a domain validation hook. The same design includes full OCR
  Markdown downloads
  and file uploads, including Markdown, with explicit upload metadata.
- ~~**What the Paperless 3.x API adds, and what its newer payload version
  changes in what this client already parses.**~~ **Answered**, `evidenced`, by
  [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113) within its
  two-day appetite. The durable output is two reference pages,
  `docs/design/reference/paperless-api-versioning.md` and
  `paperless-3x-rest-surface.md`, not a spike document. Three things the
  answer changed: the version pin initially stayed at 9 because version 10
  reshapes tasks and every 2.x instance rejects it. The
  [task payload design](task-payloads.md) under #139 now prefers version 10
  with explicit version-rejection fallback for 2.x; the AI surface is **additive, not
  substitutive**, so nothing this client already parses is affected by it; and
  the gap is 63 unwrapped routes out of 93, which is a menu to choose from
  rather than a debt to repay. The condition that made this a research issue
  — "if it turns out to decide scope for a whole package rather than for one
  feature" — held: the feature issues beneath this theme could not have been
  written honestly before the inventory existed, and they now exist.
- **Whether any Paperless call on the deployed instance blocks long enough to
  need a job.** `stated` in
  [#110](https://github.com/pvliesdonk/paperless-mcp/issues/110), with the
  owner's own "not sure". **Answered**, within the one-day appetite; the numbers
  and the cost table are in `long-running-calls.md` beside this file.
  `evidenced`: one call does. A document consume waited on through
  `wait_for_task` runs to a median of 46.8s and a p95 of 113.7s against that
  tool's own 60s default, so 45% of the observed API uploads would fail on the
  deadline rather than on anything wrong upstream. The two other candidates the
  issue named block for nothing — Paperless returns from both the upload and
  the bulk-edit endpoints before the work they queue has run. `derived`: the
  wait is queue contention rather than OCR (median execution is 1.7s), and the
  queue is the caller's own — all 44 uploads arrived in bursts about a second
  apart and backed up behind each other on a single consume worker, so the nth
  upload waits roughly 2n seconds. `evidenced`: each burst's first upload
  waited essentially nothing. That narrows the verdict rather than weakening
  it: a lone ad-hoc upload never needs a job, and batch ingestion always will.
  This entry stays rather than disappearing, because what it settles is narrow:
  warranted for one tool, in one usage shape, while the calls that will be slow
  *by design* are still unbuilt.
- **Whether a required domain configuration field becomes expressible upstream,
  and whether the resolved config can reach tool registration.** `evidenced`:
  both are worked around in this repository and filed as
  pvliesdonk/fastmcp-server-template#621 and
  pvliesdonk/fastmcp-server-template#622. Resolved by those issues. Recording
  them is enough; neither blocks anything here, and the workarounds are
  documented in `config.md` beside this file.

## Revisions

### 2026-09-20 (bounded document output)

- `stated`: revisit context caps after payload v10 and transfer links shipped
  (implementation session, 2026-09-20). `evidenced`: #155 supplies full files
  and OCR Markdown outside model context, while offset paging remains available
  without transfers. The earlier reason to hold the inline default at 50,000
  characters no longer applies; [inline content size](inline-content-size.md)
  now sets a hard 20,000-character per-call preview budget.
- `evidenced`: #149 found uncapped OCR in four structured tool responses and
  two document resources, plus whole binary preview/download resources. The MCP
  surface now keeps structured responses free of OCR, bounds text resources,
  and routes whole files through transfer links. Direct Python-client calls
  retain their full-content option.
- `evidenced`: a live payload-v10 page of 25 documents carried 2,094,953 OCR
  characters before the client discarded them. That upstream request waste is
  separate from model context and remains tracked by #164.

### 2026-09-20 (payload version 10)

- `stated`: implement #139. `derived`: retain 2.x support through a bounded
  version-rejection fallback while using v10 pagination and structured task
  results on 3.x. [Task payloads](task-payloads.md) records the compatibility
  boundary and its tests. `evidenced`: the source-backed API reference also
  identifies two saved-view preferences omitted by v10; their absence now
  means unknown, requiring Python consumers to handle nullable fields.


### 2026-09-20 (shared registration)

- `stated`: core's Path 1 should cover ordinary integrations, with roughly
  99% as the architectural target rather than a measured claim. Path 2 needs
  a concrete unmet user requirement and a reason a shared upstream change is
  unsuitable ([#158](https://github.com/pvliesdonk/paperless-mcp/issues/158)).
- `evidenced`: [tool registration](tool-registration.md) separates domain
  metadata and error translation from registration. Core's Jobs Path 1 accepts
  both, and transfer Path 1 carries the existing file operations through its
  reference validator. `derived`: preserving a local wrapper or locally
  chosen signature cannot justify taking maintenance out of core. This
  corrects the earlier transfer rationale and the Jobs spike's recommendation.

### 2026-09-19 (document transfers)

- `stated`: implement #111 and #112 together, with Markdown uploads for
  symmetry (implementation session, 2026-09-19). `derived`: preserve uploaded
  bytes and accept explicit metadata; exported front matter remains content.
- `evidenced`: the [core transfer reference](reference/core-transfer-links.md)
  establishes that successful uploads may replay during grace. The
  [design](document-transfers.md) records persisted acknowledgements and a
  conservative recovery path when Paperless acceptance is uncertain.
- `derived`: keep the inline default and pagination unchanged. File delivery
  removes the need to read an entire document merely to copy it; changing how
  much text a reader sees by default needs its own rationale.

### 2026-09-17

- The Paperless 3.x known unknown is answered and struck through rather than
  deleted, because the argument for *why* it was research rather than a feature
  is the part worth keeping. `evidenced`: the appetite held, and the verdict
  moved direction in one concrete way — "move to payload version 10" was a
  plausible next step before the sweep and is now explicitly not one, since the
  only version-10 difference this client meets breaks tasks and buys nothing.
- The 63 unwrapped routes are deliberately **not** decomposed into a package
  here. `derived`: the roadmapping skill wants packages charted only as far as
  they can honestly be seen, and the inventory's own finding is that most of
  those routes are administrative surface this server has no stated user need
  for. Feature issues were opened for the three capabilities the evidence
  argues for; the rest stay an inventory in the reference, which is where a
  menu belongs.
- The long-running-calls known unknown is answered, and the answer contradicts
  the issue's own doubt. `evidenced`: `wait_for_task` blocks past its own
  default on 45% of observed API uploads, so the honest verdict is "warranted"
  rather than the "not needed yet" the issue anticipated. `derived`: two
  corrections to direction follow. First, the issue's three candidates are
  really one — Paperless returns from the upload and bulk-edit endpoints before
  the work they queue runs, so only the polling tool ever blocks, which shrinks
  the theme to a single pull request. Second, the binding deadline is the
  tool's own 60s default and not the client's 180s patience, so this was never
  the client-timeout problem ADR 0002 was written for; it is a tool-layer
  default meeting a queue. Third, that queue is self-inflicted: the first
  stated cause — ambient load from the frequent `mail_fetch` schedule — was
  **refuted** by the arrival gaps, which show one batch of 37 uploads queuing
  behind itself at ~1.2s intervals. `derived`: recording the refutation matters
  more than the correction did, because the wrong cause would have pointed the
  next reader at instance tuning, when what actually changes the exposure is
  how many documents a caller uploads at once — which
  [#111](https://github.com/pvliesdonk/paperless-mcp/issues/111) will increase,
  because it is the sibling that carries an upload path. `evidenced`: this
  entry first named [#112](https://github.com/pvliesdonk/paperless-mcp/issues/112)
  alongside it, which is the download side and cannot change how many consumes
  are queued; corrected under
  [#143](https://github.com/pvliesdonk/paperless-mcp/issues/143).
- The measurement deliberately did not run through this server's own
  `upload_document`. `derived`: that path carries file bytes as a base64 tool
  argument, which is exactly the shape
  [#111](https://github.com/pvliesdonk/paperless-mcp/issues/111) and
  [#112](https://github.com/pvliesdonk/paperless-mcp/issues/112) exist to
  replace, so timing it would have measured a transport on its way out. Reading
  the instance's own task history instead cost nothing, mutated nothing, and
  gave 4,133 records where an upload probe would have given one.

### 2026-09-16

- Index written for the first time; the file was the template's stub until now.
  Everything above is `derived` unless marked otherwise, and the epic and
  package below it were reconstructed from issues that already existed rather
  than charted before decomposition. That is backwards from how the skill wants
  an epic built, and it is worth saying plainly: the "Done when" for
  [#100](https://github.com/pvliesdonk/paperless-mcp/issues/100) was written
  after its children existed, so it is weaker evidence than one written before
  them. It was deliberately phrased from the epic's own "What changes for the
  user" rather than from the children, and it is frozen from here.
- No refinement issue was opened for
  [#100](https://github.com/pvliesdonk/paperless-mcp/issues/100). `derived`:
  the skill wants one from the moment an epic is created, and its definition of
  done is the coverage check, "feature issues exist that plausibly satisfy the
  epic's Done when". That check already holds, so a refinement issue opened now
  could only be closed immediately, and the trail of how often an epic was
  rethought is signal — a fabricated entry in it is not. Future epics get
  theirs at creation.
- Epic [#100](https://github.com/pvliesdonk/paperless-mcp/issues/100) carries no
  package. It was assigned to `010` while this index was first written and the
  owner removed it the same day. `derived`: that is the skill's default and the
  right call — the epic's own answer to "ships atomically" is *no*, so a package
  on it would claim a commitment the epic explicitly disclaims, and sub-issues
  inherit a parent's milestone at link time, which would have swept future
  children into a cut nobody decided on. The children carry the package
  individually instead.
- The earlier `v1.0.0` milestone was left as it stands. `evidenced` **at the
  time of writing, and no longer true**: it was version-named and open, which
  the skill's stop rules name as a violation, but its content had shipped and
  closing it read as a judgement about history rather than about direction. It
  was closed later the same day, at `2026-09-16T13:02:32Z`. The correction is
  recorded below rather than by rewriting this bullet, because how quickly an
  `evidenced` claim went stale is itself the useful signal.

### 2026-09-16 (triage pass, later the same day)

- The `v1.0.0` locator above stopped resolving within hours of being written.
  `evidenced`: `gh api repos/pvliesdonk/paperless-mcp/milestones/1` reports
  `state=closed`, `closed_at=2026-09-16T13:02:32Z`. `derived`: the lesson is
  not that the claim was careless but that the index should assert tracker
  state as rarely as possible — GitHub owns status, and every such sentence
  here is a hostage to it. Tracked as
  [#126](https://github.com/pvliesdonk/paperless-mcp/issues/126).
- `020 surface-legibility` was created and three issues committed to it. The
  index previously said "No package beyond `010` exists", which is the kind of
  sentence that goes stale by being true only on the day it is written; the
  Packages section now argues the sequence instead, and names the gate holding
  the next candidate back.
- `010`'s payload was completed rather than changed in intent. The closed
  #101, #102 and #105 were added to the milestone so it holds the whole
  platform move, matching what this index already claimed it was; the
  still-open [#123](https://github.com/pvliesdonk/paperless-mcp/issues/123) and
  [#126](https://github.com/pvliesdonk/paperless-mcp/issues/126) were committed
  to it deliberately, which means the major cut now waits on both. `derived`:
  taking the index correction into the same cut is the point — a release whose
  own roadmap misdescribes its packages is worse than one that waits an hour.
- [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113) and
  [#110](https://github.com/pvliesdonk/paperless-mcp/issues/110) became
  `research` issues with appetites (two days and one day). Both were filed on
  the Feature form and keep its headings; the appetite lives in a comment on
  each. `derived`: relabelling was the honest call because what each produces
  first is evidence, not software, and the skill refuses a research issue with
  no appetite — so the appetites were agreed before the labels were applied,
  not after.
- [#43](https://github.com/pvliesdonk/paperless-mcp/issues/43) was closed as
  obsolete, not duplicate. `evidenced`: it asked for a migration to
  `register_file_exchange()`, which left `fastmcp-pvl-core` at version 3; this
  repository is on 7.x and `tests/test_smoke.py` now asserts that scaffolding
  stays absent. Its successor on the transfer subsystem is
  [#111](https://github.com/pvliesdonk/paperless-mcp/issues/111). It was part
  of "the older backlog that predates this index" referred to above.
- The `enhancement` label was retired in place in favour of `feature`, which is
  what the issue forms emit. `derived`: retired rather than deleted because
  deletion strips the label from closed issues and destroys the historical
  attribution; a greyed-out label costs only picker noise.
