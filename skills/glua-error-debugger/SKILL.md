---
name: glua-error-debugger
description: Reads and fixes Garry's Mod Lua errors. Explains the error line and stack trace format, how to tell client errors from server errors, and the usual cause and fix for the common messages - attempt to index a nil value, attempt to call a nil value, attempt to perform arithmetic or concatenate on nil, bad argument, Tried to use a NULL entity, Couldn't include file, unexpected symbol, 'end' expected, stack overflow. Includes realm mistakes and debugging tools (print, PrintTable, lua_run, developer). Use whenever someone pastes a GMod console error, a script or addon "does not work", or a server or client throws red/yellow/blue Lua errors.
---

# Debugging GLua errors

## Step-by-step

1. **Find the first error.** Later errors are often side effects of the first one. Scroll up in the console.
2. **Read the error line.** It has three parts: the file path, the line number, and the message.

```
[ERROR] addons/myaddon/lua/autorun/server/sv_shop.lua:12: attempt to index local 'ply' (a nil value)
  1. buy - addons/myaddon/lua/autorun/server/sv_shop.lua:12
   2. func - addons/myaddon/lua/autorun/server/sv_shop.lua:30
    3. unknown - lua/includes/extensions/net.lua:NN
```

   - `addons/myaddon/...sv_shop.lua` tells you **which addon and file**.
   - `:12` is the **line**.
   - `local 'ply'` is the **name of the thing that was nil**.
3. **Read the stack trace** (the numbered lines). Line 1 is where it broke; the lines below show who called it. Walk down until you reach code you own. Frames in `lua/includes/...` are GMod's own code calling your function.
4. **Know the realm.** In the in-game console, server errors are blue and client errors are yellow (menu errors are green). On a dedicated server console, everything shown there is server-side. A file path containing `/server/`, `sv_` or `init.lua` is usually server; `/client/`, `cl_` or `cl_init.lua` is client.
5. **Fix the cause, not just the symptom**, then reproduce what triggered it to confirm.

## Common errors

| Message | Usual cause | Fix |
|---|---|---|
| `attempt to index local/global/field 'x' (a nil value)` | `x` does not exist: misspelled, not loaded yet, wrong realm, or a function returned nothing | Check spelling; make sure the file defining it loads first; check the realm; guard with `if not x then return end` |
| `attempt to call global/field/method 'Foo' (a nil value)` | Function does not exist **in this realm** or is misspelled (Lua is case-sensitive: `GetPos` not `getPos`) | Check the wiki realm badge; use `:` for methods (`ply:Nick()`), `.` for library functions (`util.TraceLine()`) |
| `attempt to perform arithmetic on ... (a nil value)` | Using `+ - * /` on a missing value, often an unset variable or failed `tonumber` | Default it: `local n = tonumber( str ) or 0` |
| `attempt to concatenate ... (a nil value)` | `..` with a nil | `tostring( x )` or check first |
| `attempt to compare number with nil` | `<` / `>` with a nil | Make sure both sides are numbers |
| `bad argument #1 to 'pairs' (table expected, got nil)` | Looping over a table that does not exist | `for k, v in pairs( tbl or {} ) do` or create it first |
| `Tried to use a NULL entity!` | Entity was removed, never existed, or a player left | Check `IsValid( ent )` before using it, especially in timers and hooks |
| `Couldn't include file 'x' - File not found` | Wrong path, empty file, file created while server running, or a client file not sent with `AddCSLuaFile` | Fix the path; add `AddCSLuaFile` on the server; restart |
| `unexpected symbol near 'x'` | Syntax: missing `then`/`do`, unclosed `(` or `{`, missing comma in a table | Look at the line given **and the line above** |
| `'end' expected (to close 'function' at line N) near '<eof>'` | A block is never closed | Count `function`/`if`/`for`/`while` against `end` from line N |
| `'=' expected near 'x'` | Often a typo in a keyword, or `==` where `=` was meant | Read the line carefully |
| `stack overflow` | A function calls itself forever, or two hooks call each other | Add a stop condition; do not call `hook.Run` for the hook you are inside |
| `Infinite loop detected` (or the game freezes) | A loop that never ends | Make sure the loop condition changes; never `while true do` without a `break` |

## Realm mistakes (very common)

| Error appears | Typical cause |
|---|---|
| Server: `attempt to call global 'LocalPlayer' (a nil value)` | Client-only function in a server/shared file |
| Server: `attempt to index global 'vgui'`/`'surface'`/`'draw' (a nil value)` | UI code running on the server |
| Client: `attempt to call field 'AddNetworkString' (a nil value)` | `util.AddNetworkString` is server-only |
| Client: `attempt to call field 'Create' (a nil value)` on `ents.Create` | Entities are created on the server |
| Client: `attempt to call method 'Give' (a nil value)` | `ply:Give` is server-only |

Fix by moving the code to the right file, or wrapping it in `if SERVER then ... end` / `if CLIENT then ... end`. See the `glua-realms-hooks` skill.

## Debugging tools

- `print( x )` and `PrintTable( tbl )` to see values. `MsgN( "here 1" )` to see how far the code gets.
- `lua_run <code>` in the **server** console runs server Lua, for example `lua_run PrintTable( player.GetAll() )`.
- `lua_run_cl <code>` runs client Lua (only allowed if the server has `sv_allowcslua 1`; keep it `0` on public servers).
- `developer 1` shows extra engine warnings (missing models, net messages).
- `debug.Trace()` prints the current call stack without erroring.
- `ErrorNoHaltWithStack( "message" )` reports a problem with a stack trace but keeps running.
- Lua auto-refresh: saving a file reloads it on a running server. Hooks with fixed identifiers replace themselves; anything created at load time (timers with random names, panels) may duplicate.

## GLua syntax notes

GMod's Lua accepts extra C-style syntax: `!=`, `!`, `&&`, `||`, `//` and `/* */` comments, and `continue`. Plain Lua tools may flag these as errors even though GMod runs them. Use a GLua-aware linter such as glualint.

## When asking for help, include

- The full first error and its stack trace (copy text, not a photo).
- The file it points to, with the line numbers.
- Whether it happened on server or client, and what you did to trigger it.

## Common mistakes

- Fixing the last error in the console instead of the first.
- Hiding errors with `pcall` instead of fixing the nil value.
- Not checking `IsValid` in timers, where the player or entity may be gone.
- Assuming "it works in singleplayer" means the realms are right. Test on a dedicated server.
- Editing a file in the wrong copy of the addon (Workshop vs `addons/` folder).

## References

- https://wiki.facepunch.com/gmod/Lua_Error_Explanation
- https://wiki.facepunch.com/gmod/null
- https://wiki.facepunch.com/gmod/States
