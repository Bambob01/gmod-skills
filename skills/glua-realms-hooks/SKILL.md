---
name: glua-realms-hooks
description: Explains Garry's Mod Lua realms (server, client, shared, menu), how file location decides where a file runs, the AddCSLuaFile + include loading pattern, and the hook library (hook.Add, hook.Remove, hook.Run). Use when writing or reviewing any GLua addon code, deciding where a file or function belongs, laying out an autorun loader, adding or creating hooks, or fixing errors caused by code running in the wrong realm (for example "attempt to call global 'LocalPlayer' (a nil value)" on the server, or "Couldn't include file").
---

# GLua realms and hooks

Garry's Mod runs separate Lua states. Most bugs in new addons come from code running in the wrong one.

## The realms

| Realm | Where it runs | Check with |
|---|---|---|
| Server | The server (dedicated or the host of a listen server). Physics, entities, saving data, authority. | `SERVER` is `true` |
| Client | Each player's game. HUD, menus (VGUI/Derma), rendering, input. | `CLIENT` is `true` |
| Shared | Not a separate state: the same file is loaded on both sides, but each copy runs separately. | - |
| Menu | The main menu only. Addons almost never need it. | `MENU_DLL` |

`if SERVER and CLIENT then` is never true. Shared code that touches client-only libraries must still branch with `if CLIENT then`.

## Which file runs where

| Location | Realm | Sent to clients automatically? |
|---|---|---|
| `lua/autorun/*.lua` | Shared | Yes |
| `lua/autorun/server/*.lua` | Server | No (never sent) |
| `lua/autorun/client/*.lua` | Client | Yes |
| `lua/entities/<name>/init.lua`, `lua/weapons/<name>/init.lua` | Server | No |
| `lua/entities/<name>/cl_init.lua`, `.../shared.lua` | Client / shared | Only if you `AddCSLuaFile` them |
| `lua/vgui/*.lua` | Client, but only when you `include` it | Yes |
| Anything else under `lua/` | Only when you `include` it | Only if you `AddCSLuaFile` it |

The common `sv_` / `cl_` / `sh_` filename prefixes are a community convention, not something the engine reads. Use them anyway so humans can tell realms apart.

## AddCSLuaFile vs include

- `AddCSLuaFile( path )` (server-side) marks a file to be **downloaded** by clients. It does not run it. On the client it does nothing, so it is safe in shared files. With no argument it sends the current file.
- `include( path )` **runs** a file in the current realm and returns whatever the file returns.
- A client or shared file needs both: `AddCSLuaFile` on the server, then `include` on the client.
- Paths are relative to the current file or to `lua/` (for example `"myaddon/sh_config.lua"`).
- Empty files fail to send and fail to include. Paths must not contain spaces.

## Step-by-step: a clean loader

1. Pick a unique folder name, for example `lua/myaddon/`. All addons share one virtual `lua/` folder, so generic names like `lua/config.lua` collide.
2. Create one shared entry point in `lua/autorun/`:

```lua
-- lua/autorun/myaddon_load.lua (runs on server AND client)
MyAddon = MyAddon or {}

if SERVER then
    AddCSLuaFile( "myaddon/sh_config.lua" )
    AddCSLuaFile( "myaddon/cl_hud.lua" )

    include( "myaddon/sh_config.lua" )
    include( "myaddon/sv_main.lua" )   -- never AddCSLuaFile server files
else
    include( "myaddon/sh_config.lua" )
    include( "myaddon/cl_hud.lua" )
end
```

3. Keep secrets (API keys, database passwords, admin logic) only in `sv_` files. Every file sent with `AddCSLuaFile` can be read by players.

## Hooks

Hooks let many addons react to the same event without overwriting each other.

```lua
-- Server: greet players when they spawn
hook.Add( "PlayerSpawn", "MyAddon_Greet", function( ply )
    ply:ChatPrint( "Welcome back, " .. ply:Nick() )
end )

-- Remove it later with the same event name + identifier
hook.Remove( "PlayerSpawn", "MyAddon_Greet" )
```

- `hook.Add( eventName, identifier, func )`. The identifier should be a unique string (prefix it with your addon name). Adding again with the same identifier replaces the old function, which makes Lua auto-refresh safe.
- The identifier can also be an object with `IsValid`, such as a Panel or Entity. It is passed as the first argument, and the hook is removed automatically once the object is invalid. Numbers and booleans are not allowed.
- Hook order is not guaranteed.
- **Return values matter.** Returning anything other than `nil` stops all remaining hooks for that event and the gamemode's own `GM:` function. Only return when the hook's wiki page has a "Returns" section and you mean it.

```lua
-- Bad: always returns, so it breaks every other addon using PlayerSpawnProp
hook.Add( "PlayerSpawnProp", "MyAddon_Props", function( ply, model )
    if ply:IsAdmin() then return true end
    return false
end )

-- Better: only return to block; return nothing to let others decide
hook.Add( "PlayerSpawnProp", "MyAddon_Props", function( ply, model )
    if not ply:IsAdmin() then return false end
end )
```

### Custom hooks

Let other addons extend yours with `hook.Run`:

```lua
-- Inside your addon
local allowed = hook.Run( "MyAddon_CanLevelUp", ply, newLevel )
if allowed == false then return end

-- In someone else's addon
hook.Add( "MyAddon_CanLevelUp", "OtherAddon_Block", function( ply, lvl )
    if lvl > 100 then return false end
end )
```

`hook.Run( name, ... )` calls every hook plus the active gamemode's function of the same name. `hook.Call( name, gmTable, ... )` is the same but you pass the gamemode table yourself.

### Realm reminders for common hooks

- Server: `PlayerInitialSpawn`, `PlayerSpawn`, `PlayerSay`, `PlayerDeath`, `EntityTakeDamage`.
- Client: `HUDPaint`, `HUDShouldDraw`, `OnScreenSizeChanged`, `PostDrawOpaqueRenderables`.
- Shared: `Think`, `Initialize`, `InitPostEntity`, `SetupMove`.
- `PlayerInitialSpawn` runs before the player has finished loading. If you need the client ready, have the client send a net message from `InitPostEntity` and reply to that.

## Common mistakes

- Calling client-only things (`LocalPlayer`, `vgui`, `surface`, `draw`) in server files, or server-only things (`util.AddNetworkString`, `ents.Create`, `ply:Give`) in client files. The error is usually "attempt to call/index ... (a nil value)".
- `include` of a client file without `AddCSLuaFile` on the server: the client says "Couldn't include file".
- `AddCSLuaFile` on a server file, leaking server code to every player.
- Generic hook identifiers like `"think"` that another addon overwrites.
- Returning `false`/`true` from a hook "just in case", breaking other addons.
- Creating hooks inside other hooks or loops, so they get re-added every frame.
- Generic filenames that collide with other addons in the shared `lua/` folder.

## References

- https://wiki.facepunch.com/gmod/States
- https://wiki.facepunch.com/gmod/Global.AddCSLuaFile
- https://wiki.facepunch.com/gmod/Global.include
- https://wiki.facepunch.com/gmod/hook.Add
- https://wiki.facepunch.com/gmod/Hook_Library_Usage
