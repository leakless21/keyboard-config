-- hosts/macos/sketchybar/items/status.lua
-- Status items on right: Wi-Fi (icon only), Volume (icon only), Battery (icon + %), Clock (HH:mm, 60s)

local colors = require("colors")

local function setup_status()
  local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")

  local common_style = string.format(
    "icon.font=\"JetBrainsMono Nerd Font:Bold:12.0\" " ..
    "label.font=\"SF Pro:Semibold:12.0\" " ..
    "icon.color=0x%08x label.color=0x%08x " ..
    "background.color=0x%08x background.drawing=on background.corner_radius=6 background.height=24 " ..
    "icon.padding_left=8 icon.padding_right=4 label.padding_left=4 label.padding_right=8",
    colors.text, colors.text, colors.item_bg
  )

  local commands = {
    -- 1. Clock (HH:mm, updates every 60s)
    string.format(
      "sketchybar --add item status.clock right --set status.clock %s update_freq=60 script=\"lua '%s/items/status_updater.lua' clock\" click_script=\"open -a Calendar\"",
      common_style, config_dir
    ),

    -- 2. Battery (percentage, updates on power change or every 60s)
    string.format(
      "sketchybar --add item status.battery right --set status.battery %s update_freq=60 script=\"lua '%s/items/status_updater.lua' battery\" --subscribe status.battery power_source_change system_woke",
      common_style, config_dir
    ),

    -- 3. Volume (icon only, event-driven on volume_change)
    string.format(
      "sketchybar --add item status.volume right --set status.volume %s label.drawing=off script=\"lua '%s/items/status_updater.lua' volume\" --subscribe status.volume volume_change",
      common_style, config_dir
    ),

    -- 4. Wi-Fi (icon only, event-driven on wifi_change)
    string.format(
      "sketchybar --add item status.wifi right --set status.wifi %s label.drawing=off script=\"lua '%s/items/status_updater.lua' wifi\" --subscribe status.wifi wifi_change",
      common_style, config_dir
    ),
  }

  for _, cmd in ipairs(commands) do
    os.execute(cmd)
  end

  -- Initial run to populate all values
  dofile(config_dir .. "/items/status_updater.lua")
end

return setup_status
