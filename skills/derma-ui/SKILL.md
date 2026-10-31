---
name: derma-ui
description: Builds Garry's Mod menus and HUD panels with VGUI/Derma on the client. Covers vgui.Create, DFrame, DPanel, DButton, DLabel, DScrollPanel, docking (Dock, DockMargin, DockPadding), custom Paint functions, vgui.Register for reusable panels, resolution scaling with ScrW/ScrH and ScreenScale, surface.CreateFont, and opening menus from a console command or net message. Use when creating or fixing any in-game menu, shop, settings window, scoreboard-style panel or HUD element, or when a menu looks wrong at other resolutions, opens twice, or will not close or take mouse input.
---

# Derma / VGUI menus

Derma is **client-only**. Put UI code in `lua/autorun/client/` or a `cl_` file that is sent with `AddCSLuaFile` and included on the client. `vgui`, `surface` and `draw` do not exist on the server.

## Step-by-step: a basic window

```lua
-- lua/myaddon/cl_menu.lua
MyAddon = MyAddon or {}

local function OpenMenu()
    -- Only one copy open at a time
    if IsValid( MyAddon.Menu ) then MyAddon.Menu:Remove() end

    local frame = vgui.Create( "DFrame" )
    frame:SetSize( ScrW() * 0.4, ScrH() * 0.6 )   -- scale with screen size
    frame:Center()
    frame:SetTitle( "My Addon" )
    frame:SetDraggable( true )
    frame:MakePopup()                             -- gives mouse + keyboard focus
    MyAddon.Menu = frame

    local scroll = vgui.Create( "DScrollPanel", frame )
    scroll:Dock( FILL )

    for i = 1, 20 do
        local btn = scroll:Add( "DButton" )       -- Add() parents to the scroll canvas
        btn:SetText( "Option " .. i )
        btn:SetTall( 30 )
        btn:Dock( TOP )
        btn:DockMargin( 0, 0, 0, 5 )
        btn.DoClick = function()
            -- tell the server what was chosen; the server decides what happens
            chat.AddText( "You picked option " .. i )
        end
    end
end

concommand.Add( "myaddon_menu", OpenMenu )        -- type myaddon_menu in console
```

Opening from the server instead (for example when a player presses E on an NPC): the server sends a net message and the client calls `OpenMenu()` in its `net.Receive`. Any action chosen in the menu must be sent back and **validated on the server** (see `gmod-net-security`).

## Docking and layout

- `panel:Dock( DOCK )` with `FILL`, `TOP`, `BOTTOM`, `LEFT`, `RIGHT` or `NODOCK`.
- Children dock in creation order. Create `TOP`/`BOTTOM` bars first, then the `FILL` panel last.
- `DockMargin( left, top, right, bottom )`: space outside a panel, between siblings.
- `DockPadding( left, top, right, bottom )`: space inside a parent, around its docked children. On a `DScrollPanel`, set padding on `scroll:GetCanvas()`.
- Docked panels still need a size on the free axis: `SetTall` for `TOP`/`BOTTOM`, `SetWide` for `LEFT`/`RIGHT`.
- Prefer docking over hard-coded `SetPos` numbers: it adapts to any size.
- Never call `PerformLayout` yourself; call `panel:InvalidateLayout()` and the engine does it.

## Custom look with Paint

```lua
frame.Paint = function( self, w, h )
    draw.RoundedBox( 8, 0, 0, w, h, Color( 25, 25, 30, 240 ) )
end

btn.Paint = function( self, w, h )
    local col = self:IsHovered() and Color( 70, 120, 200 ) or Color( 50, 50, 60 )
    draw.RoundedBox( 4, 0, 0, w, h, col )
end
```

`Paint` runs every frame the panel is visible, so keep it cheap: no `surface.CreateFont`, no `Material()` calls, no table building inside it. Cache those outside.

## Reusable panels with vgui.Register

```lua
local PANEL = {}

function PANEL:Init()
    self.Label = vgui.Create( "DLabel", self )
    self.Label:Dock( FILL )
    self.Label:SetFont( "MyAddon_Body" )
    self.Label:SetContentAlignment( 5 )   -- 5 = centered
end

function PANEL:SetMessage( text )
    self.Label:SetText( text )
end

function PANEL:Paint( w, h )
    draw.RoundedBox( 6, 0, 0, w, h, Color( 40, 40, 48 ) )
end

vgui.Register( "MyAddon_Card", PANEL, "DPanel" )   -- unique name, base class

-- later: local card = vgui.Create( "MyAddon_Card", parent )
```

## Fonts and scaling

```lua
local function CreateFonts()
    surface.CreateFont( "MyAddon_Title", {
        font = "Roboto",              -- ships with GMod; use the display name, not the file name
        size = ScreenScale( 10 ),     -- scales with screen width (base 640 px)
        weight = 700,
        antialias = true,
    } )
    surface.CreateFont( "MyAddon_Body", {
        font = "Roboto",
        size = ScreenScale( 7 ),
        weight = 500,
    } )
end
CreateFonts()   -- once, when the file loads

hook.Add( "OnScreenSizeChanged", "MyAddon_Fonts", function( oldW, oldH, newW, newH )
    CreateFonts()   -- rebuild for the new resolution
end )
```

- Create fonts once at load time (and again only on resolution change). Never inside `HUDPaint`, `Paint` or `Think`.
- Prefix font names with your addon name so you do not overwrite another addon's font.
- Only make the sizes you actually use; each font costs memory.
- `ScrW()` / `ScrH()` give the current resolution. `ScreenScale( n )` scales from a 640-wide screen; `ScreenScaleH( n )` scales from height. Build sizes from these instead of fixed pixels.
- Default fonts such as `DermaDefault`, `DermaLarge` and `Trebuchet24` need no `CreateFont`.

## Common mistakes

- Creating panels on the server, or in a shared file without `if CLIENT then`.
- Forgetting `MakePopup()`, so the mouse cannot click the menu.
- Opening a new frame every time without removing the old one (stacked invisible windows).
- Creating fonts or panels inside `HUDPaint`/`Paint`, which lags and can crash the game.
- Hard-coded pixel sizes that look tiny at 4K and overflow at 1366x768.
- Using `DScrollPanel:DockPadding` instead of padding its canvas.
- Docking the `FILL` panel before the `TOP`/`BOTTOM` bars.
- Trusting the menu for security: hiding a button does not stop a client from sending the net message.

## References

- https://wiki.facepunch.com/gmod/DFrame
- https://wiki.facepunch.com/gmod/DScrollPanel
- https://wiki.facepunch.com/gmod/Panel:Dock
- https://wiki.facepunch.com/gmod/vgui.Register
- https://wiki.facepunch.com/gmod/surface.CreateFont
- https://wiki.facepunch.com/gmod/Global.ScreenScale
- https://wiki.facepunch.com/gmod/Introduction_To_Using_Derma
