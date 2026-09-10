-- Status items setup on the right side: Wi-Fi, Volume, Battery, Clock
local colors = require("colors")

local function setup_status()
  local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")

  -- Status bracket / item styles
  local common_style = string.format(
    "icon.font=\"JetBrainsMono Nerd Font:Bold:12.0\" " ..
    "label.font=\"JetBrainsMono Nerd Font:Bold:11.0\" " ..
    "icon.color=0x%08x label.color=0x%08x " ..
    "background.color=0x%08x background.drawing=on background.corner_radius=6 background.height=24 " ..
    "icon.padding_left=8 icon.padding_right=4 label.padding_left=4 label.padding_right=8",
    colors.text, colors.text, colors.item_bg
  )

  local commands = {
    -- 1. Clock (updates every 10s)
    string.format("sketchybar --add item status.clock right --set status.clock %s update_freq=10 script=\"lua '%s/items/status_updater.lua' clock\" click_script=\"open -a Calendar\"",
      common_style, config_dir),

    -- 2. Battery (updates on power change or every 60s)
    string.format("sketchybar --add item status.battery right --set status.battery %s update_freq=60 script=\"lua '%s/items/status_updater.lua' battery\" --subscribe status.battery power_source_change system_woke",
      common_style, config_dir),

    -- 3. Volume (updates on volume change)
    string.format("sketchybar --add item status.volume right --set status.volume %s script=\"lua '%s/items/status_updater.lua' volume\" --subscribe status.volume volume_change",
      common_style, config_dir),

    -- 4. Wi-Fi (updates on wifi change or every 30s)
    string.format("sketchybar --add item status.wifi right --set status.wifi %s update_freq=30 script=\"lua '%s/items/status_updater.lua' wifi\" --subscribe status.wifi wifi_change",
      common_style, config_dir),
  }

  for _, cmd in ipairs(commands) do
    os.execute(cmd)
  end

  -- Initial run to populate all values
  dofile(config_dir .. "/items/status_updater.lua")
end

return setup_status
