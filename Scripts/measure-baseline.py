#!/usr/bin/python3
"""Measure the local Release app without installing additional packages."""

import argparse
import json
import os
from pathlib import Path
import platform
import selectors
import statistics
import subprocess
import time


def cpu_seconds(value):
    return sum(float(part) * 60 ** index for index, part in enumerate(reversed(value.split(":"))))


def sample(pid):
    result = subprocess.check_output(
        ["/bin/ps", "-p", str(pid), "-o", "rss=", "-o", "time="], text=True
    ).split()
    return int(result[0]), cpu_seconds(result[1])


def measure(executable, seconds):
    env = dict(os.environ, UAS_MEASURE_STARTUP="1")
    start = time.monotonic()
    process = subprocess.Popen([str(executable)], env=env, stdout=subprocess.PIPE)
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            if not selector.select(timeout=20):
                raise RuntimeError("Root view did not appear within 20 seconds.")
            if process.stdout.readline().strip() != b"UAS_ROOT_VIEW_APPEARED":
                raise RuntimeError("App exited or returned an unexpected startup marker.")
        startup_ms = (time.monotonic() - start) * 1000
        time.sleep(5)
        _, initial_cpu = sample(process.pid)
        sample_start = time.monotonic()
        rss = []
        for _ in range(seconds):
            time.sleep(1)
            memory, final_cpu = sample(process.pid)
            rss.append(memory)
        elapsed = time.monotonic() - sample_start
        return {
            "configuration": "release",
            "macos": platform.mac_ver()[0],
            "architecture": platform.machine(),
            "startup_to_root_view_ms": round(startup_ms, 2),
            "warmup_seconds": 5,
            "sample_seconds": round(elapsed, 2),
            "rss_median_mib": round(statistics.median(rss) / 1024, 2),
            "rss_max_mib": round(max(rss) / 1024, 2),
            "cpu_mean_percent_one_core": round((final_cpu - initial_cpu) / elapsed * 100, 2),
        }
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        process.stdout.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 300:
        parser.error("--seconds must be between 1 and 300")
    executable = Path(__file__).resolve().parents[1] / "dist/release/Universal AI Studio.app/Contents/MacOS/UniversalAIStudio"
    if not executable.is_file():
        parser.error("Build the Release app first: bash Scripts/build-app.sh release")
    print(json.dumps(measure(executable, args.seconds), indent=2))
