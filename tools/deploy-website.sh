#!/usr/bin/env bash
set -euo pipefail
spp_project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
: "${SPP_SITE_HOST:?Set SPP_SITE_HOST to the authorized SSH destination}"
: "${SPP_SITE_DIRECTORY:?Set SPP_SITE_DIRECTORY to the remote static site directory}"
if [[ ! "$SPP_SITE_DIRECTORY" =~ ^/[A-Za-z0-9_./-]+$ || "$SPP_SITE_DIRECTORY" == / ]]; then
  printf 'Use an absolute destination path containing only letters, digits, _, ., / and -.\n' >&2
  exit 2
fi
python3 "$spp_project_dir/website/check_site.py"
python3 "$spp_project_dir/tools/check_public_sources.py"
tar -C "$spp_project_dir/website/dist" -czf - . | ssh -- "$SPP_SITE_HOST" "mkdir -p -- '$SPP_SITE_DIRECTORY' && tar -xzf - -C '$SPP_SITE_DIRECTORY'"
