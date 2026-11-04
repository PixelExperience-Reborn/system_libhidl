# P1 — system/libhidl Android 17 and mondrian HIDL vendor compatibility audit

Date: 2026-11-04. **Historical source / ABI review only; no vendor blob or Android17 device runtime validated.**

## Grounded provenance

- PixelExperience-Reborn archive `system_libhidl` branch `seventeen`, SHA `c4adee3af02241cb0070590c501b354ce4109fbe`; merged Android14 r21 on 2024-01-30.
- Official AOSP17 r1 `platform/system/libhidl` exact Git tree `f57b82cf0599f5e462f5ca2808e84f45547ebb3a`, source https://android.googlesource.com/platform/system/libhidl/+/refs/tags/android-17.0.0_r1/ . This remains selected in the staged AOSP17 manifest, together with official `system/libhwbinder`, `hardware/interfaces` and `system/core`.
- The archive is not an Android17 base. No historical HIDL source is activated on the PE-Reborn device.

## Historical deltas to review (not blindly port)

**1. Legacy HIDL constructor symbol compatibility:**
- Commit `bf5d2005ec06403558a368483f0804bc70bf2f96` ("Revert delete gBn/sConstructorMap", 2022) restores `gBnConstructorMap` and `gBsConstructorMap` global symbols, with fallback lookups in `transport/HidlBinderSupport.cpp` and `transport/HidlPassthroughSupport.cpp`, and definitions in `transport/Static.cpp`.
- PE commit explicitly says "We still need it for legacy blobs." These are **binary ABI contracts**, not a cosmetic Android feature. The official AOSP17 `Static.cpp` has only current `getBnConstructorMap()` / `getBsConstructorMap()` accessors, and official `HidlBinderSupport.cpp` deliberately fails if its generated constructor is absent; it does **not** contain the old global fallback.
- **BLOCKED pending real blob ABI audit.** First inspect the actual proprietary libraries intended for the *new* PE-Reborn vendor source, with `readelf -Ws`, `nm -D`, ELF dependencies and linker resolution. Establish whether symbols and names are actually missing, and which library/partition needs them. Restore only a narrowly scoped, ABI-tested solution if a real needed blob requires it, with old/new class symbol collision and registration tests. Avoid importing old fallback silently into all HIDL services.

**2. Recovery link exposure:**
- Commit `5bde56767140c8e2cdc2a3ca3f4d123ac7e427e7` adds `recovery_available: true` to `libhidlmemory`. This exists in PE archive but **not in the official AOSP17** `libhidlmemory/Android.bp` at tag r1.
- Official AOSP17 `libhidlbase` itself already declares `recovery_available: true`. These are different modules: that setting does not imply that `libhidlmemory` can be built for recovery. **DEFER** until the independent PE-Reborn mondrian recovery Soong graph proves the library is required and all dependencies are available in the recovery image. This is a build/ABI change, not a blanket recovery feature.

**3. Core HIDL security and compatibility:**
- Official AOSP17 `libhidlbase` links the actual `libhwbinder-impl-internal`, supports vendor/product and only the reviewed APEX list (`com.android.neuralnetworks`, Bluetooth, Media, NFC, Tethering). `libhidltransport` remains a deprecated compatibility name; AOSP17 recommends `libhidlbase`.
- Current upstream HIDL service management is tied to Treble/VINTF enforcement and `ro.debuggable`/testing override conditions. Do **not** relax VINTF declarations, `hwservicemanager` registration or SELinux to make a legacy blob appear functional. Many vendor interfaces are HIDL while newer Android modules use stable AIDL; both must be coordinated.
- Historical commit `59af9c82dc648360340958983646473d63ca103b` optimizes checking `ro.debuggable` only for Treble testing override. This is largely upstream history and not a reason for ROM-wide service-manager changes.

## Native mondrian device-port acceptance

Existing LF52406 LineageOS-derived mondrian/sm8450-common trees and vendor blobs are **reference evidence only**. The product for PixelExperience-Reborn Android17 needs an independently authored device/common product and reviewed vendor/kernel graph.

1. Inventory each actually required vendor HIDL service and exported/undefined ELF symbols; verify original VINTF manifests and Matrix versions against AOSP17 frozen FCM. No speculative `gBn/gBs` compatibility fallbacks.
2. Prove `libhidlbase`/`libhwbinder` and required `libhidlmemory` build variants, 32/64-bit dependencies, partition ownership, APEX visibility and correct binder threading.
3. Confirm modern AIDL/HIDL coexistence: camera, audio, fingerprint, media, sensors, NFC, thermal, lights, keymaster/KeyMint, recovery. Do not add unused HALs merely because the original device exposed them.
4. Test boot and VINTF checks, `lshal`, `servicemanager`/`hwservicemanager`, ashmem/memory token, HIDL transport, `libhidl_test`, `vts_ibase_test` and `hal_implementation_test`.
5. For recovery, separately check HIDL memory dependency, namespaces and SELinux, and preserve AVB/FBE/OTA tests. A successful host-only audit cannot prove boot/recovery or the proprietary vendor ABI.

## Status and decision

- [x] Historical PE code, 2 device-impacting changes and commit provenance classified.
- [x] Official AOSP17 HIDL base/recovery/constructor behavior and exact tree identified.
- [x] Historical ABI source inventory [CI PASS #41792429885](https://github.com/PixelExperience-Reborn/system_libhidl/actions/runs/41792429885).
- [x] Official Android17 r1 exact tree, constructor symbols and recovery source declarations [CI PASS #41792429940](https://github.com/PixelExperience-Reborn/system_libhidl/actions/runs/41792429940). Source-only evidence, not a vendor linker/build test.
- [ ] Real proprietary blobs scanned for undefined/exported constructor symbols.
- [ ] Android17 Soong/ABI linker, VINTF/CTS/VTS and mondrian boot/recovery tests.

**Decision: preserve official `platform/system/libhidl` in staged manifest; no old global constructor symbols, forced recovery_available or VINTF/SELinux bypass until verified consumer demands them.**
