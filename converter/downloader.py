"""Downloader for Loyalsoldier/v2ray-rules-dat release assets."""

import hashlib
import os
import ssl
import sys
import urllib.request
from typing import Optional

DEFAULT_GEOSITE_URL = (
    "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geosite.dat"
)
DEFAULT_GEOIP_URL = (
    "https://github.com/Loyalsoldier/v2ray-rules-dat/releases/latest/download/geoip.dat"
)


def _create_ssl_context() -> ssl.SSLContext:
    """Create SSL context with fallback for environments with missing root certificates."""
    try:
        ctx = ssl.create_default_context()
        return ctx
    except Exception:
        ctx = ssl._create_unverified_context()
        return ctx


def download_file(
    url: str,
    output_path: str,
    sha256_url: Optional[str] = None,
    timeout: int = 60,
) -> str:
    """Download a file with progress reporting and optional SHA256 verification.

    Args:
        url: Remote URL to download.
        output_path: Local path to save the file.
        sha256_url: Optional URL to fetch sha256 checksum for verification.
        timeout: Request timeout in seconds.

    Returns:
        The output path on success.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    print(f"[*] Downloading {url} -> {output_path}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (V2Ray-Surge-Converter)"
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = _create_ssl_context()

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as response, open(
            output_path, "wb"
        ) as out_file:
            total_size = response.getheader("Content-Length")
            total_bytes = int(total_size) if total_size and total_size.isdigit() else 0
            downloaded = 0
            chunk_size = 64 * 1024

            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_bytes > 0:
                    percent = (downloaded / total_bytes) * 100
                    sys.stdout.write(
                        f"\r    Progress: {downloaded / 1024 / 1024:.2f} MB / "
                        f"{total_bytes / 1024 / 1024:.2f} MB ({percent:.1f}%)"
                    )
                else:
                    sys.stdout.write(f"\r    Downloaded: {downloaded / 1024 / 1024:.2f} MB")
                sys.stdout.flush()
            print()
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"Failed to download {url}: {e}")

    # Optional SHA256 verification
    if sha256_url:
        try:
            print(f"[*] Verifying SHA256 checksum from {sha256_url}...")
            sha_req = urllib.request.Request(sha256_url, headers=headers)
            with urllib.request.urlopen(sha_req, context=ctx, timeout=timeout) as resp:
                expected_sha = resp.read().decode("utf-8").strip().split()[0].lower()

            hasher = hashlib.sha256()
            with open(output_path, "rb") as f:
                while chunk := f.read(64 * 1024):
                    hasher.update(chunk)
            actual_sha = hasher.hexdigest().lower()

            if actual_sha != expected_sha:
                os.remove(output_path)
                raise ValueError(
                    f"SHA256 mismatch! Expected {expected_sha}, got {actual_sha}"
                )
            print("    SHA256 verification passed.")
        except Exception as e:
            print(f"[!] Warning: SHA256 check skipped or failed: {e}")

    return output_path


def download_dat_files(
    target_dir: str = "./data",
    verify_checksum: bool = True,
) -> tuple[str, str]:
    """Download latest geosite.dat and geoip.dat files from Loyalsoldier release.

    Returns:
        Tuple of (geosite_path, geoip_path).
    """
    geosite_path = os.path.join(target_dir, "geosite.dat")
    geoip_path = os.path.join(target_dir, "geoip.dat")

    geosite_sha_url = (
        f"{DEFAULT_GEOSITE_URL}.sha256sum" if verify_checksum else None
    )
    geoip_sha_url = f"{DEFAULT_GEOIP_URL}.sha256sum" if verify_checksum else None

    download_file(DEFAULT_GEOSITE_URL, geosite_path, sha256_url=geosite_sha_url)
    download_file(DEFAULT_GEOIP_URL, geoip_path, sha256_url=geoip_sha_url)

    return geosite_path, geoip_path
