-- Single-event workspace renderer for OmniWM -> SketchyBar
local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

local json = require("lib.json")
local colors = require("colors")
local icons = require("icons")

local handle = io.popen("omniwmctl query workspace-bar --format json 2>/dev/null")
if not handle then return end
local raw = handle:read("*a")
handle:close()

if not raw or raw == "" then return end

local success, data = pcall(json.decode, raw)
if not success or not data or not data.result or not data.result.payload then
  return
end

local monitors = data.result.payload.monitors
if not monitors or #monitors == 0 then return end

local ws_list = monitors[1].workspaces or {}

local default_names = {
  [1] = "WEB",
  [2] = "DEV",
  [3] = "COMMS",
  [4] = "RUN",
  [5] = "AUX",
}

local ws_map = {}
for _, w in ipairs(ws_list) do
  local num = tonumber(w.number or w.rawName)
  if num then
    ws_map[num] = w
  end
end

local cmd_parts = { "sketchybar" }

for i = 1, 5 do
  local w = ws_map[i]
  local name = default_names[i]
  local is_focused = false
  local app_icons = {}
  local has_windows = false

  if w then
    if w.displayName and w.displayName ~= "" then
      name = w.displayName
    end
    is_focused = (w.isFocused == true)
    if w.windows and #w.windows > 0 then
      local seen = {}
      for _, win in ipairs(w.windows) do
        local app = win.appName
        if app and app ~= "" and not seen[app] then
          seen[app] = true
          has_windows = true
          table.insert(app_icons, icons.get_app_icon(app))
        end
      end
    end
  end

  local label_text = name
  if #app_icons > 0 then
    label_text = name .. "  " .. table.concat(app_icons, " ")
  end

  local bg_color, bg_drawing, fg_color
  if is_focused then
    bg_color = colors.active_bg
    bg_drawing = "on"
    fg_color = colors.active_fg
  elseif has_windows then
    bg_color = colors.occupied_bg
    bg_drawing = "on"
    fg_color = colors.occupied_fg
  else
    bg_color = colors.transparent
    bg_drawing = "off"
    fg_color = colors.empty_fg
  end

  local item_cmd = string.format(
    "--set workspace.%d icon=\"%d\" label=\"%s\" background.color=0x%08x background.drawing=%s icon.color=0x%08x label.color=0x%08x",
    i, i, label_text, bg_color, bg_drawing, fg_color, fg_color
  )
  table.insert(cmd_parts, item_cmd)
end

os.execute(table.concat(cmd_parts, " "))
