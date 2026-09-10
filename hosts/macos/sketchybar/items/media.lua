-- Media display in center (shown when media is active)
local colors = require("colors")

local function setup_media()
  local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")

  local add_cmd = string.format(
    "sketchybar --add item media center " ..
    "--set media drawing=off " ..
    "icon.font=\"JetBrainsMono Nerd Font:Bold:13.0\" " ..
    "label.font=\"JetBrainsMono Nerd Font:Bold:12.0\" " ..
    "icon.color=0x%08x label.color=0x%08x " ..
    "background.color=0x%08x background.drawing=on background.corner_radius=6 background.height=24 " ..
    "icon.padding_left=8 icon.padding_right=4 label.padding_left=4 label.padding_right=8 " ..
    "script=\"lua '%s/items/media_updater.lua'\" " ..
    "--subscribe media media_change",
    colors.green, colors.text, colors.item_bg, config_dir
  )
  os.execute(add_cmd)
end

return setup_media
