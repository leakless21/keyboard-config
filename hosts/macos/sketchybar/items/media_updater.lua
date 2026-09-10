-- hosts/macos/sketchybar/items/media_updater.lua
-- Media player updater for SketchyBar (notch-aware e placement, coexists with front_app)

local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

local json = require("lib.json")
local shell = require("lib.shell")

local info = os.getenv("INFO")
if not info or info == "" then
  os.execute("sketchybar --set media drawing=off")
  return
end

local success, data = pcall(json.decode, info)
if not success or not data then
  os.execute("sketchybar --set media drawing=off")
  return
end

local state = data.state
local artist = data.artist or ""
local title = data.title or ""

if state == "playing" and title ~= "" then
  local label_text = title
  if artist ~= "" then
    label_text = string.format("%s – %s", artist, title)
  end

  if #label_text > 30 then
    label_text = string.sub(label_text, 1, 27) .. "..."
  end

  -- Display-aware position check
  local is_internal = true
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

  local target_pos = is_internal and "e" or "center"

  local cmd = string.format(
    "sketchybar --set media position=%s icon=\"♫\" label=%s drawing=on",
    target_pos,
    shell.quote(label_text)
  )
  os.execute(cmd)
else
  os.execute("sketchybar --set media drawing=off")
end
