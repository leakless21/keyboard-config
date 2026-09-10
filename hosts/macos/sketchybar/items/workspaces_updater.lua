-- hosts/macos/sketchybar/items/workspaces_updater.lua
-- Multi-monitor, compact event-driven workspace renderer for OmniWM -> SketchyBar

local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

local json = require("lib.json")
local shell = require("lib.shell")
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

-- Aggregate workspaces across all monitors for multi-monitor correctness
local ws_map = {}
for _, monitor in ipairs(monitors) do
  local ws_list = monitor.workspaces or {}
  for _, w in ipairs(ws_list) do
    local num = tonumber(w.number or w.rawName)
    if num then
      ws_map[num] = w
    end
  end
end

local default_names = {
  [1] = "WEB",
  [2] = "DEV",
  [3] = "COMMS",
  [4] = "RUN",
  [5] = "AUX",
}

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

  local label_text = ""
  local label_drawing = "off"
  local bg_color, bg_drawing, fg_color

  if is_focused then
    -- ACTIVE: number + semantic name + app icons (e.g. "2 DEV  :ghostty: :openai:")
    if #app_icons > 0 then
      label_text = name .. "  " .. table.concat(app_icons, " ")
    else
      label_text = name
    end
    label_drawing = "on"
    bg_color = colors.active_bg
    bg_drawing = "on"
    fg_color = colors.active_fg
  elseif has_windows then
    -- OCCUPIED: number + app icons only (e.g. "1 :zen_browser:")
    label_text = table.concat(app_icons, " ")
    label_drawing = "on"
    bg_color = colors.occupied_bg
    bg_drawing = "on"
    fg_color = colors.occupied_fg
  else
    -- EMPTY: number only (e.g. "4")
    label_text = ""
    label_drawing = "off"
    bg_color = colors.transparent
    bg_drawing = "off"
    fg_color = colors.empty_fg
  end

  local item_cmd = string.format(
    "--set workspace.%d icon=%s label=%s label.drawing=%s background.color=0x%08x background.drawing=%s icon.color=0x%08x label.color=0x%08x",
    i,
    shell.quote(tostring(i)),
    shell.quote(label_text),
    label_drawing,
    bg_color,
    bg_drawing,
    fg_color,
    fg_color
  )
  table.insert(cmd_parts, item_cmd)
end

os.execute(table.concat(cmd_parts, " "))
