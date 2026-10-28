#!/usr/bin/env bash
# List ManifestWorks whose current generation has not been applied by the
# work agent: status.conditions[Applied].observedGeneration is behind
# metadata.generation, or there is no Applied condition at all.
# Reads only the hub, so it uses a single clock.
#
# Usage: hack/stale-works.sh             (queries the current kube context)
#        hack/stale-works.sh <file.json>  (reads saved `kubectl get manifestwork -A -o json`)
set -euo pipefail

if [ "$#" -gt 0 ]; then
  cat "$1"
else
  kubectl get manifestwork -A -o json
fi | jq -r '.items[]
  | . as $w
  | ([.status.conditions[]? | select(.type == "Applied")][0]) as $c
  | select(($c.observedGeneration // 0) < $w.metadata.generation)
  | "\($w.metadata.namespace)/\($w.metadata.name) gen=\($w.metadata.generation) applied=\($c.observedGeneration // "none")"'
