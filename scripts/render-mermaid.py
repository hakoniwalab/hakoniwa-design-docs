#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
MERMAID_DIR = ROOT / "dist" / "mermaid"
PUPPETEER_CFG = ROOT / "scripts" / "puppeteer.json"
MERMAID_CFG = ROOT / "scripts" / "mermaid-config.json"

MERMAID_DIR.mkdir(parents=True, exist_ok=True)

md_files = sorted(
    p for p in ROOT.rglob("*.md")
    if "dist" not in p.parts and ".git" not in p.parts
)

blocks = []

for md in md_files:
    with md.open("r", encoding="utf-8") as f:
        in_mermaid = False
        buf = []
        for line in f:
            if line.strip() == "```mermaid":
                in_mermaid = True
                buf = []
                continue
            if line.strip() == "```" and in_mermaid:
                in_mermaid = False
                blocks.append("".join(buf))
                continue
            if in_mermaid:
                buf.append(line)

for idx, block in enumerate(blocks, start=1):
    mmd_path = MERMAID_DIR / f"mermaid_{idx}.mmd"
    png_path = MERMAID_DIR / f"mermaid_{idx}.png"
    mmd_path.write_text(block, encoding="utf-8")
    cmd = [
        "mmdc",
        "-i",
        str(mmd_path),
        "-o",
        str(png_path),
        "--quiet",
        "--puppeteerConfigFile",
        str(PUPPETEER_CFG),
        "-c",
        str(MERMAID_CFG),
    ]
    subprocess.run(cmd, check=True)
    print(png_path)
