# Release

## Version single source

The `.uplugin` `VersionName` is the **single source of truth**. `commands/bump-version.ps1` updates
it together with `GetExtensionVersion()` in the module and `version` in `extension.json`, so they can
never drift. Never hand-edit one location alone.

```powershell
./commands/bump-version.ps1 -NewVersion "0.2.0"          # apply
./commands/bump-version.ps1 -NewVersion "0.2.0" -WhatIf  # preview
./commands/get-version.ps1                                # read current
```

## The version gate

`release.yml` runs on every push to `main` but **publishes nothing unless the version changed**:

1. `check-version-tag` reads `VersionName` from the `.uplugin`, finds the previous tag, and checks
   whether a tag named after the current version already exists.
2. Every downstream job is `if: needs.check-version-tag.outputs.tag_exists == 'false'`.

So a normal merge that does not bump the version is a no-op for releases. This is the Unreal analog
of Unity's `package.json` + tag gate.

## Atomic, all-gated publish

The `release` job `needs` **every** test job (per UE version) **and** every `build` job (the
`BuildPlugin` zips) **and** the release-notes job. It downloads all per-UE-version plugin zips and
creates the GitHub Release **+ tag** in a single `softprops/action-gh-release@v2` call
(`fail_on_unmatched_files: true`). A failed test or build → **no release**; a stranded asset can't
produce a partial release. This mirrors Unity's atomic `release-unity-plugin`.

## What the release carries

One **plugin zip per supported UE version** (`<Module>-ue5.6.zip`, `<Module>-ue5.7.zip`), each a
`BuildPlugin -Rocket` package with the plugin folder at the archive root. These are exactly what
`unreal-mcp-cli install-extension` downloads and unpacks into a consumer project's `Plugins/<Module>/`.

## Tracking the core version

`commands/update-core.ps1` queries the latest `IvanMurzak/Unreal-MCP` release and records it as
`minCoreVersion` in `extension.json` — the compatibility floor the install resolver reads. It does
**not** pin a version inside the `.uplugin` (a UE plugin dependency carries no version); the floor is
advisory install-catalog metadata.

## Typical release flow

1. `./commands/bump-version.ps1 -NewVersion "x.y.z"` (or run the `bump_version` workflow → merge its PR).
2. Push/merge to `main`.
3. `release.yml` sees a fresh version, runs the full suite, packages per UE version, and publishes the
   atomic Release + tag.
