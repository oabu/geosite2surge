"""Unit tests for Protobuf parser (converter/proto.py)."""

import ipaddress
import unittest

from converter.proto import (
    DomainType,
    decode_varint,
    parse_cidr,
    parse_domain,
    parse_geoip,
    parse_geoip_data,
    parse_geosite,
    parse_geosite_data,
)


def encode_varint(val: int) -> bytes:
    """Helper to encode unsigned varint."""
    out = bytearray()
    while True:
        b = val & 0x7F
        val >>= 7
        if val:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def encode_tag(field_num: int, wire_type: int) -> bytes:
    """Helper to encode tag."""
    return encode_varint((field_num << 3) | wire_type)


def encode_length_delimited(field_num: int, data: bytes) -> bytes:
    """Helper to encode length-delimited field."""
    return encode_tag(field_num, 2) + encode_varint(len(data)) + data


class TestProtoParser(unittest.TestCase):

    def test_decode_varint(self):
        cases = [0, 1, 127, 128, 300, 16384, 1000000]
        for val in cases:
            enc = encode_varint(val)
            dec, pos = decode_varint(enc, 0)
            self.assertEqual(dec, val)
            self.assertEqual(pos, len(enc))

    def test_parse_domain_types(self):
        # RootDomain (2) -> google.com
        d_root = encode_tag(1, 0) + encode_varint(2) + encode_length_delimited(2, b"google.com")
        dtype, val = parse_domain(d_root)
        self.assertEqual(dtype, DomainType.ROOT_DOMAIN)
        self.assertEqual(val, "google.com")

        # Full (3) -> sub.google.com
        d_full = encode_tag(1, 0) + encode_varint(3) + encode_length_delimited(2, b"sub.google.com")
        dtype, val = parse_domain(d_full)
        self.assertEqual(dtype, DomainType.FULL)
        self.assertEqual(val, "sub.google.com")

        # Plain (0) -> keyword
        d_plain = encode_tag(1, 0) + encode_varint(0) + encode_length_delimited(2, b"keyword")
        dtype, val = parse_domain(d_plain)
        self.assertEqual(dtype, DomainType.PLAIN)
        self.assertEqual(val, "keyword")

        # Regex (1) -> ^abc.*
        d_regex = encode_tag(1, 0) + encode_varint(1) + encode_length_delimited(2, b"^abc.*")
        dtype, val = parse_domain(d_regex)
        self.assertEqual(dtype, DomainType.REGEX)
        self.assertEqual(val, "^abc.*")

    def test_parse_geosite_and_list(self):
        d1 = encode_tag(1, 0) + encode_varint(2) + encode_length_delimited(2, b"apple.com")
        d2 = encode_tag(1, 0) + encode_varint(3) + encode_length_delimited(2, b"icloud.com")

        site = (
            encode_length_delimited(1, b"apple")
            + encode_length_delimited(2, d1)
            + encode_length_delimited(2, d2)
        )
        code, domains = parse_geosite(site)
        self.assertEqual(code, "apple")
        self.assertEqual(len(domains), 2)
        self.assertEqual(domains[0], (2, "apple.com"))
        self.assertEqual(domains[1], (3, "icloud.com"))

        # Top-level GeoSiteList
        gsl = encode_length_delimited(1, site)
        data_map = parse_geosite_data(gsl)
        self.assertIn("apple", data_map)
        self.assertEqual(len(data_map["apple"]), 2)

    def test_parse_cidr_ipv4_and_ipv6(self):
        # IPv4: 1.2.3.4/24
        c_v4 = encode_length_delimited(1, bytes([1, 2, 3, 4])) + encode_tag(2, 0) + encode_varint(24)
        ip_bytes, prefix = parse_cidr(c_v4)
        self.assertEqual(ip_bytes, bytes([1, 2, 3, 4]))
        self.assertEqual(prefix, 24)

        # IPv6: 2001:db8::/32
        ip6 = ipaddress.IPv6Address("2001:db8::").packed
        c_v6 = encode_length_delimited(1, ip6) + encode_tag(2, 0) + encode_varint(32)
        ip_bytes, prefix = parse_cidr(c_v6)
        self.assertEqual(ip_bytes, ip6)
        self.assertEqual(prefix, 32)

    def test_parse_geoip_and_list(self):
        c_v4 = encode_length_delimited(1, bytes([8, 8, 8, 8])) + encode_tag(2, 0) + encode_varint(32)
        geoip = encode_length_delimited(1, b"google") + encode_length_delimited(2, c_v4)

        code, cidrs = parse_geoip(geoip)
        self.assertEqual(code, "google")
        self.assertEqual(len(cidrs), 1)
        self.assertEqual(cidrs[0], (bytes([8, 8, 8, 8]), 32))

        # Top-level GeoIPList
        gipl = encode_length_delimited(1, geoip)
        data_map = parse_geoip_data(gipl)
        self.assertIn("google", data_map)
        self.assertEqual(len(data_map["google"]), 1)


if __name__ == "__main__":
    unittest.main()
