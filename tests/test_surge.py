"""Unit tests for Surge formatter (converter/surge.py)."""

import ipaddress
import unittest

from converter.proto import DomainType
from converter.surge import (
    cidr_to_ruleset_line,
    domain_to_ruleset_line,
    format_geoip_ruleset,
    format_geosite_domainset,
    format_geosite_ruleset,
)


class TestSurgeFormatter(unittest.TestCase):

    def test_domain_to_ruleset_line(self):
        self.assertEqual(
            domain_to_ruleset_line(DomainType.ROOT_DOMAIN, "google.com"),
            "DOMAIN-SUFFIX,google.com",
        )
        self.assertEqual(
            domain_to_ruleset_line(DomainType.ROOT_DOMAIN, ".google.com"),
            "DOMAIN-SUFFIX,google.com",
        )
        self.assertEqual(
            domain_to_ruleset_line(DomainType.FULL, "mail.google.com"),
            "DOMAIN,mail.google.com",
        )
        self.assertEqual(
            domain_to_ruleset_line(DomainType.PLAIN, "google"),
            "DOMAIN-KEYWORD,google",
        )
        self.assertEqual(
            domain_to_ruleset_line(DomainType.REGEX, r"^https:\/\/.*google\.com"),
            r"URL-REGEX,^https:\/\/.*google\.com",
        )

    def test_cidr_to_ruleset_line(self):
        ip4 = bytes([1, 1, 1, 0])
        self.assertEqual(
            cidr_to_ruleset_line(ip4, 24, no_resolve=True),
            "IP-CIDR,1.1.1.0/24,no-resolve",
        )
        self.assertEqual(
            cidr_to_ruleset_line(ip4, 24, no_resolve=False),
            "IP-CIDR,1.1.1.0/24",
        )

        ip6 = ipaddress.IPv6Address("2001:db8::").packed
        self.assertEqual(
            cidr_to_ruleset_line(ip6, 32, no_resolve=True),
            "IP-CIDR6,2001:db8::/32,no-resolve",
        )
        self.assertEqual(
            cidr_to_ruleset_line(ip6, 32, no_resolve=False),
            "IP-CIDR6,2001:db8::/32",
        )

    def test_format_geosite_ruleset(self):
        domains = [
            (DomainType.FULL, "mail.google.com"),
            (DomainType.ROOT_DOMAIN, "google.com"),
            (DomainType.PLAIN, "google"),
            (DomainType.ROOT_DOMAIN, "google.com"),  # Duplicate
        ]
        output = format_geosite_ruleset("google", domains, add_header=True, timestamp="2026-09-19 12:00:00 UTC")
        self.assertIn("# Title: Surge RULE-SET - geosite:google", output)
        self.assertIn("# Total Rules: 3", output)

        lines = [l for l in output.splitlines() if not l.startswith("#") and l]
        # Suffix should come first, then DOMAIN, then KEYWORD
        self.assertEqual(
            lines,
            [
                "DOMAIN-SUFFIX,google.com",
                "DOMAIN,mail.google.com",
                "DOMAIN-KEYWORD,google",
            ],
        )

    def test_format_geosite_domainset(self):
        domains = [
            (DomainType.ROOT_DOMAIN, "google.com"),
            (DomainType.FULL, "mail.google.com"),
            (DomainType.PLAIN, "keyword"),  # Should be skipped in DOMAIN-SET
        ]
        output = format_geosite_domainset("google", domains, add_header=True, timestamp="2026-09-19 12:00:00 UTC")
        self.assertIn("# Title: Surge DOMAIN-SET - geosite:google", output)
        self.assertIn("# Total Rules: 2", output)

        lines = [l for l in output.splitlines() if not l.startswith("#") and l]
        self.assertEqual(lines, [".google.com", "mail.google.com"])

    def test_format_geoip_ruleset(self):
        cidrs = [
            (bytes([1, 1, 1, 0]), 24),
            (bytes([8, 8, 8, 8]), 32),
            (ipaddress.IPv6Address("2001:db8::").packed, 32),
            (bytes([1, 1, 1, 0]), 24),  # Duplicate
        ]
        output = format_geoip_ruleset("dns", cidrs, no_resolve=True, add_header=True, timestamp="2026-09-19 12:00:00 UTC")
        self.assertIn("# Title: Surge RULE-SET - geoip:dns", output)
        self.assertIn("# Total Rules: 3", output)

        lines = [l for l in output.splitlines() if not l.startswith("#") and l]
        self.assertEqual(
            lines,
            [
                "IP-CIDR,1.1.1.0/24,no-resolve",
                "IP-CIDR,8.8.8.8/32,no-resolve",
                "IP-CIDR6,2001:db8::/32,no-resolve",
            ],
        )


if __name__ == "__main__":
    unittest.main()
