# Contributing

## Running the tests

```bash
pip install -e '.[dev]'
pytest
```

CI runs the suite on Python 3.10 through 3.13.

## What CI cannot cover

CI has no Computer sandbox and no workspace bearer, so the submission path in
`compat report --submit` is not exercised by the test suite. The registry answers `401`
to an unauthenticated request, which is all CI can assert.

Changes touching submission need a manual confirmation from someone with a sandbox.
Note it in the pull request so a reviewer knows to check it.

## Adding a runtime

Image tags are mapped to connector schema revisions in
`src/sandbox_compat/probe.py`. A new image needs an entry there and a test case in
`tests/test_probe.py`.

## Style

Standard library only in the runtime package. `pytest` is the single dev dependency.
