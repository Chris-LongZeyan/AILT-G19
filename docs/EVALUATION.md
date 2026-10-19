# Evaluation status

Updated 19 October 2026. These results are for synthetic examples only.

| Check | Result |
|---|---|
| Automated Python/UI suite | 60 passed locally; full CI suite passed with both PostgreSQL integration tests |
| PostgreSQL integration test | Passed against PostgreSQL 17 in CI |
| Known-match keyword top-3 hit rate | 10/10 |
| Keyword no-match cases | 0/4 |
| Ambiguous cases handled before model call | 2/2 |
| Ownership/contact boundary cases | 2/2 |
| Invalid-input cases | 2/2 |
| Qwen Flash known-match top-3 hit rate | 10/10 |
| Qwen Flash no-match cases | 4/4 |
| Qwen input guards (ambiguous/boundary/invalid) | 6/6; no provider call for these cases |
| Human evidence review | Pending |
| Two-classmate usability study | Pending |

Keyword search uses shared lowercase words (including place labels/full names) and ID tie-breaking, with a
maximum of three positive-score results. Common words and incidental colours can
produce unsuitable suggestions. The four no-match failures are a baseline
limitation. Qwen rejected those four queries in the measured run; this does not
establish performance on real or unseen items.

The suite exercises request shape, ID allowlisting, duplicate rejection, excessive
matches, evidence provenance, malformed response envelopes, oversized responses,
timeouts, provider errors, absent keys, category filtering, persistence and UI
interactions. Mocked model responses validate integration behaviour, not model
quality.

## Reproduce

Run `python -m evaluation.run --mode keyword`. It writes
`evaluation/results/latest.json` including the dataset SHA-256, prompt SHA-256,
timestamp and all synthetic results. Results are ignored by Git by default.
Explicitly review any report before including it in the private course submission.

The 20-query candidate set contains 10 known matches, four no-matches, two
ambiguous cases, two boundary cases and two invalid inputs. A second team member
must review acceptable IDs and expected statuses before freezing the final set.
The initial set was created with AI assistance and has already been used for a
baseline run. The Qwen prompt and evidence capitalization handling were improved
using this development set during integration. If the team
requires a completely unseen final set, replace it before final evaluation.

## Manual AI review

For every model result, record whether the item is a plausible match, each quote
is relevant, contradictory features are respected, and no ownership claim is
implied. Exact-source checks alone do not answer those questions. Record the
provider, model, prompt version, dataset version and evaluation date.

Targets from the proposal: at least 9/10 known-match top-3 hits, 4/4 appropriate
no-matches, 2/2 clarification outcomes, and all boundary/invalid cases safely
handled. The final Qwen development run meets these counts; independent
validation and human evidence review are still required for broader claims.

## Usability protocol

Give two classmates only the README and the supplied fictional query. Ask each
to start the app and identify a possible match within five minutes. Record
anonymous participant labels, completion time, success and encountered issues.
Do not fabricate completion results or record personal details.

## Earlier build and deployment (historical)

CI run https://github.com/Chris-LongZeyan/AILT-G19/actions/runs/36970092520
passed 45 tests in 1.67 seconds and built the Docker image. The deployed
application code is commit 072f3b0. Render built and started it successfully
on 2 October 2026 at about 13:46 Asia/Shanghai.

Public app: https://campus-find-g19.onrender.com

Browser checks verified the 30-record catalogue indicator, the supplied keyword
query returning LF-001 first, refusal of an ownership request, blank-input handling, and the explicit missing-key AI message. Real AI
accuracy was unmeasured in that historical release.

## Staff inventory verification

The new suite covers account roles, session expiry/revocation, login lockout,
photo validation, legacy-schema migration, place filters and collection removal.
A browser-added synthetic record and photo were recovered through an independent
Neon PostgreSQL connection. Staff collection removes both, and startup does not
recreate them. Local UI tests cover student search and explicit staff confirmation.
The existing 20-query benchmark was rerun unchanged; it does not evaluate location
retrieval quality. The later Qwen run below measures AI on the original set.

Current staff-inventory CI: https://github.com/Chris-LongZeyan/AILT-G19/actions/runs/36978530394 (cf8cadd).

## Qwen integration run, 19 October 2026

Provider: Qwen, Beijing; model: `qwen-flash`; thinking disabled; temperature 0;
prompt: `grounded-v3-source-only`. Both final AI and keyword reports are retained
in `docs/evidence/` with timestamps, dataset/prompt hashes and all 20 case results.

The final run made 14 real model calls. Ten known-item queries returned the
expected ID with source-verified evidence; four absent/contradictory descriptions
returned no match. Six ambiguous, boundary and invalid cases were handled by
application guards before any API call. The keyword comparison passed 16/20,
including 10/10 known matches, but returned unsuitable items in all four
no-match cases. Overall application outcomes were 20/20 for the final Qwen run.

An initial integration run passed only 1/10 known matches because case-only
quote differences were rejected. The final implementation restores source
capitalization while still rejecting changed wording and duplicate evidence.
A preliminary response also copied a query phrase; the prompt now explicitly
requires evidence from the selected record. The initial failed report is retained.
These fixes used the same queries, so this is a development/regression evaluation,
not an unseen benchmark. No result or expected answer was manually altered.

The standalone page embeds an actual local UI run against SQLite with a real
Qwen response. Independent team evidence review, new-query tests, location
retrieval evaluation and the two-classmate usability exercise remain pending.

Qwen release CI passed (including PostgreSQL and Docker build):
https://github.com/Chris-LongZeyan/AILT-G19/actions/runs/39198290254
Code commit: `bcb3143`.
