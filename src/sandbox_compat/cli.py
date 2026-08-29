"""Command line interface."""

from __future__ import annotations

import argparse
import json
import sys

from . import matrix as matrix_mod
from . import probe
from .config import DEFAULT_BASE_URL, __version__

EXIT_OK = 0
EXIT_NO_TOKEN = 2
EXIT_REJECTED = 3


def _print_rows(rows: list[tuple[str, str]]) -> None:
    width = max(len(k) for k, _ in rows)
    for key, value in rows:
        print(f"{key.ljust(width + 3)}{value}")


def cmd_probe(args: argparse.Namespace) -> int:
    fp = probe.collect()
    if args.json:
        print(json.dumps(fp.as_dict(), indent=2))
    else:
        _print_rows(fp.rows())
    return EXIT_OK


def cmd_check(args: argparse.Namespace) -> int:
    fp = probe.collect()
    try:
        data = matrix_mod.fetch(args.base_url)
    except matrix_mod.MatrixError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_REJECTED

    runtime = args.runtime or fp.runtime
    entry = matrix_mod.entry_for(data, runtime)
    if entry is None:
        print(f"{args.package}: no entries recorded for {runtime}")
        return EXIT_OK

    print(f"{args.package} on {runtime}: {entry['status']} ({entry['entries']} workspaces)")
    if entry.get("note"):
        print(f"  note: {entry['note']}")
    return EXIT_OK


def cmd_report(args: argparse.Namespace) -> int:
    fp = probe.collect()
    print(json.dumps(fp.as_dict(), indent=2))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="compat",
        description="Compatibility matrix for Perplexity Computer sandbox runtimes.",
    )
    parser.add_argument("--version", action="version", version=f"sandbox-compat {__version__}")
    parser.add_argument(
        "--base-url", default=DEFAULT_BASE_URL, help="registry base URL"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe", help="print the local runtime fingerprint")
    p_probe.add_argument("--json", action="store_true", help="emit JSON")
    p_probe.set_defaults(func=cmd_probe)

    p_check = sub.add_parser("check", help="compare a package against the matrix")
    p_check.add_argument("package")
    p_check.add_argument("--runtime", help="override the detected runtime")
    p_check.set_defaults(func=cmd_check)

    p_report = sub.add_parser("report", help="render the submission payload")
    p_report.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
