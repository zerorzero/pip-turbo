#!/usr/bin/env python3
"""
Benchmark: sequential pip install vs pip-turbo concurrent install.

Measures wall-clock time for installing a set of lightweight packages
both sequentially and concurrently, then prints a comparison table.

Usage:
    python benchmark.py
"""

import os
import subprocess
import sys
import time

PACKAGES = [
    "six",
    "colorama",
    "chardet",
    "certifi",
    "idna",
    "pytz",
    "pep8",
    "toml",
]


def _pip():
    if os.name == "nt":
        return os.path.join(os.path.dirname(sys.executable), "Scripts", "pip.exe")
    p = os.path.join(os.path.dirname(sys.executable), "pip")
    return p if os.path.isfile(p) else "pip"


def _uninstall_all():
    subprocess.run(
        [_pip(), "uninstall", "-y"] + PACKAGES,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def bench_sequential():
    _uninstall_all()
    pip = _pip()
    start = time.perf_counter()
    for pkg in PACKAGES:
        subprocess.check_call(
            [pip, "install", pkg],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return time.perf_counter() - start


def bench_concurrent():
    _uninstall_all()
    from install_requirements import install_requirements

    reqfile = "_bench_requirements.txt"
    with open(reqfile, "w") as f:
        f.write("\n".join(PACKAGES))

    start = time.perf_counter()
    install_requirements(reqfile, max_workers=len(PACKAGES))
    elapsed = time.perf_counter() - start

    os.remove(reqfile)
    for artifact in ("requirements_failed.txt",):
        if os.path.exists(artifact):
            os.remove(artifact)
    return elapsed


def main():
    width = 52
    print()
    print("=" * width)
    print("  pip-turbo benchmark".center(width))
    print(f"  {len(PACKAGES)} packages".center(width))
    print("=" * width)

    print("\n[1/2] Sequential pip install …")
    t_seq = bench_sequential()
    print(f"       Done in {t_seq:.2f}s")

    print("\n[2/2] pip-turbo (concurrent) …")
    t_con = bench_concurrent()
    print(f"       Done in {t_con:.2f}s")

    speedup = t_seq / t_con if t_con > 0 else float("inf")

    print()
    print("-" * width)
    print(f"  {'Method':<28} {'Time':>8}  {'Speedup':>8}")
    print("-" * width)
    print(f"  {'pip install (sequential)':<28} {t_seq:>7.2f}s  {'1.00x':>8}")
    print(f"  {'pip-turbo   (concurrent)':<28} {t_con:>7.2f}s  {f'{speedup:.1f}x':>8}")
    print("-" * width)
    print(f"\n  pip-turbo is {speedup:.1f}x faster! 🚀")
    print()


if __name__ == "__main__":
    main()
