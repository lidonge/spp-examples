#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 1 ]]; then
  printf 'Usage: %s /path/to/authorized/spplang-checkout\n' "$0" >&2
  exit 2
fi
spp_toolchain_dir=$(cd -- "$1" && pwd)
if [[ ! -f "$spp_toolchain_dir/generator/pom.xml" || ! -f "$spp_toolchain_dir/appframe/pom.xml" ]]; then
  printf 'The selected directory does not contain the S++ compiler/runtime project.\n' >&2
  exit 2
fi
mvn -f "$spp_toolchain_dir/pom.xml" -pl generator,appframe -am install -DskipTests
