---
name: gmod-net-security
description: Defensive guide to writing safe Garry's Mod net messages and auditing addons. Covers util.AddNetworkString, net.Receive on the server, validating every value a client sends, permission and distance checks, per-player rate limiting, size limits, keeping secrets out of client files, and recognising common backdoor and exploit patterns so they can be removed. Use when writing or reviewing any net.Receive, net.Start or concommand code, building shops, admin tools or anything that changes money, items or ranks, or when checking a downloaded or leaked addon for backdoors. Defensive only; never use it to write exploits.
---

# Safe GMod networking

**Golden rule: the server never trusts the client.** Anything a client sends can be forged, repeated thousands of times per second, or sent with values your UI would never allow. Cheaters can also read every client-side Lua file.

## How net messages work (quick recap)

1. Server registers the name once at load: `util.AddNetworkString( "myaddon_buy" )`. Unregistered names fail to send.
2. Sender: `net.Start( name )`, `net.Write*` calls, then `net.SendToServer()` (client) or `net.Send( ply )` / `net.Broadcast()` (server).
3. Receiver: `net.Receive( name, function( len, ply ) ... end )`. `len` is the size in **bits**. `ply` (the sender) only exists server-side.
4. Read values in exactly the same order and with the same bit sizes they were written.
5. Limit: about 64 KB per message. Huge or frequent reliable messages overflow the channel and disconnect players.

## Step-by-step: a safe server receiver

```lua
-- lua/myaddon/sv_net.lua (server only, never AddCSLuaFile it)
util.AddNetworkString( "myaddon_buy" )

local ITEMS = {                      -- prices live on the SERVER
    [1] = { name = "Medkit", price = 100 },
    [2] = { name = "Armor",  price = 250 },
}

local nextAllowed = {}               -- per-player cooldown
local COOLDOWN = 0.5

net.Receive( "myaddon_buy", function( len, ply )
    -- 1. Sender sanity and rate limit
    if not IsValid( ply ) then return end
    local now = CurTime()
    if ( nextAllowed[ ply ] or 0 ) > now then return end
    nextAllowed[ ply ] = now + COOLDOWN

    -- 2. Size check: one small UInt + one entity is only a few dozen bits,
    --    so anything much larger is junk
    if len > 64 then return end

    -- 3. Read with fixed sizes and validate types and ranges
    local itemId = net.ReadUInt( 8 )
    local item = ITEMS[ itemId ]
    if not item then return end

    -- 4. Validate entities: exist, right class, close to the player
    local npc = net.ReadEntity()
    if not IsValid( npc ) or npc:GetClass() ~= "myaddon_shop_npc" then return end
    if ply:GetPos():DistToSqr( npc:GetPos() ) > 150 * 150 then return end

    -- 5. Check state and permissions on the server
    if not ply:Alive() then return end
    -- e.g. money check with your own server-side data, never a client value

    -- 6. Act
    -- give the item, take the money, log it
end )

hook.Add( "PlayerDisconnected", "myaddon_net_cleanup", function( ply )
    nextAllowed[ ply ] = nil
end )
```

Client side only sends **what the player wants**, never the result:

```lua
-- lua/myaddon/cl_shop.lua
net.Start( "myaddon_buy" )
    net.WriteUInt( itemId, 8 )
    net.WriteEntity( shopNpc )
net.SendToServer()
```

## Validation checklist for every receiver

- Use the `ply` argument. Never read "who sent this" from the message (`net.ReadEntity()` as the player is forgeable).
- Prices, rewards, damage, cooldowns and permissions come from server tables, never from the client.
- Numbers: use `net.ReadUInt( bits )` with the smallest size that fits, then check min/max. Reject negatives, `NaN` and huge values for anything read with `ReadFloat`/`ReadDouble`/`ReadInt`.
- Strings: check `#str` against a maximum and expected characters before storing or printing them.
- Entities: `IsValid`, expected class, owner, and distance.
- Permissions: `ply:IsAdmin()` / `ply:IsSuperAdmin()` or your admin mod's API, checked on the server for every admin action.
- Avoid `net.ReadTable()` from clients. It accepts any size and any types, which makes it easy to abuse. Send fixed fields instead.
- Rate limit anything that touches the database, spawns entities, or sends messages to other players.
- Ignore messages instead of erroring. A Lua error in a receiver can be triggered on purpose to spam logs.

## Keep secrets server-side

- Files sent with `AddCSLuaFile` (and everything in `lua/autorun/` and `lua/autorun/client/`) are downloaded by every player and can be read.
- Database passwords, API keys, webhook URLs and anti-cheat logic belong in `lua/autorun/server/` or `sv_` files that are only `include`d on the server.
- Keep `sv_allowcslua 0` on public servers so players cannot run their own client Lua.

## Spotting backdoors in addons (auditing)

Leaked "free" copies of paid addons and random uploads often contain backdoors. When reviewing code, treat these as red flags that need a clear, legitimate explanation:

- `RunString`, `RunStringEx` or `CompileString` on anything from the network, `http.Fetch`, a file or a convar.
- `http.Fetch` / `http.Post` / `HTTP` to unknown URLs, especially if the response is executed or server info (IP, rcon, players) is sent out.
- Obfuscation: long `string.char( ... )` sequences, `\x` or decimal escapes, base64 strings passed to `util.Base64Decode`, `string.reverse` on code, or variables named like `_____`.
- Dynamic global lookups such as `_G[ someString ]` used to hide function names.
- Net receivers that call `RunConsoleCommand`, `game.ConsoleCommand`, `SetUserGroup` or change money without a permission check.
- Hard-coded SteamIDs that get admin, immunity or hidden commands.
- `debug.*` functions, `setfenv`, or overriding core functions such as `net.Receive`, `hook.Add` or `file.Read`.

A quick search across your addons folder (run from `garrysmod/`):

```bash
grep -rnE "RunString|CompileString|http\.Fetch|http\.Post|Base64Decode|string\.char|_G\[" addons/ --include=*.lua
```

Matches are not proof of a backdoor (many addons use `http.Fetch` legitimately), but each one should be read and understood. When in doubt, remove the addon and get it from the original author.

## Common mistakes

- Trusting a price, amount, target player or "isAdmin" flag sent by the client.
- Doing the permission check only on the client (hiding a button is not security).
- Forgetting `util.AddNetworkString`, or calling it inside a function every time.
- Reading values in a different order or bit size than they were written.
- No cooldown on expensive actions, letting one player lag the server.
- Putting server logic or secrets in shared/client files.
- Broadcasting large tables every tick instead of sending only changes.

## References

- https://wiki.facepunch.com/gmod/Net_Library_Usage
- https://wiki.facepunch.com/gmod/net.Receive
- https://wiki.facepunch.com/gmod/util.AddNetworkString
- https://wiki.facepunch.com/gmod/Networking_Usage
- https://wiki.facepunch.com/gmod/Steam_Workshop_Rules
