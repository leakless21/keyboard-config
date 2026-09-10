-- Front App updater for SketchyBar
local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

local json = require("lib.json")
local icons = require("icons")

local app_name = os.getenv("INFO")
local title = ""

-- Attempt to get focused window from OmniWM IPC
local handle = io.popen("omniwmctl query focused-window --format json 2>/dev/null")
if handle then
  local raw = handle:read("*a")
  handle:close()
  if raw and raw ~= "" then
    local success, data = pcall(json.decode, raw)
    if success and data and data.result and data.result.payload and data.result.payload.window then
      local win = data.result.payload.window
      if win.app and win.app.name then
        app_name = win.app.name
      end
      if win.title then
        title = win.title
      end
    end
  end
end

if not app_name or app_name == "" then
  os.execute("sketchybar --set front_app drawing=off")
  return
end

local app_icon = icons.get_app_icon(app_name)

-- Truncate title if long
if #title > 35 then
  title = string.sub(title, 1, 32) .. "..."
end

-- Escape double quotes in title
title = title:gsub('"', '\\"')

local display_label = app_name
if title ~= "" and title ~= app_name then
  display_label = string.format("%s — %s", app_name, title)
end

local cmd = string.format(
  "sketchybar --set front_app icon=\"%s\" label=\"%s\" drawing=on",
  app_icon, display_label
)
os.execute(cmd)
