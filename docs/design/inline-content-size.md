# How large is a document's inline content

Internal design note. Not published; not Vale-linted.

Written for [#35](https://github.com/pvliesdonk/paperless-mcp/issues/35), which
asked for a cap on `get_document_content` and proposed 50,000 characters as the
value. The issue said plainly that sizes were not measured
([#112](https://github.com/pvliesdonk/paperless-mcp/issues/112) marks the same
claim `[unverified]`). They are measured here, and the proposed number turned
out to sit in the wrong place.

## Verdict

**Cap every inline preview at 20,000 characters, and keep paging.**

The first implementation shipped 50,000 characters before transfer links
existed. PR #155 added full OCR Markdown downloads outside model context. That
removed the earlier lower bound, so #149 sets a hard 20,000-character
characters, roughly 2,700 tokens at the measured median and 5,000 at a
pessimistic 4:1 ratio.

The number is chosen as a *token budget*, not to fit any particular document.
That distinction is the point of this note: no cap that a context window can
afford also fits the documents in this archive, so a cap cannot be justified by
the fraction of documents it returns whole. What it is for is the tail.

**A cap that fires often is the intended behaviour, given paging.** At 20,000
characters about a quarter of this archive arrives whole and
the rest arrives in sections. An earlier draft of this note argued for 100,000
on the grounds that a default firing on half the archive "is not a safety rail,
it is the normal path". That objection holds only in a world without `offset`:
once continuation exists, the cost of the cap firing is one more call, while
the cost of it not firing is a flooded context. The asymmetry is the whole
argument, and it points at the smaller number.

## The measurement

All 244 documents on the deployed archive, `len(content)` from
`/api/documents/?fields=id,content`, 2026-09-18.

| percentile | characters | ≈ tokens |
|---|---|---|
| min | 31 | — |
| p25 | 23,527 | ~3,200 |
| p50 | 88,080 | ~12,100 |
| p75 | 225,831 | ~30,900 |
| p90 | 725,258 | ~99,400 |
| p95 | 1,100,869 | ~150,900 |
| p99 | 2,145,867 | ~294,000 |
| max | 2,407,894 | ~330,000 |

Mean 232,421; median 2,912 characters per page over the 214 documents that
report a page count, whose own page counts run to a median of 32 and a maximum
of 1,009.

Two facts do the work:

- **The tail genuinely exceeds a context window.** The largest document — a
  1,009-page TPM 2.0 library specification — is about 330,000 tokens on its
  own. It cannot be read inline at any cap, capped or not; the cap's job is to
  fail it legibly rather than by flooding.
- **Every affordable cap fires on most of this archive.** At 88,080 characters
  the median document exceeds each candidate below, so "which cap returns most
  documents whole" has no good answer and is the wrong question. The right one
  is how much context a single call may spend, which is what makes paging the
  load-bearing half of this change rather than an extension of it.

Coverage at candidate caps, as a share of documents returned *complete*:

| cap | complete |
|---|---|
| 20,000 | 23.8% |
| 50,000 | 36.5% |
| 100,000 | 53.7% |
| 200,000 | 71.7% |

## Why paging is not optional

#35 filed `offset` as a deferred extension. The distribution says otherwise: at
the original 50,000-character cap, 63.5% of this archive was returned
partially, and without `offset` that content is **unreachable** — the caller
can see that text was cut and has no way to read the rest. A cap alone
therefore replaces one failure (context flooded) with a worse one (document
silently unreadable past its first section). `offset` ships with the cap.

The dependency runs the other way too, and it is why the cap could be set
defensively rather than generously: paging is what makes a small cap cheap. A
cap without continuation must be generous enough to be *sufficient*; a cap with
continuation only has to be affordable.

## Caveats, stated rather than buried

- **This archive is not a typical one.** It is technical standards and eBooks —
  TOGAF, DAMA-DMBOK, the Handbook of Applied Cryptography — at ~2,900
  characters per page. A household Paperless archive of receipts and letters
  would rarely reach any of these caps. What generalises is the shape (a fat
  tail that no context window survives), not the median.
- **The token figures are a proxy.** 7.30 characters per token is the median
  over 25 real OCR samples under `cl100k_base`, ranging 3.66–9.21. That is not
  Claude's tokenizer; treat the ratio as an order-of-magnitude check, which is
  all the cap needs.
- **The cap is a rail, not the answer.** PR #155 closed
  [#112](https://github.com/pvliesdonk/paperless-mcp/issues/112) with a full OCR
  Markdown transfer. On deployments without transfer links, offset paging still
  reaches every part of the document. Inline resources and structured document
  responses cannot override or bypass the preview boundary.

## Beyond #35

The roadmap's bytes theme says the
[#111](https://github.com/pvliesdonk/paperless-mcp/issues/111)/#112 story is
promoted by "a size distribution from the deployed archive that says how much of
it is actually unreachable". For the text half, that distribution is the table
above: **76.2% of documents exceed the 20,000-character cap now used,
and the top decile exceeds a whole context window.** This note does not re-open the
sequencing argument; it records the evidence that was missing.
