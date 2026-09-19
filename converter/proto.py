"""Protobuf binary decoder for V2Ray geosite.dat and geoip.dat.

This module provides a pure Python, zero-dependency parser for the Protocol Buffer
wire format used by v2ray-core, v2fly, and Loyalsoldier/v2ray-rules-dat.

Protobuf wire specifications referenced from:
- v2ray.core.app.router.routercommon.Domain
- v2ray.core.app.router.routercommon.GeoSite / GeoSiteList
- v2ray.core.app.router.routercommon.CIDR
- v2ray.core.app.router.routercommon.GeoIP / GeoIPList
"""

import enum
from typing import Dict, List, Tuple


class DomainType(enum.IntEnum):
    """Domain matching type defined in v2ray router common.proto."""

    PLAIN = 0       # Keyword matching
    REGEX = 1       # Regular expression
    ROOT_DOMAIN = 2 # Domain suffix matching
    FULL = 3        # Exact full domain matching


def decode_varint(buf: bytes, pos: int) -> Tuple[int, int]:
    """Decode an unsigned varint from buf starting at pos.

    Returns:
        Tuple of (value, new_position).
    """
    res = 0
    shift = 0
    buf_len = len(buf)
    while pos < buf_len:
        b = buf[pos]
        pos += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80):
            return res, pos
        shift += 7
        if shift > 64:
            raise ValueError("Varint too long")
    raise IndexError("Buffer truncated while reading varint")


def skip_field(buf: bytes, pos: int, wire_type: int) -> int:
    """Skip a field based on its wire type."""
    if wire_type == 0:  # Varint
        _, pos = decode_varint(buf, pos)
    elif wire_type == 1:  # 64-bit
        pos += 8
    elif wire_type == 2:  # Length-delimited
        length, pos = decode_varint(buf, pos)
        pos += length
    elif wire_type == 5:  # 32-bit
        pos += 4
    else:
        raise ValueError(f"Unsupported wire type: {wire_type}")
    return pos


def parse_domain(buf: bytes) -> Tuple[int, str]:
    """Parse a v2ray Domain message.

    Fields:
      1: Domain.Type type (varint enum)
      2: string value (length-delimited)
      3: repeated Attribute attribute (ignored)
    """
    pos = 0
    domain_type = DomainType.PLAIN
    value = ""
    buf_len = len(buf)

    while pos < buf_len:
        tag, pos = decode_varint(buf, pos)
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 1 and wire_type == 0:
            raw_type, pos = decode_varint(buf, pos)
            try:
                domain_type = DomainType(raw_type)
            except ValueError:
                domain_type = raw_type
        elif field_num == 2 and wire_type == 2:
            length, pos = decode_varint(buf, pos)
            value = buf[pos : pos + length].decode("utf-8", errors="ignore")
            pos += length
        else:
            pos = skip_field(buf, pos, wire_type)

    return int(domain_type), value


def parse_geosite(buf: bytes) -> Tuple[str, List[Tuple[int, str]]]:
    """Parse a single GeoSite message.

    Fields:
      1: string country_code (length-delimited)
      2: repeated Domain domain (length-delimited)
    """
    pos = 0
    country_code = ""
    domains: List[Tuple[int, str]] = []
    buf_len = len(buf)

    while pos < buf_len:
        tag, pos = decode_varint(buf, pos)
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 1 and wire_type == 2:
            length, pos = decode_varint(buf, pos)
            country_code = buf[pos : pos + length].decode("utf-8", errors="ignore").strip().lower()
            pos += length
        elif field_num == 2 and wire_type == 2:
            length, pos = decode_varint(buf, pos)
            domain_buf = buf[pos : pos + length]
            pos += length
            dtype, val = parse_domain(domain_buf)
            if val:
                domains.append((dtype, val))
        else:
            pos = skip_field(buf, pos, wire_type)

    return country_code, domains


