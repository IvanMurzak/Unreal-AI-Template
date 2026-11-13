"""Regenerate the README images docs/assets/hero.svg and docs/assets/flow.svg.

Run from anywhere: `python docs/assets/build-svgs.py`. Dependency-free (Python 3.8+); the shared style lives in
svgkit.py next to this file (the ai-game.dev website style used by every AI Game Developer repo).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import svgkit as K  # noqa: E402

M = K.MONO


def code_card():
    x, y, w, h = 760, 70, 420, 240
    lines = [
        [(K.TEXT, "Registry."), (K.BLUE, "Tool"), (K.TEXT, '(TEXT('), ("#F5D08A", '"my-tool"'), (K.TEXT, "))")],
        [(K.TEXT, "  ."), (K.BLUE, "Title"), (K.TEXT, "(TEXT("), ("#F5D08A", '"My Tool"'), (K.TEXT, "))")],
        [(K.TEXT, "  ."), (K.BLUE, "ParamString"), (K.TEXT, "(TEXT("), ("#F5D08A", '"name"'), (K.TEXT, "), …)")],
        [(K.TEXT, "  ."), (K.BLUE, "Handle"), (K.TEXT, "(OnCall);")],
        [(K.MUTED, "// runs on the game thread")],
    ]
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#card)" stroke="{K.HAIR}"/>',
           f'<rect x="{x}" y="{y + 12}" width="3" height="{h - 24}" rx="1.5" fill="{K.RED_TEXT}"/>',
           f'<text x="{x + 24}" y="{y + 38}" class="m" font-size="16" fill="{K.MUTED}">&lt;Module&gt;Module.cpp</text>',
           K.logo(x + w - 40, y + 34, 40)]
    for i, spans in enumerate(lines):
        t = "".join(f'<tspan fill="{c}">{K.esc(s)}</tspan>' for c, s in spans)
        out.append(f'<text x="{x + 24}" y="{y + 84 + i * 34}" class="m" font-size="17">{t}</text>')
    out.append(f'<rect class="blink" x="{x + 24 + 26 * 10.2 + 6}" y="{y + 84 + 4 * 34 - 16}" width="10" height="20" fill="{K.TEXT}"/>')
    return "".join(out)


def hero():
    return K.hero(
        title="Unreal AI ", accent="Template", eyebrow_text="Unreal-MCP extension template",
        subtitle=["Scaffold a C++ editor plugin that", "adds MCP tools for AI agents."],
        chip_items=["Type=Editor", "C++ / UBT", "source zip"], right=code_card(),
        label="Unreal AI Template: scaffold a C++ editor plugin that adds MCP tools to AI Game Developer (Unreal-MCP)")


def flow():
    W, CW, CH, X = 1200, 340, 96, (40, 430, 820)
    steps = [
        ("1  Use this template", "a new GitHub repository", "red"),
        ("2  init", "rename module, fill placeholders", "red"),
        ("3  Add tools", "Registry.Tool(...) per tool", "red"),
        ("4  Build & test", "UBT, Automation specs, E2E", "blue"),
        ("5  Release", "version-gated source zip", "blue"),
        ("6  Install", "unreal-mcp-cli install-extension", "blue"),
    ]
    b = [K.eyebrow(40, 56, "From template to installed extension")]
    rows = (84, 224)
    for i, (t, s, a) in enumerate(steps):
        b.append(K.card(X[i % 3], rows[i // 3], CW, CH, t, s, accent=a))
    for r in rows:
        y = r + CH / 2
        b.append(K.wire(f"M{X[0] + CW} {y} H{X[1]}", K.RED_TEXT, 1.6))
        b.append(K.wire(f"M{X[1] + CW} {y} H{X[2]}", K.RED_TEXT, 1.6, 0.8))
    b.append(K.wire(f"M{X[2] + CW / 2} {rows[0] + CH} V{rows[0] + CH + 22} H{X[0] + CW / 2} V{rows[1]}", K.BLUE, 3.2))
    b.append(K.eyebrow(40, 384, "In the editor"))
    rt = [("Your plugin", "IUnrealMcpToolProvider", "red"),
          ("Unreal-MCP", "finds it as a modular feature", "blue"),
          ("AI agent", "calls your tools over MCP", "green")]
    for i, (t, s, a) in enumerate(rt):
        b.append(K.card(X[i], 412, CW, CH, t, s, accent=a))
    b.append(K.wire(f"M{X[0] + CW} 460 H{X[1]}", K.BLUE, 1.6))
    b.append(K.wire(f"M{X[1] + CW} 460 H{X[2]}", K.GREEN, 1.6, 0.8))
    return K.panel(W, 548, "".join(b),
                   "Six steps: use the template, run init, add tools, build and test, release a source zip, install "
                   "with unreal-mcp-cli. In the editor Unreal-MCP finds the plugin's tool provider and serves its "
                   "tools to the AI agent.")


if __name__ == "__main__":
    K.write(os.path.join(HERE, "hero.svg"), hero())
    K.write(os.path.join(HERE, "flow.svg"), flow())
