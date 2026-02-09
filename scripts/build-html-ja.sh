#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$root_dir/dist"
output_html="$output_dir/hakoniwa-design-docs-ja.html"
css_path="$root_dir/styles/pdf.css"

mkdir -p "$output_dir"

# Render mermaid diagrams to PNG (from all markdown files)
"$root_dir/scripts/render-mermaid.py" > "$output_dir/mermaid.list" || true

# Japanese document set
ordered_files=(
  "$root_dir/src/position-ja.md"
  "$root_dir/src/glossary-ja.md"
  "$root_dir/src/architecture/overview-ja.md"
  "$root_dir/src/architecture/core-functions-ja.md"
  "$root_dir/src/architecture/diagrams-ja.md"
  "$root_dir/src/architecture/repository-mapping-ja.md"
)

# Build a temporary markdown where mermaid blocks are replaced with PNG images
combined_md="$output_dir/combined-ja.md"
: > "$combined_md"

for md in "${ordered_files[@]}"; do
  awk -v rel="mermaid" '
    BEGIN{in_mermaid=0;}
    /^```mermaid[[:space:]]*$/ {in_mermaid=1; ++i; print "![](" rel "/mermaid_" i ".png)"; next}
    /^```[[:space:]]*$/ {if(in_mermaid){in_mermaid=0; next}}
    {if(!in_mermaid){print}}
  ' "$md" >> "$combined_md"
  echo "" >> "$combined_md"
done

pandoc "$combined_md" \
  --standalone \
  --toc \
  --metadata title="Hakoniwa Design Docs (JA)" \
  -c "$css_path" \
  -o "$output_html"

# Patch pandoc default CSS that WeasyPrint cannot parse
perl -0pi -e 's/gap: min\\(4vw, 1\\.5em\\);/gap: 1.5em;/g; s/overflow-x: auto;/overflow: visible;/g' "$output_html"

echo "Generated: $output_html"