def parse_geosite_data(data: bytes) -> Dict[str, List[Tuple[int, str]]]:
    """Parse a GeoSiteList protobuf binary blob (geosite.dat).

    GeoSiteList:
      1: repeated GeoSite entry (length-delimited)
    """
    pos = 0
    data_len = len(data)
    result: Dict[str, List[Tuple[int, str]]] = {}

    while pos < data_len:
        tag, pos = decode_varint(data, pos)
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 1 and wire_type == 2:
            length, pos = decode_varint(data, pos)
            site_buf = data[pos : pos + length]
            pos += length
            code, domains = parse_geosite(site_buf)
            if code:
                if code not in result:
                    result[code] = []
                result[code].extend(domains)
        else:
            pos = skip_field(data, pos, wire_type)

    return result


def parse_cidr(buf: bytes) -> Tuple[bytes, int]:
    """Parse a CIDR message.

    Fields:
      1: bytes ip (length-delimited: 4 bytes for IPv4 or 16 bytes for IPv6)
      2: uint32 prefix (varint)
    """
    pos = 0
    ip_bytes = b""
    prefix = 0
    buf_len = len(buf)

    while pos < buf_len:
        tag, pos = decode_varint(buf, pos)
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 1 and wire_type == 2:
            length, pos = decode_varint(buf, pos)
            ip_bytes = buf[pos : pos + length]
            pos += length
        elif field_num == 2 and wire_type == 0:
            prefix, pos = decode_varint(buf, pos)
        else:
            pos = skip_field(buf, pos, wire_type)

    return ip_bytes, prefix


def parse_geoip(buf: bytes) -> Tuple[str, List[Tuple[bytes, int]]]:
    """Parse a single GeoIP message.

    Fields:
      1: string country_code (length-delimited)
      2: repeated CIDR cidr (length-delimited)
      3: bool inverse_match (varint)
    """
    pos = 0
    country_code = ""
    cidrs: List[Tuple[bytes, int]] = []
    buf_len = len(buf)

    while pos < buf_len:
        tag, pos = decode_varint(buf, pos)
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 1 and wire_type == 2:
            length, pos = decode_varint(buf, pos)
            country_code = buf[pos : pos + length].decode("utf-8", errors="ignore").strip().lower()
            pos += length
        elif field_num == 2 and wire_type == 2:
            length, pos = decode_varint(buf, pos)
            cidr_buf = buf[pos : pos + length]
            pos += length
            ip_bytes, prefix = parse_cidr(cidr_buf)
            if ip_bytes and len(ip_bytes) in (4, 16):
                cidrs.append((ip_bytes, prefix))
        else:
            pos = skip_field(buf, pos, wire_type)

    return country_code, cidrs


def parse_geoip_data(data: bytes) -> Dict[str, List[Tuple[bytes, int]]]:
    """Parse a GeoIPList protobuf binary blob (geoip.dat).

    GeoIPList:
      1: repeated GeoIP entry (length-delimited)
    """
    pos = 0
    data_len = len(data)
    result: Dict[str, List[Tuple[bytes, int]]] = {}

    while pos < data_len:
        tag, pos = decode_varint(data, pos)
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 1 and wire_type == 2:
            length, pos = decode_varint(data, pos)
            geoip_buf = data[pos : pos + length]
            pos += length
            code, cidrs = parse_geoip(geoip_buf)
            if code:
                if code not in result:
                    result[code] = []
                result[code].extend(cidrs)
        else:
            pos = skip_field(data, pos, wire_type)

    return result


def parse_geosite_file(file_path: str) -> Dict[str, List[Tuple[int, str]]]:
    """Read and parse a geosite.dat file."""
    with open(file_path, "rb") as f:
        return parse_geosite_data(f.read())


def parse_geoip_file(file_path: str) -> Dict[str, List[Tuple[bytes, int]]]:
    """Read and parse a geoip.dat file."""
    with open(file_path, "rb") as f:
        return parse_geoip_data(f.read())
