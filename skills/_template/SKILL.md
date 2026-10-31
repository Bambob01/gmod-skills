---
name: your-skill-name
description: One or two sentences on what this skill does, followed by when to use it. Start the second part with "Use when..." and list the situations, keywords and error messages someone might mention (for example "Use when writing a TTT2 role, adding a role icon, or fixing 'role not found' errors."). Max 1024 characters.
---

<!--
How to use this template:
1. Copy this whole folder to skills/<your-skill-name>/ (lowercase letters, numbers and hyphens only).
2. Set `name` above to exactly the folder name. It must not contain "claude" or "anthropic".
3. Write the description: WHAT it does + WHEN to use it. This is what the agent reads to decide
   whether to load your skill, so include the words people actually type.
4. Replace the sections below. Aim for 80-200 lines. Delete this comment block.
5. Run: python3 scripts/validate_skills.py
-->

# Skill title

One short paragraph: what problem this solves and the single most important rule.

## Background (optional)

Only what the reader needs to follow the steps. Link to the wiki for the rest.

## Step-by-step

1. First step, with the exact file path (for example `lua/autorun/server/myaddon.lua`).
2. Second step.
3. Third step.

```lua
-- A short, correct, tested example.
-- Use real function names from https://wiki.facepunch.com/gmod/ and note the realm.
hook.Add( "PlayerSpawn", "MyAddon_Example", function( ply )
    print( ply:Nick() .. " spawned" )
end )
```

## Reference table (optional)

| Field / function | Realm | What it does |
|---|---|---|
| `example_field` | Shared | Explain it in a few words |

## Common mistakes

- Mistake people often make, and how to fix it.
- Another one.

## References

- https://wiki.facepunch.com/gmod/ (link the exact pages you checked)
