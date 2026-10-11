# Unreal-AI-Template

**Template repo** for Unreal-MCP extension plugins (the Unreal analog of `Unity-AI-Tools-Template`). An
extension is a C++ `Type=Editor` UE plugin implementing `IUnrealMcpToolProvider` that contributes MCP
tools to AI Game Developer (Unreal-MCP).

`commands/init.ps1` (or `init.py`) renames the plugin/module and replaces the placeholders
`YOUR_EXTENSION_MODULE`, `YOUR_EXTENSION_ID`, `YOUR_EXTENSION_DISPLAY_NAME`, `YOUR_TOOL_ID`,
`YOUR_GITHUB_USERNAME_REPOSITORY`, `YOUR_FEATURE_PLUGIN`/`YOUR_FEATURE_MODULE`. Changes here propagate to
every future extension — keep the tokens consistent. After `init`, rewrite this file for the new
extension (what it wraps, its gating plugin, its tool family); it is no longer the template.

## Layout

- `YOUR_EXTENSION_MODULE/` — the plugin (the only folder the release zip ships): `.uplugin` + `Source/<Module>/`
  (`*.Build.cs`, `Private/<Module>Module.cpp` = provider + module, `Private/Tests/` = Automation specs).
- `Tests/e2e/` — `Run-ToolChecks.ps1` harness + `tools/<tool-id>.e2e.ps1`, one check per tool.
- `commands/` — `init`, `bump-version`, `get-version`, `update-core` (excluded from `init` substitution).
- `extension.json` — install-catalog manifest (`version` mirrors the `.uplugin`; `minCoreVersion`, `enginePlugins`, `tools[]`).
- `.github/workflows/` — `*.yml-sample` go live on `init` (`test_unreal_plugin.yml`, `bump_version.yml` already are).
- `docs/claude/` — `architecture.md` (extension shape, contract, init flow), `ci.md` (workflows, repo
  variables, self-hosted runner gating), `release.md` (version gate, atomic source-zip release).
- `README.md` — user walkthrough: scaffold → init → build → register → release → install.

## The contract (read before editing tools)

- `IUnrealMcpToolProvider` (Unreal-MCP `UnrealMcpRuntime/Public/IUnrealMcpToolProvider.h`):
  `GetExtensionId()` / `GetDisplayName()` / `GetExtensionVersion()` / `RegisterTools(FUnrealMcpToolRegistry&)`.
- Tools use the fluent builder: `Registry.Tool("kebab-id").Title(...).Description(...).Param*(...).Handle([](const FUnrealMcpToolCall&){...})`.
- The provider is registered as a **modular feature** in `StartupModule` and unregistered in
  `ShutdownModule`; Unreal-MCP discovers it on boot or live.
- Handlers run on the **game thread** (call editor/engine APIs directly). Tool ids MUST match
  `^[a-z0-9]+(-[a-z0-9]+)*$` or the registry drops them.

## Commands

```powershell
# Scaffold a new extension from the template
./commands/init.ps1 -ExtensionModule "UnrealAINiagara" -ExtensionId "com.company.unreal-ai-niagara" `
  -DisplayName "Unreal AI Niagara" -GitHubRepository "Owner/Unreal-AI-Niagara" -FeaturePlugin "Niagara"
# parity: python commands/init.py --module ... --id ... --name ... --repo ... --feature ...

./commands/bump-version.ps1 -NewVersion "<x.y.z>"  # .uplugin VersionName + GetExtensionVersion() + extension.json
./commands/get-version.ps1                         # prints the .uplugin VersionName
./commands/update-core.ps1                         # refreshes extension.json minCoreVersion from Unreal-MCP releases
```

## Build / test (local loop)

Junction the plugin into a UE project that has the UnrealMCP core plugin available, build with UBT
(`README.md` step 4), and run the Automation specs with filter = the module name. CI does the same on a
self-hosted runner.

## Conventions

- **Naming:** repo `Unreal-AI-<Feature>` (hyphens); plugin + module `UnrealAI<Feature>` (no hyphens — UE
  module names can't contain `-`); C++ prefixes `F*`/`U*`/`I*`; tool ids kebab-case.
- **C++ style:** Unreal — tabs, braces on new lines, UE types. File header: the
  `// Copyright (c) 2026 ...` Apache-2.0 one-liner.
- **Versioning:** the `.uplugin` `VersionName` is the single source of truth; never hand-edit one version
  location alone — use `bump-version.ps1`.
- **Tests:** one UE Automation spec + one E2E `unreal-mcp-cli` check **per tool**.
- **Secrets:** never commit `.env` or tokens.
