"""End-to-end CLI integration tests for convert.py."""

import ipaddress
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from tests.test_proto import encode_length_delimited, encode_tag, encode_varint


def create_mock_geosite_dat(file_path: str):
    """Create a mock geosite.dat containing 'google' and 'apple' categories."""
    d_google = encode_tag(1, 0) + encode_varint(2) + encode_length_delimited(2, b"google.com")
    site_google = (
        encode_length_delimited(1, b"google") + encode_length_delimited(2, d_google)
    )

    d_apple = encode_tag(1, 0) + encode_varint(2) + encode_length_delimited(2, b"apple.com")
    site_apple = (
        encode_length_delimited(1, b"apple") + encode_length_delimited(2, d_apple)
    )

    gsl = encode_length_delimited(1, site_google) + encode_length_delimited(1, site_apple)
    with open(file_path, "wb") as f:
        f.write(gsl)


def create_mock_geoip_dat(file_path: str):
    """Create a mock geoip.dat containing 'cn' and 'us' categories."""
    c_cn = encode_length_delimited(1, bytes([114, 114, 114, 114])) + encode_tag(2, 0) + encode_varint(32)
    geoip_cn = encode_length_delimited(1, b"cn") + encode_length_delimited(2, c_cn)

    c_us = encode_length_delimited(1, bytes([8, 8, 8, 8])) + encode_tag(2, 0) + encode_varint(32)
    geoip_us = encode_length_delimited(1, b"us") + encode_length_delimited(2, c_us)

    gipl = encode_length_delimited(1, geoip_cn) + encode_length_delimited(1, geoip_us)
    with open(file_path, "wb") as f:
        f.write(gipl)


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.geosite_path = os.path.join(self.temp_dir, "geosite.dat")
        self.geoip_path = os.path.join(self.temp_dir, "geoip.dat")
        self.dist_dir = os.path.join(self.temp_dir, "dist")
        create_mock_geosite_dat(self.geosite_path)
        create_mock_geoip_dat(self.geoip_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_full_conversion(self):
        cmd = [
            sys.executable,
            "convert.py",
            "--geosite",
            self.geosite_path,
            "--geoip",
            self.geoip_path,
            "--output-dir",
            self.dist_dir,
            "--format",
            "both",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, msg=res.stderr)

        # Check geosite ruleset files
        self.assertTrue(os.path.exists(os.path.join(self.dist_dir, "geosite", "google.list")))
        self.assertTrue(os.path.exists(os.path.join(self.dist_dir, "geosite", "apple.list")))

        # Check geosite domainset files
        self.assertTrue(os.path.exists(os.path.join(self.dist_dir, "domainset", "google.list")))
        self.assertTrue(os.path.exists(os.path.join(self.dist_dir, "domainset", "apple.list")))

        # Check geoip ruleset files
        self.assertTrue(os.path.exists(os.path.join(self.dist_dir, "geoip", "cn.list")))
        self.assertTrue(os.path.exists(os.path.join(self.dist_dir, "geoip", "us.list")))

        # Check contents
        with open(os.path.join(self.dist_dir, "geosite", "google.list"), "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("DOMAIN-SUFFIX,google.com", content)

        with open(os.path.join(self.dist_dir, "geoip", "cn.list"), "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("IP-CIDR,114.114.114.114/32,no-resolve", content)

    def test_cli_include_filter(self):
        cmd = [
            sys.executable,
            "convert.py",
            "--geosite",
            self.geosite_path,
            "--output-dir",
            self.dist_dir,
            "--include",
            "google",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, msg=res.stderr)

        self.assertTrue(os.path.exists(os.path.join(self.dist_dir, "geosite", "google.list")))
        self.assertFalse(os.path.exists(os.path.join(self.dist_dir, "geosite", "apple.list")))


if __name__ == "__main__":
    unittest.main()
