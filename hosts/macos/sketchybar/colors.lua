-- Catppuccin Mocha Palette for SketchyBar
-- ARGB format: 0xAARRGGBB

local colors = {
  -- Base Catppuccin Mocha
  base        = 0xff1e1e2e,
  mantle      = 0xff181825,
  crust       = 0xff11111b,
  surface0    = 0xff313244,
  surface1    = 0xff45475a,
  surface2    = 0xff585b70,
  overlay0    = 0xff6c7086,
  overlay1    = 0xff7f849c,
  subtext0    = 0xffa6adc8,
  subtext1    = 0xffbac2de,
  text        = 0xffcdd6f4,
  lavender    = 0xffb4befe,
  blue        = 0xff89b4fa,
  sapphire    = 0xff74c7ec,
  sky         = 0xff89dceb,
  teal        = 0xff94e2d5,
  green       = 0xffa6e3a1,
  yellow      = 0xfff9e2af,
  peach       = 0xfffab387,
  maroon      = 0xffeba0ac,
  red         = 0xfff38ba8,
  mauve       = 0xffcba6f7,
  pink        = 0xfff5c2e7,
  flamingo    = 0xfff2cdcd,
  rosewater   = 0xfff5e0dc,
  transparent = 0x00000000,

  -- Bar surfaces
  bar_bg      = 0xe6181825,  -- 90% opacity Mantle
  bar_border  = 0x33b4befe,  -- 20% opacity Lavender border

  -- Workspace Pill Semantic Colors
  active_bg   = 0xffb4befe,  -- Filled Lavender accent
  active_fg   = 0xff11111b,  -- Dark crust text on active
  occupied_bg = 0x4d313244,  -- 30% opacity Surface0 for occupied
  occupied_fg = 0xffcdd6f4,  -- Text
  empty_bg    = 0x00000000,  -- Transparent for empty
  empty_fg    = 0xff585b70,  -- Subtle Surface2
  urgent_bg   = 0xfff38ba8,  -- Red for attention/urgent
  urgent_fg   = 0xff11111b,

  -- Status / Item backgrounds
  item_bg     = 0x66313244,  -- 40% opacity Surface0
  item_border = 0x22b4befe,
}

return colors
