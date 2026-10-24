#!/usr/bin/env python3
"""Fetch pinned public upstream inputs and verify their SHA-256 digests."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

base = Path(__file__).resolve().parent

def download(url, name, expected):
    target = base / name
    if target.is_file():
        with target.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual == expected:
            print(name + ": SHA256 OK", flush=True)
            return target
        raise RuntimeError(name + ": existing file has an unexpected checksum")
    partial = target.with_name(target.name + ".part")
    subprocess.run(["curl", "--fail", "--location", "--retry", "3",
                    "--retry-delay", "2", "--output", str(partial), url], check=True)
    with partial.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != expected:
        raise RuntimeError(name + ": downloaded file has an unexpected checksum")
    partial.replace(target)
    print(name + ": SHA256 OK", flush=True)
    return target

archive = download(
    "https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.2_build/ghidra_12.2_PUBLIC_20261016.zip",
    "ghidra_12.2_PUBLIC_20261016.zip",
    "2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67",
)
if not (base / "ghidra_12.2_PUBLIC").exists():
    subprocess.run(["unzip", "-q", str(archive), "-d", str(base)], check=True)

for arch in ("arm64", "amd64"):
    metadata = json.loads((base / ("temurin25-" + arch + ".json")).read_text())
    package = metadata[0]["binary"]["package"]
    jdk_archive = download(package["link"], "temurin25-" + arch + ".tar.gz", package["checksum"])
    if arch == "amd64":
        destination = base / "test-jdk25"
        if not (destination / "bin/java").exists():
            destination.mkdir(exist_ok=True)
            subprocess.run(["tar", "-xzf", str(jdk_archive), "-C",
                            str(destination), "--strip-components=1"], check=True)
print("Upstream inputs ready.", flush=True)
