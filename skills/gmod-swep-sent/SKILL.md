---
name: gmod-swep-sent
description: Templates and field reference for Garry's Mod scripted weapons (SWEPs) and scripted entities (SENTs), using the three-file layout (shared.lua, init.lua, cl_init.lua) or a single file. Covers SWEP fields (Primary/Secondary, HoldType, ViewModel, WorldModel, Slot, Spawnable), weapon_base helpers (CanPrimaryAttack, ShootBullet, TakePrimaryAmmo), prediction, ENT fields, physics setup, Use, and NetworkVar. Use when making a new weapon or entity, converting a single file into the three-file layout, or fixing weapons that do not show in the spawn menu, shoot twice, have the wrong hold type, or entities that fall through the world.
---

# SWEPs and SENTs

## Where the files go

| Kind | Folder (class name = folder or file name) |
|---|---|
| Weapon | `lua/weapons/myaddon_pistol/` or `lua/weapons/myaddon_pistol.lua` |
| Entity | `lua/entities/myaddon_crate/` or `lua/entities/myaddon_crate.lua` |

Class names should be lowercase, unique and prefixed (`myaddon_`), because they are global.

Three-file layout (both kinds):

- `shared.lua` - fields and functions for both realms.
- `init.lua` - server. Sends the client files and includes shared.
- `cl_init.lua` - client. Includes shared, adds drawing code.

```lua
-- init.lua
AddCSLuaFile( "cl_init.lua" )
AddCSLuaFile( "shared.lua" )
include( "shared.lua" )

-- cl_init.lua
include( "shared.lua" )
```

Single-file layout: put `AddCSLuaFile()` at the top and wrap realm-only code in `if SERVER then` / `if CLIENT then`.

## SWEP template (single file, based on weapon_base)

```lua
-- lua/weapons/myaddon_pistol.lua
AddCSLuaFile()

SWEP.PrintName    = "My Pistol"
SWEP.Author       = "You"
SWEP.Category     = "My Addon"
SWEP.Spawnable    = true
SWEP.AdminOnly    = false
SWEP.Base         = "weapon_base"

SWEP.ViewModel    = "models/weapons/c_pistol.mdl"
SWEP.WorldModel   = "models/weapons/w_pistol.mdl"
SWEP.UseHands     = true      -- c_ models + UseHands = player's own hands
SWEP.ViewModelFOV = 62
SWEP.HoldType     = "pistol"

SWEP.Slot         = 1         -- 0-5, weapon selection column
SWEP.SlotPos      = 10

SWEP.Primary.ClipSize    = 12
SWEP.Primary.DefaultClip = 24
SWEP.Primary.Automatic   = false
SWEP.Primary.Ammo        = "Pistol"

SWEP.Secondary.ClipSize    = -1   -- -1 = no clip
SWEP.Secondary.DefaultClip = -1
SWEP.Secondary.Automatic   = false
SWEP.Secondary.Ammo        = "none"

function SWEP:Initialize()
    -- weapon_base hard-codes "pistol" here, so apply your HoldType yourself
    self:SetHoldType( self.HoldType )
end

function SWEP:PrimaryAttack()
    if not self:CanPrimaryAttack() then return end   -- plays empty sound + reloads

    self:EmitSound( "Weapon_Pistol.Single" )
    self:ShootBullet( 15, 1, 0.02 )   -- damage, bullets, spread (also plays effects)
    self:TakePrimaryAmmo( 1 )
    self:SetNextPrimaryFire( CurTime() + 0.25 )
end

function SWEP:SecondaryAttack()
    -- unused; override so weapon_base's shotgun blast does not run
end
```

Valid `HoldType` values on weapon_base: `pistol`, `revolver`, `duel`, `smg`, `ar2`, `shotgun`, `rpg`, `physgun`, `crossbow`, `camera`, `slam`, `normal`, `grenade`, `melee`, `melee2`, `knife`, `fist`, `passive`, `magic`.

### Prediction (why things happen twice)

