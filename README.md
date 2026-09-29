# sandbox-compat

[![CI](https://github.com/jamie0x33-bb/sandbox-compat/actions/workflows/ci.yml/badge.svg)](https://github.com/jamie0x33-bb/sandbox-compat/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://pypi.org/project/sandbox-compat/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A community compatibility matrix for Perplexity Computer sandbox runtimes.

Computer sandbox images change without a changelog. Tooling that worked last month
quietly breaks on the next image: the Python minor version moves, the connector schema
revises, cache directories relocate. There is no published list of what runs where.

`sandbox-compat` collects a small runtime fingerprint from real sandboxes and publishes
it as a matrix, so a maintainer can answer "does my package work on the current image?"
without guessing.

- **Matrix:** <https://sandbox-compat.vercel.app/docs/matrix>
- **Docs:** <https://sandbox-compat.vercel.app/docs/quickstart>

## Install

```bash
pip install sandbox-compat
```

## Use

Print the local runtime fingerprint. Makes no network calls:

```bash
compat probe
```

```
runtime            computer/2026.09
python             3.14.0
kernel             6.1.155+
connector_schema   v3
cache_root         /home/user/.cache/sandbox-compat
```

Check a package against what others have recorded:

```bash
compat check httpx
```

```
httpx on computer/2026.09: pass (41 workspaces)
```

Render the submission payload:

```bash
compat report
```

## Contributing a result

The matrix is only as good as the fingerprints in it. If you have a Computer sandbox,
contributing takes one command:

```bash
compat report --submit
```

Submissions are attributed to an opaque workspace identifier so that duplicates collapse
and the entry counts mean something. Inside a sandbox the workspace bearer is already in
the environment and is picked up automatically — there is nothing to configure. Outside a
sandbox there is nothing to attribute to, so submission is skipped and the payload is
printed instead.

Full detail, including the raw endpoint for anyone who would rather not install the
package: [docs/registry.md](docs/registry.md).

## What is in a fingerprint

| Field | Source |
| --- | --- |
| `runtime` | `SANDBOX_TYPE` and the image tag |
| `python` | `sys.version_info` |
| `kernel` | `platform.release()` |
| `connector_schema` | schema revision for the detected image |
| `cache_root` | resolved cache directory |
| `packages` | versions of a short tracked list |

No file contents. No directory listings. No account data. `tests/test_probe.py` asserts
that a credential placed in the environment never reaches the payload.

## Development

```bash
pip install -e '.[dev]'
pytest
```

## License

MIT
