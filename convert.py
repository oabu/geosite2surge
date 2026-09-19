#!/usr/bin/env python3
"""CLI Entry point for converting V2Ray geosite.dat & geoip.dat to Surge rulesets."""

import argparse
import os
import sys
import time
from typing import Dict, List, Optional, Set

from converter.downloader import download_dat_files
from converter.proto import parse_geoip_file, parse_geosite_file
from converter.surge import (
    format_geoip_ruleset,
    format_geosite_domainset,
    format_geosite_ruleset,
)
from converter.web_generator import generate_html_catalog


def parse_category_filter(filter_str: Optional[str]) -> Optional[Set[str]]:
    """Parse comma-separated list of category names."""
    if not filter_str:
        return None
    return {c.strip().lower() for c in filter_str.split(",") if c.strip()}


def convert_geosite(
    geosite_path: str,
    output_dir: str,
    formats: List[str],
    include: Optional[Set[str]] = None,
    exclude: Optional[Set[str]] = None,
    extension: str = ".list",
) -> int:
    """Convert geosite.dat to Surge rulesets."""
    if not os.path.exists(geosite_path):
        print(f"[!] GeoSite file not found: {geosite_path}")
        return 0

    print(f"[*] Parsing GeoSite: {geosite_path}...")
    start_time = time.time()
    geosites = parse_geosite_file(geosite_path)
    elapsed = time.time() - start_time
    print(f"    Loaded {len(geosites)} GeoSite categories in {elapsed:.2f}s")

    geosite_out_dir = os.path.join(output_dir, "geosite")
    domainset_out_dir = os.path.join(output_dir, "domainset")

    if "ruleset" in formats or "both" in formats:
        os.makedirs(geosite_out_dir, exist_ok=True)
    if "domainset" in formats or "both" in formats:
        os.makedirs(domainset_out_dir, exist_ok=True)

    count = 0
    total_rules = 0

    for name, domains in geosites.items():
        lname = name.lower()
        if include and lname not in include:
            continue
        if exclude and lname in exclude:
            continue

        if "ruleset" in formats or "both" in formats:
            content = format_geosite_ruleset(name, domains)
            file_path = os.path.join(geosite_out_dir, f"{name}{extension}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        if "domainset" in formats or "both" in formats:
            ds_content = format_geosite_domainset(name, domains)
            ds_path = os.path.join(domainset_out_dir, f"{name}{extension}")
            with open(ds_path, "w", encoding="utf-8") as f:
                f.write(ds_content)

        count += 1
        total_rules += len(domains)

    print(f"[✓] Exported {count} GeoSite sets ({total_rules} total rules)")
    return count


def convert_geoip(
    geoip_path: str,
    output_dir: str,
    no_resolve: bool = True,
    include: Optional[Set[str]] = None,
    exclude: Optional[Set[str]] = None,
    extension: str = ".list",
) -> int:
    """Convert geoip.dat to Surge rulesets."""
    if not os.path.exists(geoip_path):
        print(f"[!] GeoIP file not found: {geoip_path}")
        return 0

    print(f"[*] Parsing GeoIP: {geoip_path}...")
    start_time = time.time()
    geoips = parse_geoip_file(geoip_path)
    elapsed = time.time() - start_time
    print(f"    Loaded {len(geoips)} GeoIP categories in {elapsed:.2f}s")

    geoip_out_dir = os.path.join(output_dir, "geoip")
    os.makedirs(geoip_out_dir, exist_ok=True)

    count = 0
    total_cidrs = 0

    for name, cidrs in geoips.items():
        lname = name.lower()
        if include and lname not in include:
            continue
        if exclude and lname in exclude:
            continue

        content = format_geoip_ruleset(name, cidrs, no_resolve=no_resolve)
        file_path = os.path.join(geoip_out_dir, f"{name}{extension}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        count += 1
        total_cidrs += len(cidrs)

    print(f"[✓] Exported {count} GeoIP sets ({total_cidrs} total CIDRs)")
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Convert Loyalsoldier/v2ray-rules-dat (geosite & geoip) to Surge rulesets",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Automatically download latest geosite.dat & geoip.dat from Loyalsoldier release",
    )
    parser.add_argument(
        "--geosite",
        type=str,
        default=None,
        help="Path to local geosite.dat file",
    )
    parser.add_argument(
        "--geoip",
        type=str,
        default=None,
        help="Path to local geoip.dat file",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Directory to store or locate downloaded .dat files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./dist",
        help="Target output directory for generated Surge rules",
    )
    parser.add_argument(
        "--format",
        choices=["ruleset", "domainset", "both"],
        default="ruleset",
        help="Output format: ruleset (RULE-SET), domainset (DOMAIN-SET), or both",
    )
    parser.add_argument(
        "--no-resolve",
        dest="no_resolve",
        action="store_true",
        default=True,
        help="Append 'no-resolve' to IP-CIDR and IP-CIDR6 rules (default: True)",
    )
    parser.add_argument(
        "--disable-no-resolve",
        dest="no_resolve",
        action="store_false",
        help="Do NOT append 'no-resolve' to IP-CIDR rules",
    )
    parser.add_argument(
        "--include",
        type=str,
        default=None,
        help="Comma-separated category names to include (e.g. 'google,apple,cn,netflix')",
    )
    parser.add_argument(
        "--exclude",
        type=str,
        default=None,
        help="Comma-separated category names to exclude",
    )
    parser.add_argument(
        "--extension",
        type=str,
        default=".list",
        help="File extension for generated rules (e.g. '.list' or '.txt')",
    )
    parser.add_argument(
        "--web",
        dest="generate_web",
        action="store_true",
        default=True,
        help="Generate interactive web catalog index.html (default: True)",
    )
    parser.add_argument(
        "--no-web",
        dest="generate_web",
        action="store_false",
        help="Do NOT generate web catalog",
    )

    args = parser.parse_args()

    geosite_path = args.geosite
    geoip_path = args.geoip

    if args.download:
        print("[*] Downloading latest Loyalsoldier rules...")
        try:
            geosite_path, geoip_path = download_dat_files(target_dir=args.data_dir)
        except Exception as e:
            print(f"[X] Error downloading files: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Check if default paths in data-dir exist if not specified
        if not geosite_path:
            candidate = os.path.join(args.data_dir, "geosite.dat")
            if os.path.exists(candidate):
                geosite_path = candidate
        if not geoip_path:
            candidate = os.path.join(args.data_dir, "geoip.dat")
            if os.path.exists(candidate):
                geoip_path = candidate

    if not geosite_path and not geoip_path:
        print(
            "[!] No geosite.dat or geoip.dat provided.\n"
            "    Use --download to fetch latest releases, or specify --geosite and/or --geoip.\n"
            "    Run with --help for full usage details.",
            file=sys.stderr,
        )
        sys.exit(1)

    include_filter = parse_category_filter(args.include)
    exclude_filter = parse_category_filter(args.exclude)

    print(f"[*] Starting conversion to Surge rules -> {args.output_dir}...")
    start_total = time.time()

    total_geosite = 0
    total_geoip = 0

    if geosite_path:
        total_geosite = convert_geosite(
            geosite_path=geosite_path,
            output_dir=args.output_dir,
            formats=[args.format],
            include=include_filter,
            exclude=exclude_filter,
            extension=args.extension,
        )

    if geoip_path:
        total_geoip = convert_geoip(
            geoip_path=geoip_path,
            output_dir=args.output_dir,
            no_resolve=args.no_resolve,
            include=include_filter,
            exclude=exclude_filter,
            extension=args.extension,
        )

    if args.generate_web:
        web_path = os.path.join(args.output_dir, "index.html")
        generate_html_catalog(args.output_dir, web_path)

    total_time = time.time() - start_total
    print("\n" + "=" * 50)
    print(" [✓] Conversion Completed Successfully!")
    print(f"     Total GeoSite sets: {total_geosite}")
    print(f"     Total GeoIP sets:   {total_geoip}")
    print(f"     Output directory:   {os.path.abspath(args.output_dir)}")
    print(f"     Time elapsed:       {total_time:.2f}s")
    print("=" * 50)


if __name__ == "__main__":
    main()
