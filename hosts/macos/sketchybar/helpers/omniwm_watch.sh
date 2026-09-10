#!/usr/bin/env sh
# helpers/omniwm_watch.sh
# Bridge OmniWM IPC events to SketchyBar

# Kill any existing watcher processes to prevent duplicate streams
pgrep -fl "omniwmctl watch.*sketchybar" | awk '{print $1}' | while read -r pid; do
  if [ "$pid" != "$$" ]; then
    kill "$pid" 2>/dev/null || true
  fi
done

# Run omniwmctl watch with --reconnect
# Subscriptions: active-workspace, workspace-bar, focus, display-changed, layout-changed
exec omniwmctl watch \
  active-workspace,workspace-bar,focus,display-changed,layout-changed \
  --reconnect \
  --exec sketchybar --trigger omniwm_state_changed
