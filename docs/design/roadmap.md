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
([#110](https://github.com/pvliesdonk/paperless-mcp/issues/110)–[#114](https://github.com/pvliesdonk/paperless-mcp/issues/114)).
They are backlog: none has a package, and none has been decomposed. They cluster
into four candidate stories, listed with what would promote one to an epic
rather than with an order, because the ordering argument does not exist yet.

- **Getting bytes out of the context window** —
  [#111](https://github.com/pvliesdonk/paperless-mcp/issues/111) (files),
  [#112](https://github.com/pvliesdonk/paperless-mcp/issues/112) (content as a
  file). `stated`: scanned PDFs are consistently larger than a context window
  can take, so the file endpoints are unusable for the documents they exist for
  ([#111](https://github.com/pvliesdonk/paperless-mcp/issues/111)). Promoted by
  a size distribution from the deployed archive that says how much of it is
  actually unreachable, and by a decision on which of the two wiring paths the
  library offers this server should take. The two issues share one subsystem,
  so they are one story or neither.
- **What Paperless 3.x offers that this server does not** —
  [#113](https://github.com/pvliesdonk/paperless-mcp/issues/113). `stated`: the
  client was written against the 2.x API and Paperless has since shipped a
  major with AI-backed capabilities. Promoted by the written inventory that
  issue asks for; until then there is nothing to sequence, because which
  capabilities are worth exposing is exactly what is unknown. This is the one
  theme that plausibly needs a research issue with an appetite before any
  feature issue is honest.
- **Telling the model what instance it is on** —
  [#114](https://github.com/pvliesdonk/paperless-mcp/issues/114). `stated`: the
  composed instructions never name the Paperless instance, although the server
  knows it. Promoted by nothing external; it is small, self-contained and
  already shaped enough to be a feature rather than an epic. The likeliest
  outcome is that it joins a package without ever becoming one.
- **Calls that outlast a client's patience** —
  [#110](https://github.com/pvliesdonk/paperless-mcp/issues/110). `stated`,
  including its own doubt: "not sure there is anything (yet)". Promoted by
  measurements from the deployed instance showing a call that actually blocks
  long enough to matter. Absent those, the honest outcome is "not needed yet",
  recorded with the numbers.

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
  only decision left is whether the follow-ups ride along, and they are small,
  internal and nearly done.

No package beyond `010` exists. `derived`: the themes above have no order yet,
and the skill's horizon rule says create packages only as far ahead as you can
genuinely see them. An issue with no milestone is backlog, sitting under its
epic or on its own; that includes everything in
[#110](https://github.com/pvliesdonk/paperless-mcp/issues/110)–[#114](https://github.com/pvliesdonk/paperless-mcp/issues/114)
and the older backlog that predates this index.

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
  that issue's inventory. If it turns out to decide scope for a whole package
  rather than for one feature, it should become a research issue with an
  appetite before any feature issue is written; nothing has established that yet.
- **Whether any Paperless call on the deployed instance blocks long enough to
  need a job.** `stated` in
  [#110](https://github.com/pvliesdonk/paperless-mcp/issues/110), with the
  owner's own "not sure". Resolved by that issue. Recording it is enough: not
  knowing changes nothing about what happens next, because nothing is waiting
  on the answer.
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
- The earlier `v1.0.0` milestone was left as it stands. `evidenced`: it is
  version-named and open, which the skill's stop rules name as a violation, but
  its content has shipped and closing it is a judgement about history rather
  than about direction.
