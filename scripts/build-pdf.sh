#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
output_dir="$root_dir/dist"
output_html="$output_dir/hakoniwa-design-docs.html"
output_pdf="$output_dir/hakoniwa-design-docs.pdf"

# Ensure fontconfig cache is writable
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/fontconfig-cache}"
mkdir -p "$XDG_CACHE_HOME"

"$root_dir/scripts/build-html.sh"

weasyprint "$output_html" "$output_pdf"

echo "Generated: $output_pdf"
