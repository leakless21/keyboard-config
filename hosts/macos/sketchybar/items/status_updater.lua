-- hosts/macos/sketchybar/items/status_updater.lua
-- Simplified status updater: Wi-Fi (icon only), Volume (icon only), Battery (icon + %), Clock (HH:mm)

local config_dir = os.getenv("CONFIG_DIR") or (os.getenv("HOME") .. "/.config/sketchybar")
package.path = config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua;" .. package.path

local icons = require("icons")
local shell = require("lib.shell")

local target = arg[1] or "all"

local function update_clock()
  local time_str = os.date("%H:%M")
  local cmd = string.format(
    "sketchybar --set status.clock icon=%s label=%s",
    shell.quote(icons.clock),
    shell.quote(time_str)
  )
  os.execute(cmd)
end

local function update_battery()
  local f = io.popen("pmset -g batt 2>/dev/null")
  local out = f and f:read("*a") or ""
  if f then f:close() end

  local pct = tonumber(out:match("(%d+)%%")) or 100
  local is_charging = (out:match("charging") ~= nil) and not (out:match("discharging") ~= nil)
  local on_ac = (out:match("AC Power") ~= nil)

  local icon = icons.battery.med
  if is_charging or on_ac then
    icon = icons.battery.charging
  elseif pct > 85 then
    icon = icons.battery.full
  elseif pct > 60 then
    icon = icons.battery.high
  elseif pct > 35 then
    icon = icons.battery.med
  elseif pct > 15 then
    icon = icons.battery.low
  else
    icon = icons.battery.empty
  end

  local label_str = string.format("%d%%", pct)
  local cmd = string.format(
    "sketchybar --set status.battery icon=%s label=%s",
    shell.quote(icon),
    shell.quote(label_str)
  )
  os.execute(cmd)
end

local function update_volume()
  local f = io.popen("osascript -e 'get volume settings' 2>/dev/null")
  local out = f and f:read("*a") or ""
  if f then f:close() end

  local vol = tonumber(out:match("output volume:(%d+)")) or 0
  local muted = (out:match("output muted:true") ~= nil)

  local icon = icons.volume.muted
  if not muted then
    if vol > 60 then
      icon = icons.volume.high
    elseif vol > 25 then
      icon = icons.volume.med
    else
      icon = icons.volume.low
    end
  end

  local cmd = string.format(
    "sketchybar --set status.volume icon=%s label.drawing=off",
    shell.quote(icon)
  )
  os.execute(cmd)
end

local function update_wifi()
  local f = io.popen("ipconfig getsummary en0 2>/dev/null | grep ' SSID'")
  local out = f and f:read("*a") or ""
  if f then f:close() end

  local ssid = out:match("SSID%s*:%s*(.+)")
  local icon = icons.wifi.disconnected

  if ssid and ssid ~= "" and not ssid:match("<redacted>") then
    icon = icons.wifi.connected
  elseif ssid and ssid:match("<redacted>") then
    icon = icons.wifi.connected
  end

  local cmd = string.format(
    "sketchybar --set status.wifi icon=%s label.drawing=off",
    shell.quote(icon)
  )
  os.execute(cmd)
end

if target == "clock" then
  update_clock()
elseif target == "battery" then
  update_battery()
elseif target == "volume" then
  update_volume()
elseif target == "wifi" then
  update_wifi()
else
  update_wifi()
  update_volume()
  update_battery()
  update_clock()
end
