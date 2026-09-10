-- Icon mappings using Nerd Font glyphs (compatible with JetBrains Mono Nerd Font)

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
    low      = "󰁻",
    empty    = "󰁺",
  },

  clock = "󰥔",

  -- App icon lookup table
  apps = {
    ["Safari"]            = "",
    ["Google Chrome"]     = "",
    ["Chrome"]            = "",
    ["Zen"]               = "",
    ["Zen Browser"]       = "",
    ["Firefox"]           = "",
    ["Arc"]               = "󰞍",
    ["Brave Browser"]     = "",
    ["Ghostty"]           = "",
    ["Terminal"]          = "",
    ["iTerm2"]            = "",
    ["Alacritty"]         = "",
    ["Kitty"]             = "",
    ["Zed"]               = "",
    ["Code"]              = "󰨞",
    ["Visual Studio Code"]= "󰨞",
    ["Cursor"]            = "󰨞",
    ["Sublime Text"]      = "󰅩",
    ["Discord"]           = "󰙯",
    ["Vesktop"]           = "󰙯",
    ["Slack"]             = "󰒱",
    ["Messages"]          = "󰍡",
    ["Mail"]              = "󰇮",
    ["Microsoft Outlook"] = "󰇮",
    ["Outlook"]           = "󰇮",
    ["Spotify"]           = "󰓇",
    ["Music"]             = "",
    ["Finder"]            = "󰀶",
    ["System Settings"]   = "󰒓",
    ["System Preferences"]= "󰒓",
    ["Simulator"]         = "󰢹",
    ["Docker"]            = "󰡨",
    ["Obsidian"]          = "󰠮",
    ["Notion"]            = "󰠮",
    ["Notes"]             = "󰠮",
    ["Linear"]            = "󰒓",
    ["default"]           = "󰘔",
  },
}

function icons.get_app_icon(app_name)
  if not app_name or app_name == "" then
    return icons.apps["default"]
  end
  return icons.apps[app_name] or icons.apps["default"]
end

return icons
