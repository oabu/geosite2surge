#!/usr/bin/env python3
"""Standalone script to generate or update the web catalog index.html in dist/."""

import argparse
import os
import sys

from converter.web_generator import generate_html_catalog


def main():
    parser = argparse.ArgumentParser(
        description="Generate Surge rules interactive web catalog (index.html)"
    )
    parser.add_argument(
        "--dist-dir",
        type=str,
        default="./dist",
        help="Path to dist directory containing geosite/ and geoip/ folders",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output index.html (default: <dist-dir>/index.html)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.dist_dir):
        print(f"[!] Error: {args.dist_dir} does not exist. Run convert.py first.", file=sys.stderr)
        sys.exit(1)

    out_path = args.output or os.path.join(args.dist_dir, "index.html")
    generate_html_catalog(args.dist_dir, out_path)
    print(f"[✓] Web catalog ready at: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    main()
