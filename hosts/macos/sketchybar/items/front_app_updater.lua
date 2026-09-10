-- hosts/macos/sketchybar/items/front_app_updater.lua
-- Front App updater for SketchyBar (notch-aware q/center placement, app icon + name)

local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

local json = require("lib.json")
local shell = require("lib.shell")
local icons = require("icons")

local app_name = os.getenv("INFO")
local is_internal = true

-- Attempt to get focused window and monitor information from OmniWM IPC
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
    end
  end
end

-- Check display setup to position at q (notched internal) vs center (external)
local mhandle = io.popen("omniwmctl query workspace-bar --format json 2>/dev/null")
if mhandle then
  local mraw = mhandle:read("*a")
  mhandle:close()
  if mraw and mraw ~= "" then
    local msuccess, mdata = pcall(json.decode, mraw)
    if msuccess and mdata and mdata.result and mdata.result.payload and mdata.result.payload.monitors then
      local monitors = mdata.result.payload.monitors
      local active_id = mdata.result.payload.interactionMonitorId
      for _, m in ipairs(monitors) do
        if m.id == active_id or #monitors == 1 then
          local mname = m.name or ""
          if not mname:find("Built%-in") and not mname:find("Retina") then
            is_internal = false
          end
          break
        end
      end
    end
  end
end

if not app_name or app_name == "" then
  os.execute("sketchybar --set front_app drawing=off")
  return
end

local app_icon = icons.get_app_icon(app_name)
local target_pos = is_internal and "q" or "center"

local cmd = string.format(
  "sketchybar --set front_app position=%s icon=%s label=%s drawing=on",
  target_pos,
  shell.quote(app_icon),
  shell.quote(app_name)
)
os.execute(cmd)
