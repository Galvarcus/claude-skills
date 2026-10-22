#!/bin/bash

# Hook for UserPromptSubmit and PostToolUse. Asks Claude to write a
# handoff when context or a rate limit reaches HANDOFF_THRESHOLD, default
# 90. Reads the usage that save-usage.sh saves from the status line.
# Context fires once per session and rearms after compaction. Each rate
# limit fires once per window across all sessions.

input=$(cat)
session=$(jq -r '.session_id // empty' <<<"$input")
event=$(jq -r '.hook_event_name // "UserPromptSubmit"' <<<"$input")
state="$HOME/.claude/state/handoff"
snapshot="$state/$session.json"
[ -n "$session" ] && [ -f "$snapshot" ] || exit 0
threshold=${HANDOFF_THRESHOLD:-90}
session_fired="$state/$session.fired"
limit_fired="$state/limits.fired"
touch "$session_fired" "$limit_fired"
find "$state" -type f -mtime +8 -delete 2>/dev/null

reasons=()

# FUNCTION: Add a reason when pct reaches the threshold and key has not
# fired yet in fired_file.
check() {
  local key=$1 label=$2 pct=$3 fired_file=$4
  [ -n "$pct" ] && [ "$pct" != null ] || return
  pct=${pct%.*}
  [ "$pct" -ge "$threshold" ] || return
  grep -qxF "$key" "$fired_file" && return
  echo "$key" >>"$fired_file"
  reasons+=("$label at $pct%")
}

context=$(jq -r '.context // empty' "$snapshot")
# Compaction drops context well below the threshold, so clear the marker
# and let a later rise fire again.
if [ -n "$context" ] && [ "${context%.*}" -lt 50 ]; then
  sed -i '' '/^context$/d' "$session_fired" 2>/dev/null ||
    sed -i '/^context$/d' "$session_fired"
fi
check context "Context window" "$context" "$session_fired"
check "five_hour:$(jq -r '.five_hour.resets_at // empty' "$snapshot")" \
  "5-hour usage limit" "$(jq -r '.five_hour.used_percentage // empty' "$snapshot")" \
  "$limit_fired"
check "seven_day:$(jq -r '.seven_day.resets_at // empty' "$snapshot")" \
  "Weekly usage limit" "$(jq -r '.seven_day.used_percentage // empty' "$snapshot")" \
  "$limit_fired"

[ ${#reasons[@]} -gt 0 ] || exit 0
joined=$(printf '%s, ' "${reasons[@]}")
message="Handoff threshold reached: ${joined%, }. Use the handoff skill now to write or update the handoff file, then continue the current task."
jq -n --arg event "$event" --arg msg "$message" \
  '{hookSpecificOutput: {hookEventName: $event, additionalContext: $msg}}'
