-- Front application display in center
local colors = require("colors")

local function setup_front_app()
  local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")

  local add_cmd = string.format(
    "sketchybar --add item front_app center " ..
    "--set front_app " ..
    "icon.font=\"JetBrainsMono Nerd Font:Bold:13.0\" " ..
    "label.font=\"JetBrainsMono Nerd Font:Bold:12.0\" " ..
    "icon.color=0x%08x label.color=0x%08x " ..
    "background.color=0x%08x background.drawing=on background.corner_radius=6 background.height=24 " ..
    "icon.padding_left=8 icon.padding_right=4 label.padding_left=4 label.padding_right=8 " ..
    "script=\"lua '%s/items/front_app_updater.lua'\" " ..
    "--subscribe front_app front_app_switched space_windows_change omniwm_state_changed",
    colors.lavender, colors.text, colors.item_bg, config_dir
  )
  os.execute(add_cmd)

  dofile(config_dir .. "/items/front_app_updater.lua")
end

return setup_front_app
