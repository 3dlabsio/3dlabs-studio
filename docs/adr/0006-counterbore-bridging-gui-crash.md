# ADR 0006: Counterbore-hole-bridging GUI crash on start-up

## Status
Proposed (2024-04-16) - In progress

---

## Context / Problem Statement
The application crashes with an **access-violation** (nullptr dereference) on start-up after integrating the counterbore-hole-bridging feature.

```
OptionsGroup.cpp:1031  ret = config.option(opt_key)->getInt();
                           ^ opt_key == "counterbore_hole_bridging"
Exception: 0xC0000005 – access violation reading location 0x000000000000
```

* `config.option(opt_key)` (with `create = false`) returns `nullptr` because the currently-loaded
  `DynamicPrintConfig` does **not** contain a concrete `ConfigOption` instance for the newly-added
  enum key.
* The GUI branch for `coEnum` dereferences the pointer immediately, unlike other branches that call
  helper getters (`opt_int`, `opt_bool`, …) which assume the option exists.
* This happens for any profile/preset saved before the new option existed.

## Decision / Mitigation Strategies
We must guarantee that **every** `DynamicPrintConfig` used by the GUI contains a valid
`ConfigOption*` for `counterbore_hole_bridging` (and any future newcomers).

Two complementary approaches are outlined below.  Either one is sufficient; implementing both gives
extra safety but is not strictly required.

### A) Normalise configs after loading (preferred)
1. Identify the central place where print configs are hydrated from presets / 3MF / JSON.  For FFF
   slicing this is `DynamicPrintConfig::normalize_fdm()` (called by the GUI after loading a preset).
2. Inside **phase-1** of the normalisation flow add:
   ```cpp
   if (!this->has("counterbore_hole_bridging"))
       this->set("counterbore_hole_bridging", int(chbNone), /*create=*/true);
   ```
   – This forces instantiation with the default when missing.
3. Audit any alternative code-paths that build `DynamicPrintConfig` objects bypassing
   `normalize_fdm()` (e.g. CLI or SLA) and replicate the guard if necessary.
4. Unit-test: deserialise a legacy profile (without the key) and assert `has()` returns true after
   normalisation.

### B) Harden the GUI getter (quick guard)
1. In `src/slic3r/GUI/OptionsGroup.cpp` change the `coEnum` branch:
   ```diff
   -case coEnum:
   -    ret = config.option(opt_key)->getInt();
   +case coEnum:
   +    {
   +        const ConfigOption *opt_ptr = config.option(opt_key, /*create=*/true);
   +        ret = opt_ptr ? opt_ptr->getInt() : 0; // 0 = first enum item (safe default)
   +    }
   ```
2. Add the same guard in `get_config_value2()` to keep both helpers consistent.
3. Re-compile and verify that the GUI opens with an old profile.

### Trade-offs
* **Approach A** keeps the data layer consistent; any consumer of the config can rely on the option
  existing.  This is the upstream OrcaSlicer pattern.
* **Approach B** is a localised fix requiring no deeper knowledge of the config pipeline, but bugs
  may surface elsewhere if another code-path dereferences the missing option.

## Consequences
Positive:
* Removes start-up crash for legacy presets.
* Establishes a pattern for future option additions.

Negative / Risks:
* If we only implement approach B, other places may still crash/have UB when assuming the option is
  instantiated.
* Approach A touches core normalisation logic—ensure no performance regressions.

## Implementation Status and Roadblocks

### Current Status
- ✅ Feature code integration is complete (see ADR-0005 for implementation details)
- ⚠️ Build system integration has faced challenges:
  - Issues with libnoise dependency integration (addressed through graceful fallback)
  - Environment variable resolution in Windows batch scripts causing problems with NLopt and wxWidgets dependencies
  - Build order changes affecting dependency resolution

### Recent Fixes
- 🔄 Reverted libnoise integration changes to restore build stability
- 🛠️ Fixed environment variable expansion in build_release.bat
- 📝 Documented dependency issues for future reference

### Next Steps
1. Re-approach libnoise integration with better isolation from core build processes
2. Implement the missing-option guard in normalize_fdm() to prevent nullptr crashes
3. Complete the unit tests for the counterbore-bridging functionality
4. Refine build scripts to be more resilient to environment variable issues

## Implementation Checklist
- [ ] Add missing-option guard in `normalize_fdm()` (or equivalent for SLA) to prevent nullptr crash on startup
- [ ] (Optional) Patch `OptionsGroup.cpp` as fallback guard
- [ ] Fix build system to correctly handle dependency integration:
  - [ ] Resolve CMAKE_PREFIX_PATH variable expansion in build scripts
  - [x] Update dependency resolution order to prevent build failures
  - [x] Fixed PressureEqualizer.cpp build error (variable name issue in assert statement)
  - [ ] Create more robust detection for third-party libraries
- [ ] Re-run full GUI smoke test with:
  * factory defaults,
  * an old user profile,
  * a 3MF slice project
- [ ] Add regression unit-test `ProfileBackwardCompatTest.CounterboreBridgingKey`
- [ ] Update release notes (section *Bug fixes*)

## References
* [ADR-0005](0005-counterbore-bridging-implementation.md) – original counterbore-hole-bridging feature design
* Crash analysis conversation (2024-04-16)
* Build dependency issues (2024-05-03)
* Source files involved:
  * `src/libslic3r/PrintConfig.cpp` (enum registration)
  * `src/libslic3r/Config.hpp` (`DynamicPrintConfig::option` helpers)
  * `src/slic3r/GUI/OptionsGroup.cpp` (GUI dereference site)
  * `build_release.bat` (Build script with environment variable issues)
  * `deps/CMakeLists.txt` (Dependencies resolution) 