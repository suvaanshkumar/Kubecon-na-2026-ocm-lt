#!/usr/bin/env bash
# Join hub write lines (T1, flow=mw_hub_apply) with work-agent apply lines
# (T2, flow=mw_spoke_apply) on {mw_namespace, mw_name, generation} and print
# hub->managed cluster propagation latency per ManifestWork generation.
#
# A T1 with no T2 older than TIMEOUT_MS is reported as NEVER ARRIVED.
#
# Usage: hack/latency.sh [log files...]   (JSON lines; default: examples/*.log)
#   NOW_MS=<epoch ms>   reference "now" (default: current time)
#   TIMEOUT_MS=<ms>     how long a T1 may wait for its T2 (default: 120000)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ "$#" -eq 0 ]; then
  set -- "${REPO_ROOT}"/examples/*.log
fi

NOW_MS=${NOW_MS:-$(date +%s%3N)}
TIMEOUT_MS=${TIMEOUT_MS:-120000}

cat "$@" | jq -rs --argjson now "${NOW_MS}" --argjson timeout "${TIMEOUT_MS}" '
  map(select(.flow == "mw_hub_apply" or .flow == "mw_spoke_apply"))
  | group_by([.mw_namespace, .mw_name, .generation])
  | map({
      cluster: .[0].mw_namespace,
      work:    .[0].mw_name,
      gen:     .[0].generation,
      t1: (map(select(.flow == "mw_hub_apply")   | .ts_epoch_ms) | min),
      t2: (map(select(.flow == "mw_spoke_apply") | .ts_epoch_ms) | min)
    })
  | map(select(.t1 != null))
  | (["CLUSTER", "WORK", "GEN", "LATENCY"] | @tsv),
    (.[] | [.cluster, .work, (.gen | tostring),
            (if .t2 != null then "\(.t2 - .t1) ms"
             elif ($now - .t1) > $timeout then "NEVER ARRIVED"
             else "pending" end)] | @tsv)
' | column -t -s $'\t'