In multiplayer, `PrimaryAttack` runs on the server **and** on the shooting client (prediction), sometimes several times per shot on the client. Sounds, `ShootBullet` and ammo use are designed for this. For things only the server should do once, guard them:

```lua
if CLIENT then return end            -- e.g. before ents.Create
-- or, for client-only effects:
if CLIENT and not IsFirstTimePredicted() then return end
```

In singleplayer, `PrimaryAttack` only runs on the server.

## SENT template (three files)

```lua
-- lua/entities/myaddon_crate/shared.lua
ENT.Type      = "anim"
ENT.Base      = "base_anim"
ENT.PrintName = "Supply Crate"
ENT.Author    = "You"
ENT.Category  = "My Addon"
ENT.Spawnable = true

function ENT:SetupDataTables()
    -- type, slot (0-31 per type), name -> creates GetUses/SetUses
    self:NetworkVar( "Int", 0, "Uses" )
end
```

```lua
-- lua/entities/myaddon_crate/init.lua
AddCSLuaFile( "cl_init.lua" )
AddCSLuaFile( "shared.lua" )
include( "shared.lua" )

function ENT:Initialize()
    self:SetModel( "models/items/item_item_crate.mdl" )
    self:PhysicsInit( SOLID_VPHYSICS )
    self:SetMoveType( MOVETYPE_VPHYSICS )
    self:SetSolid( SOLID_VPHYSICS )
    self:SetUseType( SIMPLE_USE )      -- Use fires once per key press

    local phys = self:GetPhysicsObject()
    if IsValid( phys ) then phys:Wake() end

    self:SetUses( 3 )
end

function ENT:Use( activator, caller )
    if not IsValid( activator ) or not activator:IsPlayer() then return end

    activator:SetHealth( math.min( activator:Health() + 25, activator:GetMaxHealth() ) )
    self:SetUses( self:GetUses() - 1 )
    if self:GetUses() <= 0 then self:Remove() end
end
```

```lua
-- lua/entities/myaddon_crate/cl_init.lua
include( "shared.lua" )

function ENT:Draw()
    self:DrawModel()
end
```

Spawning from code (server only):

```lua
local ent = ents.Create( "myaddon_crate" )
if not IsValid( ent ) then return end
ent:SetPos( ply:GetEyeTrace().HitPos + Vector( 0, 0, 10 ) )
ent:Spawn()
```

Useful `ENT.Type` values: `anim` (normal visible entity), `point` (invisible logic), `brush` (map triggers), `nextbot` (NPCs). Values in the ENT table are shared by every copy, so put per-entity state in `Initialize` or a `NetworkVar`.

## Common mistakes

- Missing `Spawnable = true` or `PrintName`, so it never shows in the spawn menu.
- Setting `SWEP.HoldType` but not calling `self:SetHoldType( self.HoldType )`: weapon_base forces `pistol`.
- Using a `v_` view model with `UseHands = true` (hands only work with `c_` models).
- Forgetting `SetNextPrimaryFire`, so the weapon fires every tick.
- Calling `ents.Create` or `ply:Give` on the client inside a predicted hook.
- Not overriding `SecondaryAttack` when you inherit from `weapon_base`.
- No `PhysicsInit` (entity floats or has no collisions), or calling `phys:Wake()` without checking `IsValid( phys )`.
- Leaving out `SetUseType( SIMPLE_USE )`, so `Use` fires every tick while E is held.
- Storing per-entity values directly on `ENT.` instead of on `self` or in a NetworkVar.
- Class name with capitals or spaces.

## References

- https://wiki.facepunch.com/gmod/Structures/SWEP
- https://wiki.facepunch.com/gmod/WEAPON_Hooks
- https://wiki.facepunch.com/gmod/Hold_Types
- https://wiki.facepunch.com/gmod/Structures/ENT
- https://wiki.facepunch.com/gmod/Scripted_Entities
- weapon_base source: https://github.com/Facepunch/garrysmod/tree/master/garrysmod/gamemodes/base/entities/weapons/weapon_base
