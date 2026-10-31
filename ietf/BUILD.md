# Building draft-sansone-axes-evidence-envelope

The source is `draft-sansone-axes-evidence-envelope.md` (kramdown-rfc). Appendix files are in `appendix/` and are checked by `check_appendices.py`. Continuous integration (`.github/workflows/sdk-and-ietf.yml`) runs every step below except the upload.

## Tools used for the -00

| Tool | Version |
|---|---|
| Ruby | 3.3 |
| kramdown-rfc | 1.7.43 |
| cddl (Ruby gem) | 0.12.14 |
| xml2rfc | 3.35.0 |
| idnits | `@ietf-tools/idnits` 3.3.0 via npx |
| Python | 3.9 or later, with `requirements-dev.txt` |

## Steps

From the repository root:

```bash
python ietf/check_appendices.py
```

From `ietf/`:

```bash
kramdown-rfc draft-sansone-axes-evidence-envelope.md > draft-sansone-axes-evidence-envelope.xml
xml2rfc --v2v3 draft-sansone-axes-evidence-envelope.xml -o draft-sansone-axes-evidence-envelope-00.xml
xml2rfc --text --html draft-sansone-axes-evidence-envelope-00.xml
npx --yes @ietf-tools/idnits@3.3.0 draft-sansone-axes-evidence-envelope-00.txt
```

kramdown-rfc writes the older v2 vocabulary even when asked for v3, so the upload copy is converted with xml2rfc's own `--v2v3`. Rendering the v2 output and the converted v3 file to text must give identical bytes; CI checks this.

The build fills the date from the day it runs and fetches I-D references from the datatracker, so two builds on different days differ in those places. Record the SHA-256 of the three upload files, with the source commit, in the PR or release note when the draft is submitted.

## Expected idnits result

One warning, kept on purpose: RFC 6962 is cited alongside RFC 9162, which obsoletes it, because the text explains that relationship. Three comments: two non-ASCII letters in a contributor's name, the spelling "Time-Stamp" in the title of RFC 3161, and the style of RFC reference URLs that xml2rfc generates.
