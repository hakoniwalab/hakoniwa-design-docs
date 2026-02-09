#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$root_dir/dist"
output_html="$output_dir/hakoniwa-design-docs-en.html"
css_path="$root_dir/styles/pdf.css"

mkdir -p "$output_dir"

# Render mermaid diagrams to PNG (from all markdown files)
"$root_dir/scripts/render-mermaid.py" > "$output_dir/mermaid.list" || true

# English document set
ordered_files=(
  "$root_dir/README.md"
  "$root_dir/src/position.md"
  "$root_dir/src/glossary.md"
  "$root_dir/src/architecture/overview.md"
  "$root_dir/src/architecture/core-functions.md"
  "$root_dir/src/architecture/diagrams.md"
  "$root_dir/src/architecture/repository-mapping.md"
)

# Build a temporary markdown where mermaid blocks are replaced with PNG images
combined_md="$output_dir/combined-en.md"
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
  --metadata title="Hakoniwa Design Docs (EN)" \
  -c "$css_path" \
  -o "$output_html"

echo "Generated: $output_html"
