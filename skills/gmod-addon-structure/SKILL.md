---
name: gmod-addon-structure
description: Shows how a Garry's Mod addon folder is laid out (addon.json, lua/autorun, lua/entities, lua/weapons, materials, models, sound, maps, gamemodes), how to name files so they do not collide with other addons, how clients get custom content, and how to pack and publish to the Steam Workshop with gmad and gmpublish. Use when creating a new addon from scratch, fixing an addon that does not load or shows missing textures (purple/black checkers) or ERROR models, writing addon.json, or uploading or updating a Workshop item.
---

# GMod addon structure and publishing

## Folder layout

Each addon is one folder in `garrysmod/addons/`. Only create the folders you need.

```
garrysmod/addons/myaddon/
├── addon.json              -- needed to pack/publish with gmad
├── lua/
│   ├── autorun/            -- runs on server + client at startup
│   │   ├── server/         -- runs on server only
│   │   └── client/         -- runs on client only
│   ├── myaddon/            -- your own files, loaded by an autorun file
│   ├── entities/           -- scripted entities (SENTs)
│   ├── weapons/            -- scripted weapons (SWEPs)
│   ├── effects/            -- Lua effects
│   ├── vgui/               -- Derma panels
│   └── weapons/gmod_tool/stools/  -- toolgun tools
├── materials/              -- .vmt / .vtf / .png
├── models/                 -- .mdl + .vvd + .vtx + .phy
├── sound/                  -- .wav / .mp3 / .ogg
├── maps/                   -- .bsp (and .nav)
├── resource/               -- fonts, localization
└── gamemodes/<name>/       -- only for gamemode addons
```

Rules that save hours:

- Use lowercase folder and file names with no spaces. Linux servers are case-sensitive, so `Materials/MyThing.vmt` works on Windows and breaks on Linux.
- All addons are merged into one virtual filesystem. Two addons with `lua/autorun/init.lua` or `materials/logo.png` overwrite each other. Prefix everything: `lua/autorun/myaddon_load.lua`, `materials/myaddon/logo.png`.
- Paths in code are relative to the content root and do not include the addon folder: `Material( "myaddon/logo.png" )`, `Model( "models/myaddon/crate.mdl" )`, `"myaddon/beep.wav"` for sounds.
- An addon must keep the game's folder names exactly (`materials`, not `textures`; `sound`, not `sounds`).

## addon.json

```json
{
    "title": "My Addon",
    "type": "tool",
    "tags": [ "fun", "build" ],
    "ignore": [
        "*.psd",
        "*.git*",
        "README.md"
    ]
}
```

- `type` must be one of: `ServerContent`, `gamemode`, `map`, `weapon`, `vehicle`, `npc`, `tool`, `effects`, `model`, `entity`.
- `tags`: up to two of `fun`, `roleplay`, `scenic`, `movie`, `realism`, `cartoon`, `water`, `comic`, `build`.
- `ignore`: wildcard list of files left out of the `.gma`.
- Make sure it is valid JSON (no trailing commas, double quotes only).

## Getting content to players

- Lua files are sent by the Lua system (`AddCSLuaFile`, see the `glua-realms-hooks` skill). They are not "content".
- Models, materials and sounds must be downloaded by clients separately. The usual way is the Workshop: on the server, `resource.AddWorkshop( "WORKSHOP_ID" )` forces joining players to download that item.
- `resource.AddWorkshop` takes a single item ID, not a collection, and does not install the addon on the server. Only add items that contain real content; Lua-only items do nothing there.
- Maps and gamemodes in the server's Workshop collection are added for download automatically.

## Packing and publishing

Tools live in `steamapps/common/GarrysMod/bin/` (`gmad.exe`, `gmpublish.exe` on Windows). Steam must be running and logged in for publishing.

1. Create the `.gma`:

```bat
gmad.exe create -folder "C:\path\to\garrysmod\addons\myaddon" -out "C:\path\to\myaddon.gma"
```

   gmad refuses files that are not on its whitelist (for example `.exe`, `.dll`, `.bat`, `.html`, `.js`, most `.txt`). Remove them or add them to `ignore`.

2. Make the icon: **512x512, baseline JPEG** (not progressive, not PNG), 4:2:0 chroma. If gmpublish rejects it, re-save it in MS Paint or Paint.NET.

3. First upload (prints the new Workshop ID):

```bat
gmpublish.exe create -addon "C:\path\to\myaddon.gma" -icon "C:\path\to\myaddon.jpg"
```

4. Updates reuse the ID from the item's URL (`...filedetails/?id=123456789`):

```bat
gmpublish.exe update -addon "C:\path\to\myaddon.gma" -id "123456789" -changes "Fixed a bug"
```

5. Open the Workshop page, set visibility, write a description, and add screenshots.

Never upload a second item to "update" an addon, and never reupload other people's work. Follow the Workshop rules (no malicious code, no ads, no retail game content, accurate tags).

## Testing before you publish

1. Put the folder in `garrysmod/addons/` and start a local game (Lua errors show in the console).
2. Test on a dedicated server too: client/server realm bugs hide in singleplayer.
3. Join with `developer 1` and check for missing models/materials.
4. Pack with gmad and test the `.gma` by moving the loose folder out first.

## Common mistakes

- Purple/black checkerboard textures or big red ERROR models: wrong path, wrong case, or clients never downloaded the content (missing `resource.AddWorkshop`).
- Addon folder nested twice (`addons/myaddon/myaddon/lua/...`), so nothing loads.
- Lua files outside `lua/` (for example `addons/myaddon/autorun/`) are ignored.
- Generic filenames that clash with other addons.
- Invalid `addon.json` (comments, trailing commas, a `type` or tag not in the lists above).
- Progressive JPEG or PNG icon making gmpublish fail.
- Publishing a new item for every update instead of `gmpublish update`.

## References

- https://wiki.facepunch.com/gmod/Lua_Folder_Structure
- https://wiki.facepunch.com/gmod/Workshop_Addon_Creation
- https://wiki.facepunch.com/gmod/Workshop_Addon_Updating
- https://wiki.facepunch.com/gmod/resource.AddWorkshop
- https://wiki.facepunch.com/gmod/Steam_Workshop_Rules
