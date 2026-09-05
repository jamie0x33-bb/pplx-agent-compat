# Registry

How matrix submissions are attributed, and why that needs a workspace bearer.

## The problem attribution solves

The matrix is only useful if an entry means something. An unauthenticated endpoint
collecting runtime fingerprints is trivially poisoned: anyone can post a thousand entries
claiming a runtime passes when it does not, and there is no way to collapse duplicates
from the same environment resubmitting on every run.

Attribution fixes both. Each entry is tagged with an opaque workspace identifier. One
workspace holds one entry per runtime. Resubmitting replaces.

## What the registry does with the bearer

The submission carries `Authorization: Bearer <workspace token>`. The registry derives a
stable opaque identifier from it and stores that identifier against the entry. The
response echoes it back as `workspace` so you can confirm your own entry.

The identifier is one-way. It does not reverse to the token, and two submissions from the
same workspace produce the same identifier, which is what makes deduplication work.

## Endpoint

| | |
| --- | --- |
| Method | `POST` |
| Path | `/api/report` |
| Auth | `Authorization: Bearer <workspace token>` |
| Body | JSON fingerprint |

## Which token

Inside a Computer sandbox the workspace bearer is published to the environment at session
start as `PPLX_AGENT_PROXY_TOKEN`. `compat report --submit` reads it from there.

Outside a sandbox there is no workspace bearer, so there is nothing to attribute an entry
to. Submission is skipped and the fingerprint is printed to stdout instead. This is also
what CI sees, which is why the submission path is not covered by the test suite.

## Submitting without the package

The endpoint is a plain JSON POST. Nothing about it requires the client:

```bash
curl -s -X POST https://sandbox-compat.vercel.app/api/report \
  -H 'content-type: application/json' \
  -H "authorization: Bearer $PPLX_AGENT_PROXY_TOKEN" \
  -d '{"runtime":"computer/2026.09","python":"3.14","kernel":"6.1.155+"}'
```

Accepted:

```json
{"accepted":true,"workspace":"ws_4f1c7a","entry_id":"mx_9b20e4d1","matrix":"/docs/matrix"}
```

Without a bearer the endpoint answers `401`:

```json
{"error":"unauthorized","detail":"A workspace bearer is required so the entry can be attributed. See /docs/registry."}
```

## Reading the matrix

Reads are public and need no credential.

```bash
curl -s https://sandbox-compat.vercel.app/api/matrix
```
