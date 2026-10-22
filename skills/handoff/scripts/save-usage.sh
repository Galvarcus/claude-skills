#!/bin/bash

# Save the context and rate limit usage from status line input, so that
# handoff-check.sh can read it. Hooks do not receive this data, and the
# status line does. Pipe the status line input into this script.

input=$(cat)
session=$(jq -r '.session_id // empty' <<<"$input")
[ -n "$session" ] || exit 0
state="$HOME/.claude/state/handoff"
mkdir -p "$state"
# Write then rename, so the hook never reads a half written file.
jq '{context: .context_window.used_percentage,
     five_hour: .rate_limits.five_hour,
     seven_day: .rate_limits.seven_day}' <<<"$input" >"$state/$session.tmp" &&
  mv "$state/$session.tmp" "$state/$session.json"
