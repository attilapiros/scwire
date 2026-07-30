import argparse
import json

from .parser import extract_entries
from .renderer import build_html


def print_text(entries):
    for e in entries:
        print(f"{e['timestamp']} INFO LoggingInterceptor: {e['direction']} {e['rpc']}")
        if e["payload"]:
            print(json.dumps(e["payload"], indent=2))
        print()


def main():
    parser = argparse.ArgumentParser(description="Parse Spark Connect LoggingInterceptor logs")
    parser.add_argument("log", nargs="?", help="Path to log file")
    parser.add_argument("--html", metavar="OUT", help="Write Mermaid HTML to this file")
    args = parser.parse_args()

    entries = extract_entries(args.log)

    if args.html:
        html = build_html(entries, args.log)
        with open(args.html, "w") as f:
            f.write(html)
        print(f"Written: {args.html}  ({len(entries)} events)")
    else:
        print_text(entries)
