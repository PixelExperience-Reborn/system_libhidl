#!/usr/bin/env python3
"""Historical HIDL ABI/check inventory; NOT a linker, VINTF or recovery test."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise AssertionError(message)
    print("PASS legacy HIDL inventory:", message)


def main():
    bp = (ROOT / "Android.bp").read_text()
    memory = (ROOT / "libhidlmemory/Android.bp").read_text()
    static = (ROOT / "transport/Static.cpp").read_text()
    binder = (ROOT / "transport/HidlBinderSupport.cpp").read_text()
    pass_through = (ROOT / "transport/HidlPassthroughSupport.cpp").read_text()
    mapping = json.loads((ROOT / "TEST_MAPPING").read_text())
    for symbol in ('name: "libhidlbase"', 'name: "libhidltransport"',
                   'name: "libhidl_test"'):
        require(symbol in bp, "archived libhidl module " + symbol)
    require('name: "libhidlmemory"' in memory and 'recovery_available: true' in memory,
            "old PE libhidlmemory recovery flag")
    require("DoNotDestruct<BnConstructorMap> gBnConstructorMap{};" in static
            and "DoNotDestruct<BsConstructorMap> gBsConstructorMap{};" in static,
            "reintroduced legacy exported constructor maps")
    require("details::gBnConstructorMap->get" in binder,
            "archived binder constructor fallback lookup")
    require("gBsConstructorMap->get" in pass_through,
            "archived passthrough constructor fallback lookup")
    require("getBnConstructorMap()" in static and "getBsConstructorMap()" in static,
            "newer constructor accessors coexist in archived PE")
    tests = {obj.get("name") for obj in mapping.get("presubmit", [])}
    for name in ("libhidl_test", "hal_implementation_test", "vts_ibase_test"):
        require(name in tests, "historical HIDL test mapping " + name)
    print("PASS historical source-only check. No Android17 or actual vendor HIDL ABI established.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, json.JSONDecodeError) as exc:
        print("FAIL:", exc, file=sys.stderr)
        sys.exit(1)
