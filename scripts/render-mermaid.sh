#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mermaid_dir="$root_dir/dist/mermaid"

mkdir -p "$mermaid_dir"

# Find all mermaid code blocks and render to SVG using mmdc
index=0

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

md_files=$(find "$root_dir" -type f -name "*.md" \
  -not -path "$root_dir/dist/*" \
  -not -path "$root_dir/.git/*" \
  | sort)

# Extract mermaid blocks
while IFS= read -r md; do
  awk -v file="$md" -v tmp="$tmp_dir" -v mer="$mermaid_dir" '
    BEGIN{in_mermaid=0; block="";}
    /^```mermaid[[:space:]]*$/ {in_mermaid=1; block=""; next}
    /^```[[:space:]]*$/ {if(in_mermaid){
        cmd = "cat > \"" tmp "/mermaid_" ++i ".mmd\"";
        print block | cmd; close(cmd);
        in_mermaid=0;
      } else {in_mermaid=0}
      next
    }
    {if(in_mermaid){block = block $0 "\n"}}
  ' "$md"

done <<< "$md_files"

# Render all .mmd files
for mmd in "$tmp_dir"/*.mmd; do
  [[ -f "$mmd" ]] || continue
  base=$(basename "$mmd" .mmd)
  svg="$mermaid_dir/${base}.svg"
  mmdc -i "$mmd" -o "$svg" --quiet
  echo "$svg"
done
