#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$root_dir/dist"
output_html="$output_dir/hakoniwa-design-docs.html"
css_path="$root_dir/styles/pdf.css"

mkdir -p "$output_dir"

# Render mermaid diagrams to PNG
"$root_dir/scripts/render-mermaid.py" > "$output_dir/mermaid.list" || true

# Collect all markdown files, ensure stable order.
# README first, then all other .md files sorted by path.
ordered_files=()
if [[ -f "$root_dir/README.md" ]]; then
  ordered_files+=("$root_dir/README.md")
fi

while IFS= read -r f; do
  [[ "$f" == "$root_dir/README.md" ]] && continue
  ordered_files+=("$f")
done < <(
  find "$root_dir" -type f -name "*.md" \
    -not -path "$root_dir/dist/*" \
    -not -path "$root_dir/.git/*" \
    | sort
)

if [[ "${#ordered_files[@]}" -eq 0 ]]; then
  echo "No markdown files found." >&2
  exit 1
fi

# Build a temporary markdown where mermaid blocks are replaced with PNG images
combined_md="$output_dir/combined.md"
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
  --metadata title="Hakoniwa Design Docs" \
  -c "$css_path" \
  -o "$output_html"

# Patch pandoc default CSS that WeasyPrint cannot parse
perl -0pi -e 's/gap: min\\(4vw, 1\\.5em\\);/gap: 1.5em;/g; s/overflow-x: auto;/overflow: visible;/g' "$output_html"

echo "Generated: $output_html"
