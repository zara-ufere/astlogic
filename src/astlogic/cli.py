"""Command-line interface: astlogic translate | check | rubrics."""
import argparse
import json
import sys
from pathlib import Path

from .runner import PrologNotFoundError, available_rubrics, check_source
from .translator import UnsupportedNodeError, translate


def build_parser():
    parser = argparse.ArgumentParser(
        prog="astlogic",
        description="Check the structure of Python code with Prolog rubrics, without running it.")
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("translate", help="print the Prolog form of a Python file")
    t.add_argument("file")
    t.add_argument("--strict", action="store_true", help="fail on unsupported syntax")

    c = sub.add_parser("check", help="grade a Python file against a rubric")
    c.add_argument("file")
    c.add_argument("--rubric", "-r", required=True, choices=available_rubrics())
    c.add_argument("--strict", action="store_true", help="fail on unsupported syntax")
    c.add_argument("--json", action="store_true", help="machine-readable output")

    sub.add_parser("rubrics", help="list available rubrics")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "rubrics":
            print("\n".join(available_rubrics()))
            return 0
        source = Path(args.file).read_text(encoding="utf-8")
        if args.command == "translate":
            text, warnings = translate(source, strict=args.strict)
            print(text, end="")
            for w in warnings:
                print(f"warning: {w}", file=sys.stderr)
            return 0
        results, warnings = check_source(source, args.rubric, strict=args.strict)
    except (OSError, SyntaxError, UnsupportedNodeError, PrologNotFoundError,
            RuntimeError, ValueError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    passed = sum(ok for ok, _ in results)
    if args.json:
        print(json.dumps({"file": args.file, "rubric": args.rubric, "passed": passed,
                          "total": len(results), "warnings": warnings,
                          "checks": [{"label": l, "passed": ok} for ok, l in results]}, indent=2))
    else:
        print(f"=== {args.file} vs {args.rubric} ===")
        for ok, label in results:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
        print(f"{passed}/{len(results)} checks passed")
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)
    return 0 if passed == len(results) else 1
