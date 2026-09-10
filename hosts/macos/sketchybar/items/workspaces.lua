-- hosts/macos/sketchybar/items/workspaces.lua
-- Workspaces item setup for SketchyBar

local colors = require("colors")
local icons = require("icons")

local function setup_workspaces()
  local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")

  -- Register custom OmniWM event
  os.execute("sketchybar --add event omniwm_state_changed")

  -- Apple Logo Item
  local apple_cmd = string.format(
    "sketchybar --add item apple left " ..
    "--set apple icon=\"%s\" icon.color=0x%08x label.drawing=off background.drawing=off padding_right=12 click_script=\"open -a 'System Settings'\"",
    icons.apple, colors.lavender
  )
  os.execute(apple_cmd)

  -- Workspace names
  local ws_names = {
    [1] = "WEB",
    [2] = "DEV",
    [3] = "COMMS",
    [4] = "RUN",
    [5] = "AUX",
  }

  -- Add the 5 workspace items
  local batch_add = { "sketchybar" }
  for i = 1, 5 do
    table.insert(batch_add, string.format("--add item workspace.%d left", i))
  end
  os.execute(table.concat(batch_add, " "))

  local batch_init = { "sketchybar" }
  for i = 1, 5 do
    local item_cmd = string.format(
      "--set workspace.%d icon=\"%d\" label=\"%s\" " ..
      "click_script=\"omniwmctl command switch-workspace %d\" " ..
      "icon.font=\"JetBrainsMono Nerd Font:Bold:12.0\" " ..
      "label.font=\"sketchybar-app-font:Regular:12.0\" " ..
      "icon.color=0x%08x label.color=0x%08x " ..
      "background.height=24 background.corner_radius=6 background.color=0x%08x background.drawing=off " ..
      "icon.padding_left=8 icon.padding_right=4 label.padding_left=4 label.padding_right=8",
      i, i, ws_names[i], i, colors.empty_fg, colors.empty_fg, colors.transparent
    )
    table.insert(batch_init, item_cmd)
  end
  os.execute(table.concat(batch_init, " "))

  -- Add invisible updater item that listens to omniwm_state_changed, front_app_switched, system_woke, display_change
  local updater_cmd = string.format(
    "sketchybar --add item workspace_listener left " ..
    "--set workspace_listener drawing=off script=\"lua '%s/items/workspaces_updater.lua'\" " ..
    "--subscribe workspace_listener omniwm_state_changed front_app_switched system_woke display_change",
    config_dir
  )
  os.execute(updater_cmd)

  -- Run updater once to populate current state
  dofile(config_dir .. "/items/workspaces_updater.lua")
end

return setup_workspaces
