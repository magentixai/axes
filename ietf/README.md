# AXES Internet-Draft: draft-sansone-axes-evidence-envelope-00

**AXES: A Recomputable Evidence Envelope for Autonomous Execution** is the IETF Internet-Draft that describes the settled parts of AXES. This is revision -00, prepared for IETF 127, whose cut-off for new drafts is Monday 2 November 2026 at 23:59 UTC.

**[Read the draft (HTML)](https://htmlpreview.github.io/?https://github.com/magentixai/axes/blob/main/ietf/draft-sansone-axes-evidence-envelope-00.html)** · [Plain text](draft-sansone-axes-evidence-envelope-00.txt) · [XML (upload file)](draft-sansone-axes-evidence-envelope-00.xml) · [Source (Markdown)](draft-sansone-axes-evidence-envelope.md)

GitHub shows an HTML file as source code, so the HTML link above opens it through htmlpreview.github.io. To read it offline, download [`draft-sansone-axes-evidence-envelope-00.html`](draft-sansone-axes-evidence-envelope-00.html) (use "Download raw file") and open it in any browser. Once the draft is accepted, the IETF Datatracker copy at <https://datatracker.ietf.org/doc/draft-sansone-axes-evidence-envelope/> is the copy of record.

## What the draft covers

The draft specifies the parts of AXES that are settled:

- a canonical byte form (RFC 8785) and hash scope for the evidence record, the Standards Envelope;
- a hash chain over a declared stream of envelopes;
- an anchoring block whose strength is earned from a verifiable proof, not asserted;
- a four-state result vocabulary for verification (`verified`, `contradicted`, `indeterminate`, `not_evaluated`);
- requirement profiles that a relying party applies to evidence to produce a deterministic evaluation record.

It also names what is not yet settled, including the full envelope schema and the exact construction for redaction-tolerant hashing, and records the chosen direction for redaction (salted per-field hash commitments, following SD-JWT). It is an Informational draft: it offers AXES as one input format to format-neutral audit readers, not as a replacement for other record formats.

## Files in this folder

| File | What it is | Committed |
|---|---|---|
| [`draft-sansone-axes-evidence-envelope.md`](draft-sansone-axes-evidence-envelope.md) | The source, in kramdown-rfc Markdown. Edit this, never the rendered files. | Yes |
| [`draft-sansone-axes-evidence-envelope-00.xml`](draft-sansone-axes-evidence-envelope-00.xml) | The RFC XML v3 file. **This is the file uploaded to the Datatracker.** | Yes |
| [`draft-sansone-axes-evidence-envelope-00.html`](draft-sansone-axes-evidence-envelope-00.html) | The human-readable HTML rendering, with a table of contents and links. | Yes |
| [`draft-sansone-axes-evidence-envelope-00.txt`](draft-sansone-axes-evidence-envelope-00.txt) | The paginated plain-text rendering, which idnits checks. | Yes |
| [`appendix/`](appendix/) | The worked example and CDDL that the draft's appendices quote, checked byte for byte by [`check_appendices.py`](check_appendices.py). | Yes |
| [`BUILD.md`](BUILD.md) | How to rebuild the draft, the tool versions and the expected idnits result. | Yes |
| Other `.xml`, `.txt` and `.html` files | Intermediate build output. | No (ignored) |

## The submitted build

The three -00 files were built on 1 November 2026 from the source on `main` after the merge of PR #22, with the author's country (Mauritius) added so the Datatracker needs no metadata edits, with the tools listed in [BUILD.md](BUILD.md). The draft is dated 1 November 2026 and expires on 5 May 2027. Its rendered text is 2,800 lines, the v2 and v3 renderings are identical, and idnits 3.3.0 reports the expected one warning and three comments.

| File | SHA-256 |
|---|---|
| `draft-sansone-axes-evidence-envelope-00.xml` | `78ab0600f257da721c5470652e796a694ded13f62526ee13be150af25238f45f` |
| `draft-sansone-axes-evidence-envelope-00.txt` | `7b83ef460e646cad2e31f66e99ce90f2ac73550e40f9f0aa69b104eb66b5bc39` |
| `draft-sansone-axes-evidence-envelope-00.html` | `db026f5e740eb4eaeef3726ea3767567f392ec7c223bb7358820f4161bb8bbd2` |

Git keeps these files byte for byte on every platform (`.gitattributes`), so the hashes hold on any checkout. A rebuild on another day gives a different date and may pick up newer reference metadata from the Datatracker, so it will not match these hashes; that is expected, and the committed files are the ones submitted.

## Submitting

Upload `draft-sansone-axes-evidence-envelope-00.xml` at <https://datatracker.ietf.org/submit/>. The Datatracker renders its own text and HTML from it, and its rendered text should match `draft-sansone-axes-evidence-envelope-00.txt`.

## Relation to the rest of this repository

The draft describes AXES; it is not a second specification. If the draft and the documents in this repository disagree, please report it as an issue. The reference tools in [`tools/`](../tools/), the published vectors in [`vectors/`](../vectors/) and the Python SDK in [`sdk/python/`](../sdk/python/) are the implementations the draft's Implementation Status section describes. Comments on the draft are welcome as GitHub issues here, or on the Datatracker once it is posted.
