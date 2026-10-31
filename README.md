# gmod-skills

[![Validate skills](https://github.com/Bambob01/gmod-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/Bambob01/gmod-skills/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A community collection of **Agent Skills** for **Garry's Mod**: addon development in GLua, Derma UI, scripted weapons and entities, DarkRP configuration, and running a dedicated server.

Drop a skill into your AI coding agent and it follows GMod's real conventions (realms, `AddCSLuaFile`, net security, Workshop publishing) instead of guessing.

> Community-made. Not affiliated with or endorsed by Facepunch Studios, Valve or Anthropic.

## What are Agent Skills?

An Agent Skill is a folder with a `SKILL.md` file: a short YAML header (`name` and `description`) followed by Markdown instructions. The agent reads the description, and when your request matches, it loads the instructions (and any extra files in the folder) and follows them.

The format is open and is supported by Claude (Claude Code, the Claude apps and the API) and a growing number of other agents. Skills are plain text, so you can read every one before using it.

## Skills

| Skill | What it helps with |
|---|---|
| [glua-realms-hooks](skills/glua-realms-hooks/SKILL.md) | Server/client/shared realms, `AddCSLuaFile` + `include` loaders, `hook.Add`/`hook.Run`, avoiding realm errors. |
| [gmod-net-security](skills/gmod-net-security/SKILL.md) | Safe net messages: server-side validation, rate limiting, never trusting the client, spotting backdoors (defensive). |
| [gmod-addon-structure](skills/gmod-addon-structure/SKILL.md) | Addon folder layout, `addon.json`, content paths, publishing and updating with gmad and gmpublish. |
| [gmod-swep-sent](skills/gmod-swep-sent/SKILL.md) | Scripted weapon and entity templates (`shared.lua`/`init.lua`/`cl_init.lua`), fields, prediction. |
| [derma-ui](skills/derma-ui/SKILL.md) | VGUI/Derma menus, `DFrame`, docking, custom `Paint`, `ScrW`/`ScrH` scaling, `surface.CreateFont`. |
| [darkrp-config](skills/darkrp-config/SKILL.md) | DarkRP jobs, shipments, entities and categories using darkrpmodification. |
| [glua-error-debugger](skills/glua-error-debugger/SKILL.md) | Reading console errors and stack traces, common Lua errors and how to fix them. |
| [gmod-server-setup](skills/gmod-server-setup/SKILL.md) | SteamCMD install, launch options, `server.cfg`, Workshop collections, GSLT, ULX admin setup. |

## Install

### Claude Code

Copy a skill folder (the folder itself, not just `SKILL.md`) into one of:

- `~/.claude/skills/` - available in all your projects
- `.claude/skills/` inside a project - only for that project (and anyone who clones it)

```bash
git clone https://github.com/Bambob01/gmod-skills.git
mkdir -p ~/.claude/skills
cp -r gmod-skills/skills/glua-realms-hooks ~/.claude/skills/

# or install all of them (skips the template)
for d in gmod-skills/skills/*/; do
  [ "$(basename "$d")" = "_template" ] || cp -r "$d" ~/.claude/skills/
done
```

Start a new Claude Code session and the skills are picked up automatically.

### Claude apps (claude.ai / desktop)

1. Zip a skill folder so the zip contains the folder, e.g. `derma-ui.zip` containing `derma-ui/SKILL.md`. The folder name must match the skill `name`.
2. Make sure code execution is on (Settings > Capabilities; on some plans an admin has to allow skills).
3. Open the Skills page (currently **Customize > Skills**; older docs say Settings > Capabilities or Settings > Features), click **+**, choose to create a skill, then **Upload a skill** and pick the zip.
4. Toggle the skill on.

Menu names change from time to time. If these steps do not match what you see, check Anthropic's help article "Use Skills in Claude".

### Other agents

Any agent that supports the open Agent Skills format can use these folders as they are. Check your agent's docs for where it looks for skills.

## Skills wanted

These would be great additions. Pick one, open an issue saying you are on it, and send a PR:

- `ttt2-roles` - creating roles for TTT2
- `helix-schema` - building a Helix schema (factions, classes, items)
- `wiremod-e2` - Expression 2 chips for Wiremod
- `pac3-outfits` - PAC3 outfits and parts
- `starfall-scripting` - Starfall processors and screens
- `gmod-performance-profiling` - finding lag: hooks, timers, net usage, profilers
- `sandbox-gamemode-derivation` - making a gamemode derived from Sandbox
- `gmod-workshop-publishing` - Workshop pages, updates, collections in depth
- `gmod-database` - `sql` (SQLite) and MySQL modules, safe queries
- `gmod-stool` - toolgun tools (STOOLs)
- `gmod-nextbot` - NextBot NPCs and pathing
- `ttt-classic-weapons` - weapons and equipment for the original TTT

Have another idea? [Request a skill](https://github.com/Bambob01/gmod-skills/issues/new?template=skill-request.yml).

## Contributing

Contributions are very welcome, from fixing a typo to adding a whole new skill. You do not need to be an expert: if you know one corner of GMod well, that is enough.

- Read the [contributing guide](CONTRIBUTING.md) (adding a skill takes about five steps).
- Found something wrong in a skill? [Report incorrect content](https://github.com/Bambob01/gmod-skills/issues/new?template=bug-report.yml).
- Accuracy matters more than length. Check APIs against the [Garry's Mod wiki](https://wiki.facepunch.com/gmod/).
- No exploits, cheats, backdoors or leaked paid code. Ever.

## License

[MIT](LICENSE). Garry's Mod is a trademark of Facepunch Studios. DarkRP, ULX and other projects mentioned belong to their respective authors.
