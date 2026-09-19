"""Surge rule generator and formatter.

Formats parsed GeoSite and GeoIP data into Surge RULE-SET and DOMAIN-SET files.
Features:
- Standard Surge RULE-SET format (DOMAIN-SUFFIX, DOMAIN, DOMAIN-KEYWORD, URL-REGEX, IP-CIDR, IP-CIDR6)
- Optional DOMAIN-SET format
- IPv4 / IPv6 distinction (IP-CIDR vs IP-CIDR6)
- Optional `no-resolve` parameter for IP rules
- Deduplication and deterministic alphabetical sorting
- Informative header with timestamp and statistics
"""

from datetime import datetime, timezone
import ipaddress
from typing import Iterable, List, Optional, Set, Tuple

from converter.proto import DomainType


def format_header(
    name: str,
    rule_type: str,
    count: int,
    source: str = "Loyalsoldier/v2ray-rules-dat",
    timestamp: Optional[str] = None,
) -> str:
    """Generate a standard Surge rule set header comment block."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# Title: Surge {rule_type} - {name}",
        f"# Source: {source}",
        f"# Updated: {timestamp}",
        f"# Total Rules: {count}",
        "#",
    ]
    return "\n".join(lines) + "\n"


def domain_to_ruleset_line(domain_type: int, value: str) -> Optional[str]:
    """Convert a domain entry to a Surge RULE-SET line.

    Type mapping:
      ROOT_DOMAIN (2) -> DOMAIN-SUFFIX,example.com
      FULL (3)        -> DOMAIN,example.com
      PLAIN (0)       -> DOMAIN-KEYWORD,example
      REGEX (1)       -> URL-REGEX,example
    """
    val = value.strip().lower()
    if not val:
        return None

    # Remove leading dots from suffix domain if present
    if val.startswith("."):
        val = val[1:]

    if domain_type == DomainType.ROOT_DOMAIN:
        return f"DOMAIN-SUFFIX,{val}"
    elif domain_type == DomainType.FULL:
        return f"DOMAIN,{val}"
    elif domain_type == DomainType.PLAIN:
        return f"DOMAIN-KEYWORD,{val}"
    elif domain_type == DomainType.REGEX:
        return f"URL-REGEX,{value.strip()}"
    else:
        # Fallback to suffix for unknown types
        return f"DOMAIN-SUFFIX,{val}"


def cidr_to_ruleset_line(ip_bytes: bytes, prefix: int, no_resolve: bool = True) -> Optional[str]:
    """Convert a CIDR entry to a Surge RULE-SET line.

    IPv4 -> IP-CIDR,x.x.x.x/y[,no-resolve]
    IPv6 -> IP-CIDR6,x:x::x/y[,no-resolve]
    """
    try:
        suffix = ",no-resolve" if no_resolve else ""
        if len(ip_bytes) == 4:
            ip = ipaddress.IPv4Address(ip_bytes)
            return f"IP-CIDR,{ip}/{prefix}{suffix}"
        elif len(ip_bytes) == 16:
            ip = ipaddress.IPv6Address(ip_bytes)
            return f"IP-CIDR6,{ip}/{prefix}{suffix}"
    except Exception:
        return None
    return None


def format_geosite_ruleset(
    name: str,
    domains: Iterable[Tuple[int, str]],
    add_header: bool = True,
    timestamp: Optional[str] = None,
) -> str:
    """Format GeoSite domain entries into Surge RULE-SET format."""
    seen: Set[str] = set()
    rules: List[str] = []

    for dtype, val in domains:
        line = domain_to_ruleset_line(dtype, val)
        if line and line not in seen:
            seen.add(line)
            rules.append(line)

    # Deterministic sort: DOMAIN-SUFFIX first, then DOMAIN, then DOMAIN-KEYWORD, then URL-REGEX
    type_priority = {
        "DOMAIN-SUFFIX": 1,
        "DOMAIN": 2,
        "DOMAIN-KEYWORD": 3,
        "URL-REGEX": 4,
    }

    def sort_key(rule: str):
        prefix = rule.split(",", 1)[0]
        prio = type_priority.get(prefix, 99)
        content = rule.split(",", 1)[1] if "," in rule else rule
        return (prio, content)

    rules.sort(key=sort_key)

    output = ""
    if add_header:
        output += format_header(f"geosite:{name}", "RULE-SET", len(rules), timestamp=timestamp)

    if rules:
        output += "\n".join(rules) + "\n"

    return output


def format_geosite_domainset(
    name: str,
    domains: Iterable[Tuple[int, str]],
    add_header: bool = True,
    timestamp: Optional[str] = None,
) -> str:
    """Format GeoSite domain entries into Surge DOMAIN-SET format.

    Surge DOMAIN-SET format:
    - Root domains start with a dot (e.g. `.google.com`)
    - Exact domains have no dot (e.g. `google.com`)
    - Plain/Regex are noted in comments as unsupported in DOMAIN-SET.
    """
    seen: Set[str] = set()
    domain_lines: List[str] = []

    for dtype, val in domains:
        clean = val.strip().lower()
        if not clean:
            continue
        if clean.startswith("."):
            clean = clean[1:]

        if dtype == DomainType.ROOT_DOMAIN:
            entry = f".{clean}"
        elif dtype == DomainType.FULL:
            entry = clean
        else:
            # Plain and regex are not supported in DOMAIN-SET
            continue

        if entry not in seen:
            seen.add(entry)
            domain_lines.append(entry)

    domain_lines.sort()

    output = ""
    if add_header:
        output += format_header(f"geosite:{name}", "DOMAIN-SET", len(domain_lines), timestamp=timestamp)

    if domain_lines:
        output += "\n".join(domain_lines) + "\n"

    return output


def format_geoip_ruleset(
    name: str,
    cidrs: Iterable[Tuple[bytes, int]],
    no_resolve: bool = True,
    add_header: bool = True,
    timestamp: Optional[str] = None,
) -> str:
    """Format GeoIP CIDR entries into Surge RULE-SET format."""
    seen: Set[str] = set()
    ipv4_rules: List[str] = []
    ipv6_rules: List[str] = []

    for ip_bytes, prefix in cidrs:
        line = cidr_to_ruleset_line(ip_bytes, prefix, no_resolve=no_resolve)
        if line and line not in seen:
            seen.add(line)
            if line.startswith("IP-CIDR6"):
                ipv6_rules.append(line)
            else:
                ipv4_rules.append(line)

    # Sort IP rules naturally
    def ip_sort_key(rule: str):
        # Format: IP-CIDR,1.2.3.4/24,...
        parts = rule.split(",")
        cidr_str = parts[1]
        try:
            net = ipaddress.ip_network(cidr_str, strict=False)
            return (0 if net.version == 4 else 1, int(net.network_address), net.prefixlen)
        except Exception:
            return (2, 0, 0)

    ipv4_rules.sort(key=ip_sort_key)
    ipv6_rules.sort(key=ip_sort_key)
    all_rules = ipv4_rules + ipv6_rules

    output = ""
    if add_header:
        output += format_header(f"geoip:{name}", "RULE-SET", len(all_rules), timestamp=timestamp)

    if all_rules:
        output += "\n".join(all_rules) + "\n"

    return output
