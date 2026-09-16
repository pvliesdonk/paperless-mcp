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
  a size distribution from the deployed archive that says how much of it is
  actually unreachable, and by a decision on which of the two wiring paths the
  library offers this server should take. #111 and #112 share one subsystem, so
  they are one story or neither; #35 is `derived` as the same story's inline
  half and needs neither that subsystem nor that decision, which is why it
  could be committed to `020` on its own.
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
  including its own doubt: "not sure there is anything (yet)". Also now a
  `research` issue, with a one-day appetite that goes past measurement into a
  spike wiring the Jobs framework for one tool, so that a "not needed yet"
  verdict records the cost of the integration and not only its absence.

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
while the bytes work is gated on a design decision nobody has made — which of
the library's two transfer wirings this server takes. Committing a cut to work
whose shape is undecided is what the horizon rule exists to prevent.

No package beyond `020` exists. `derived`: the horizon rule says create
packages only as far ahead as you can genuinely see them, and the next
candidate — #111 with #112 — is behind that undecided wiring path. An issue
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
  text records the gap. Not a separate research issue: the measurement is the
  first step of that work, not a question that decides whether to start it.
- **Which of the library's two transfer wirings fits this server.** `derived`.
  Resolved by [#111](https://github.com/pvliesdonk/paperless-mcp/issues/111).
- **What the Paperless 3.x API adds, and what its newer payload version changes
  in what this client already parses.** `stated` in
  [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113). Resolved by
  that issue, now a `research` issue carrying a two-day appetite. The earlier
  condition — "if it turns out to decide scope for a whole package rather than
  for one feature" — was met: it decides which capabilities are worth exposing
  at all, so no feature issue beneath this theme would have been honest before
  the inventory exists. One facet is already pinned, and pinned in the repo
  rather than in the tracker: `evidenced`,
  `docs/design/reference/paperless-version-endpoints.md` records
  `[source: pngx-settings]` that `ALLOWED_VERSIONS` is `["9", "10"]` with
  `DEFAULT_VERSION` `"10"` while this client pins `version=9`, and scopes the
  payload difference to #113. That page reached `main` with #127 while this
  correction was in review — which is exactly the repoint the skill asks for
  when research output moves from working memory to the record.
- **Whether any Paperless call on the deployed instance blocks long enough to
  need a job.** `stated` in
  [#110](https://github.com/pvliesdonk/paperless-mcp/issues/110), with the
  owner's own "not sure". Resolved by that issue, now a `research` issue
  carrying a one-day appetite. This entry previously read "recording it is
  enough: not knowing changes nothing about what happens next". `derived`: that
  is no longer the honest framing. Committing an appetite is a decision to find
  out, so the question is now scheduled work rather than a noted unknown — a
  change in what we intend, not in what we know.
- **Whether a required domain configuration field becomes expressible upstream,
  and whether the resolved config can reach tool registration.** `evidenced`:
  both are worked around in this repository and filed as
  pvliesdonk/fastmcp-server-template#621 and
  pvliesdonk/fastmcp-server-template#622. Resolved by those issues. Recording
  them is enough; neither blocks anything here, and the workarounds are
  documented in `config.md` beside this file.

## Revisions

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
