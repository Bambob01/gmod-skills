---
name: darkrp-config
description: Configures the DarkRP gamemode for Garry's Mod the supported way, through the darkrpmodification addon. Covers installing DarkRP and darkrpmodification, adding jobs with DarkRP.createJob, shipments and single weapons with DarkRP.createShipment, buyable entities with DarkRP.createEntity, F4 menu categories with DarkRP.createCategory, disabling or replacing default jobs, VIP/admin-only jobs with customCheck, and settings.lua. Use when adding or editing DarkRP jobs, shipments, entities or categories, fixing DarkRP config errors (for example "Corrupt category", a job not appearing, or a duplicate command), or setting up a new DarkRP server.
---

# DarkRP configuration with darkrpmodification

**Never edit files inside `gamemodes/darkrp/`.** Updates overwrite them. All changes go in the separate **darkrpmodification** addon.

## Install

1. Get DarkRP: from GitHub (`https://github.com/FPtje/DarkRP`, into `garrysmod/gamemodes/darkrp/`) or from the Workshop (ID `248302805`) in your server's collection.
2. Download `https://github.com/FPtje/darkrpmodification` and put its contents in `garrysmod/addons/darkrpmodification/` (so the path is `addons/darkrpmodification/lua/darkrp_customthings/jobs.lua`).
3. Start the server with `+gamemode darkrp`.
4. Restart the server (or change map) after editing config files, then check the server console for red DarkRP errors.

Key files (all in `addons/darkrpmodification/lua/`):

| File | Purpose |
|---|---|
| `darkrp_config/settings.lua` | All `GM.Config.*` settings (salary, starting money, toggles) |
| `darkrp_config/disabled_defaults.lua` | Turn off default jobs, shipments, entities, modules |
| `darkrp_customthings/jobs.lua` | Your jobs |
| `darkrp_customthings/shipments.lua` | Shipments and single weapons |
| `darkrp_customthings/entities.lua` | Buyable entities (printers, labs...) |
| `darkrp_customthings/categories.lua` | F4 menu categories |

These files load on **both server and client**, so a syntax error breaks the F4 menu too.

## Jobs

```lua
-- darkrp_customthings/jobs.lua
TEAM_MECHANIC = DarkRP.createJob( "Mechanic", {
    color = Color( 200, 120, 20, 255 ),
    model = { "models/player/Group02/male_02.mdl", "models/player/Group02/male_04.mdl" },
    description = [[Repair vehicles and sell parts.]],
    weapons = { "weapon_crowbar" },
    command = "mechanic",        -- players type /mechanic; must be unique
    max = 2,                     -- 0 = unlimited, 0.25 = 25% of players
    salary = 60,
    admin = 0,                   -- 0 = everyone, 1 = admin+, 2 = superadmin
    vote = false,
    hasLicense = false,
    candemote = true,
    category = "Citizens",       -- must match an existing jobs category
} )
```

- The `TEAM_` variable name must be unique and is used elsewhere (shipment `allowed`, door groups, `GAMEMODE.CivilProtection`).
- Required fields: `color`, `model`, `description`, `command`, `max`, `salary`. `weapons`, `ammo`, `category`, `customCheck` and others are optional.
- Use only models that exist on the server **and** on clients (add custom models to your Workshop collection).

### VIP / restricted job

```lua
TEAM_VIPGUARD = DarkRP.createJob( "VIP Guard", {
    -- ...same fields as above...
    command = "vipguard",
    customCheck = function( ply )
        return ply:GetUserGroup() == "vip" or ply:IsAdmin()
    end,
    CustomCheckFailMsg = "This job is for VIPs only.",
} )
```

`customCheck` runs on both server and client; return `true` to allow. The group name must match your admin mod's group exactly (case-sensitive).

### Default team and police

At the bottom of `jobs.lua` the file already sets `GAMEMODE.DefaultTeam = TEAM_CITIZEN` and `GAMEMODE.CivilProtection = { ... }`. If you disable or rename those jobs, update these lines or DarkRP errors on spawn.

## Editing a default job

1. In `darkrp_config/disabled_defaults.lua`, set the job to `true` in `DarkRP.disabledDefaults["jobs"]` (for example `["medic"] = true`).
2. Copy the original from DarkRP's `gamemode/config/jobrelated.lua` into your `jobs.lua`.
3. Edit the copy. Keep the same `TEAM_` name if other things depend on it.

## Shipments and single weapons

```lua
-- darkrp_customthings/shipments.lua
DarkRP.createShipment( "Crowbar", {
    model = "models/weapons/w_crowbar.mdl",
    entity = "weapon_crowbar",   -- weapon class name
    price = 1500,                -- price of the whole shipment
    amount = 10,                 -- weapons in the shipment
    separate = true,             -- also sell one at a time
    pricesep = 200,              -- price of a single weapon
    noship = false,              -- true = only sold separately
    allowed = { TEAM_GUN },      -- jobs that can buy it
    category = "Other",          -- a "shipments" category
} )
```

## Entities

```lua
-- darkrp_customthings/entities.lua
DarkRP.createEntity( "Toolbox", {
    ent = "myaddon_toolbox",     -- entity class name
    model = "models/props_c17/tools_wrench01a.mdl",
    price = 500,
    max = 2,                     -- per player
    cmd = "buytoolbox",          -- /buytoolbox; must be unique
    allowed = { TEAM_MECHANIC },
    category = "Other",
} )
```

## Categories

```lua
-- darkrp_customthings/categories.lua
DarkRP.createCategory{
    name = "Mechanics",
    categorises = "jobs",        -- "jobs", "entities", "shipments", "weapons", "vehicles" or "ammo"
    startExpanded = true,
    color = Color( 200, 120, 20, 255 ),
    canSee = function( ply ) return true end,
    sortOrder = 100,             -- lower = higher in the F4 menu
}
```

DarkRP ships default categories: jobs `Citizens`, `Civil Protection`, `Gangsters`, `Other`; shipments `Pistols`, `Rifles`, `Shotguns`, `Snipers`, `Other`; entities `Other`. Creating a `shipments` category also creates the matching `weapons` category.

## Settings

Edit values in `darkrp_config/settings.lua`, for example:

```lua
GM.Config.normalsalary  = 45
GM.Config.startingmoney = 500
GM.Config.paydelay      = 160
```

If a setting is missing from the file, DarkRP uses its default.

## Common mistakes

- Editing `gamemodes/darkrp/` directly (lost on update).
- `category` naming a category that does not exist, or the wrong `categorises` type (a job in an `entities` category).
- Two jobs with the same `command`, or two entities with the same `cmd`.
- A missing comma between fields, or a missing `} )` at the end of a block, breaks the whole file. Read the first DarkRP error in the console; it names the file and line.
- Using `TEAM_X` in shipments or `allowed` before the job is created, or after disabling it.
- Editing a default job without disabling it first, so it appears twice.
- Models or weapons that only exist on your PC, not on the server and clients.
- `customCheck` that errors (for example calling a function your admin mod does not provide).

## References

- https://github.com/FPtje/darkrpmodification
- https://github.com/FPtje/DarkRP/blob/master/gamemode/config/jobrelated.lua
- https://github.com/FPtje/DarkRP/blob/master/gamemode/config/addentities.lua
- https://darkrp.miraheze.org/wiki/DarkRP:CustomJobFields
- https://darkrp.miraheze.org/wiki/DarkRP:CustomShipmentFields
- https://darkrp.miraheze.org/wiki/DarkRP:CustomEntityFields
- https://darkrp.miraheze.org/wiki/DarkRP:Categories
