#!/bin/bash
# Manual / later-cron helper. Writes to foundation/raw or daily/raw/$DATE.
# Usage: bash tools/scan/query.sh [OUTDIR]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="${1:-$ROOT/foundation/raw/manual_$(date -u +%Y%m%d)}"
mkdir -p "$OUT"
SINCE="$(date -u -d '7 days ago' '+%Y-%m-%d')"

gh_search() {
  local name="$1" q="$2"
  echo "=== $name ==="
  curl -sS "https://api.github.com/search/issues?q=${q}&sort=created&order=desc&per_page=10" \
    > "$OUT/${name}.json"
  python3 - "$OUT/${name}.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print("total", d.get("total_count"))
for i in d.get("items") or []:
    print(f"#{i['number']} {i['title'][:100]}")
    print(" ", i.get("html_url"))
PY
  sleep 8
}

gh_search megatron "repo%3ANVIDIA%2FMegatron-LM+NaN+OR+spike+created%3A%3E%3D${SINCE}"
gh_search deepspeed "repo%3Adeepspeedai%2FDeepSpeed+checkpoint+OR+NaN+created%3A%3E%3D${SINCE}"
gh_search verl "repo%3Avolcengine%2Fverl+mismatch+OR+logprob+created%3A%3E%3D${SINCE}"
gh_search trl "repo%3Ahuggingface%2Ftrl+GRPO+created%3A%3E%3D${SINCE}"
echo "raw -> $OUT"
