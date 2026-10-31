---
name: gmod-server-setup
description: Step-by-step setup of a Garry's Mod dedicated server (srcds) on Windows or Linux using SteamCMD (app 4020). Covers install and update commands, launch options (+gamemode, +map, +maxplayers, +host_workshop_collection, +sv_setsteamaccount), the Game Server Login Token, server.cfg basics, ports, Workshop collections and resource.AddWorkshop for client downloads, installing an admin mod (ULX + ULib) and making yourself superadmin, and basic hardening. Use when someone wants to host or fix a GMod server, add Workshop addons or a gamemode such as DarkRP or TTT, the server does not show in the server browser, players cannot download content, or they need admin on their own server.
---

# GMod dedicated server setup

## 1. Install with SteamCMD

**Windows**

1. Download SteamCMD from Valve and extract it to `C:\steamcmd\`.
2. Run (one line):

```bat
C:\steamcmd\steamcmd.exe +force_install_dir C:\gmodserver\ +login anonymous +app_update 4020 validate +quit
```

**Linux (Debian/Ubuntu)**

1. Create a normal user for the server (do not run it as root): `sudo adduser steam`, then log in as `steam`.
2. Install SteamCMD (on Ubuntu: enable `multiverse`, `sudo dpkg --add-architecture i386`, `sudo apt update`, `sudo apt install steamcmd`).
3. Install the server:

```bash
steamcmd +force_install_dir "$HOME/gmodserver" +login anonymous +app_update 4020 validate +quit
```

Run the same command again whenever Garry's Mod updates; players cannot join a server on an old version.

## 2. Get a Game Server Login Token (GSLT)

1. Go to `https://steamcommunity.com/dev/managegameservers` (the Steam account must meet Valve's requirements, including a verified purchase on Steam).
2. Set "App ID of the base game" to **4000** (Garry's Mod) and add a memo.
3. Copy the token. Use one token per server and keep it private.

The wiki calls this mandatory: servers without a token are ranked lower in the server browser.

## 3. Launch the server

Windows (`C:\gmodserver\start.bat`):

```bat
srcds.exe -console -game garrysmod +maxplayers 16 +gamemode sandbox +map gm_construct +host_workshop_collection 123456789 +sv_setsteamaccount YOUR_TOKEN
```

Linux (`~/gmodserver/start.sh`):

```bash
./srcds_run -console -game garrysmod +maxplayers 16 +gamemode sandbox +map gm_construct +host_workshop_collection 123456789 +sv_setsteamaccount YOUR_TOKEN
```

- `+gamemode` is the gamemode **folder name**: `sandbox`, `terrortown` (TTT, included with GMod), `darkrp` (install it first, see `darkrp-config`).
- `+map` must exist on the server (`gm_construct` and `gm_flatgrass` ship with the game).
- `-port 27015` changes the port (27015 is the default).
- Put `-` options (engine settings) and `+` options (console commands) on one line.

## 4. server.cfg

Create `garrysmod/cfg/server.cfg`. It runs on every map load.

```
hostname "My GMod Server"
sv_password ""                 // set to make the server private
rcon_password "use-a-long-random-password"
sv_lan 0
sv_allowcslua 0                // never let players run their own Lua
sv_loadingurl ""               // optional custom loading screen URL
sbox_maxprops 150              // sandbox limits (sandbox-based gamemodes)
```

Keep `rcon_password` secret and long, or leave it empty to disable RCON.

## 5. Ports and firewall

- Allow **UDP 27015** inbound (game traffic and server browser).
- Allow **TCP 27015** only if you use remote RCON.
- If you changed `-port`, open that number instead. Home hosting also needs a port forward on the router.

## 6. Workshop addons

1. On the Steam Workshop, create a **Collection** and add the addons, maps and gamemode you want.
2. Set the collection to **Public** or **Unlisted** (private collections cannot be downloaded by the server).
3. Copy the number from the collection URL (`?id=123456789`) into `+host_workshop_collection`.
4. The server downloads and mounts everything at startup. The current map and the gamemode are sent to clients automatically, but **other content (models, materials, sounds) is not**. Add those items for clients in a server file:

```lua
-- garrysmod/lua/autorun/server/workshop_downloads.lua
resource.AddWorkshop( "123456789" )   -- a single item ID, not the collection
resource.AddWorkshop( "987654321" )
```

Only list items that contain content. Lua-only addons are sent automatically and need no line here.

Some maps and addons need Counter-Strike: Source or other game content mounted; see the wiki page on mounting content for dedicated servers.

## 7. Admin mod (ULX + ULib)

1. Add **ULib** (Workshop ID `557962238`) and **ULX** (Workshop ID `557962280`) to your collection, or extract them from GitHub (TeamUlysses) into `garrysmod/addons/`.
2. Do a **full server restart** (a map change is not enough).
3. Join the server, then type in the **server console**:

```
ulx adduser "YourSteamName" superadmin
```

   Or by SteamID (works even when you are offline): `ulx adduserid STEAM_0:1:12345678 superadmin`.
4. In game, open the menu with `ulx menu` in your console (bind it to a key) or use chat commands like `!menu`.

DarkRP also includes FAdmin. Use one admin mod as your main one to avoid conflicts.

## 8. Basic hardening

- Only install addons from authors you trust; never use leaked paid addons (they often contain backdoors). See `gmod-net-security`.
- Keep `sv_allowcslua 0`.
- On Linux, run srcds as the `steam` user, never as root.
- Read and follow the Facepunch Server Operator Rules (accurate player counts and location, no malicious actions against players, banned content).

## Common mistakes

- Using App ID 4020 for the GSLT (the token uses the game's App ID, 4000) or reusing one token on several servers.
- Collection set to Private, so the server downloads nothing.
- Expecting `+host_workshop_collection` alone to make clients download models: add `resource.AddWorkshop` for content items.
- Putting a collection ID in `resource.AddWorkshop`.
- Wrong `+gamemode` value (it is the folder name, all lowercase).
- Installing ULX without ULib, or not doing a full restart afterwards.
- Forgetting to update the server after a GMod update.
- Weak or shared `rcon_password`.

## References

- https://wiki.facepunch.com/gmod/Downloading_a_Dedicated_Server
- https://wiki.facepunch.com/gmod/Linux_Dedicated_Server_Hosting
- https://wiki.facepunch.com/gmod/Steam_Game_Server_Accounts
- https://wiki.facepunch.com/gmod/Workshop_for_Dedicated_Servers
- https://wiki.facepunch.com/gmod/resource.AddWorkshop
- https://wiki.facepunch.com/gmod/Server_Operator_Rules
- https://github.com/TeamUlysses/ulx
