#!/usr/bin/env sh
# Rebuilds src/superwand/studio/static/studio.css from the Studio template.
# Run after changing classes in templates/index.html. Needs Node.js (npx).
set -eu
cd "$(dirname "$0")"
npx --yes tailwindcss@3.4.17 \
  --config tailwind.config.js \
  --input input.css \
  --output ../../src/superwand/studio/static/studio.css \
  --minify
