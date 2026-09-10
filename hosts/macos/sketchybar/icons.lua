-- hosts/macos/sketchybar/icons.lua
-- Semantic icon mappings for SketchyBar
-- Typography target:
--   SF Pro: regular labels
--   JetBrains Mono Nerd Font: generic status/control glyphs
--   SketchyBar App Font: application icons

local app_icons = require("lib.app_icons")

local icons = {
  apple = "",
  media = "♫",

  wifi = {
    connected    = "󰖩",
    disconnected = "󰖪",
  },

  volume = {
    high  = "󰕾",
    med   = "󰖀",
    low   = "󰕿",
    muted = "󰝟",
  },

  battery = {
    charging = "󰂄",
    full     = "󰁹",
    high     = "󰂀",
    med      = "󰁾",
    low      = "󰁼",
    empty    = "󰁺",
  },

  clock = "󰥔",

  -- Minimal fallback map for bundle identifiers or non-standard names
  fallback_apps = {
    ["ChatGPT"]              = ":openai:",
    ["com.openai.codex"]     = ":codex:",
    ["Codex"]                = ":codex:",
    ["Dia"]                  = ":dia:",
    ["com.mitchellh.ghostty"]= ":ghostty:",
    ["dev.zed.Zed"]          = ":zed:",
    ["app.zen-browser.zen"]   = ":zen_browser:",
    ["default"]              = ":default:",
  },
}

function icons.get_app_icon(app_name)
  if not app_name or app_name == "" then
    return icons.fallback_apps["default"]
  end

  -- 1. Direct lookup in comprehensive SketchyBar App Font map
  local icon = app_icons[app_name]
  if icon then return icon end

  -- 2. Fallback map lookup
  icon = icons.fallback_apps[app_name]
  if icon then return icon end

  -- 3. Trimmed lookup
  local trimmed = app_name:match("^%s*(.-)%s*$")
  if trimmed and trimmed ~= app_name then
    icon = app_icons[trimmed] or icons.fallback_apps[trimmed]
    if icon then return icon end
  end

  return icons.fallback_apps["default"]
end

return icons
