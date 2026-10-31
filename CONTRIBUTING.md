# Contributing to gmod-skills

Thanks for helping! Every skill here was written to be **correct first**. People will copy these examples straight into their servers, so a small accurate skill beats a long one with guesses in it.

You can contribute without writing a new skill:

- Fix a mistake or an outdated API in an existing skill.
- Add a missing "Common mistakes" item you have hit yourself.
- Test a skill with your agent and report what went wrong.
- Pick something from the "Skills wanted" list in the README.

## Add a new skill in 5 steps

1. **Check it is not already covered.** Look in `skills/` and open issues. If you are starting something big, open a [skill request](https://github.com/Bambob01/gmod-skills/issues/new?template=skill-request.yml) issue first so nobody duplicates work.

2. **Copy the template.**

   ```bash
   cp -r skills/_template skills/your-skill-name
   ```

   The folder name is the skill name: lowercase letters, numbers and hyphens only (for example `ttt2-roles`).

3. **Fill in the frontmatter** at the top of `SKILL.md`:

   ```yaml
   ---
   name: your-skill-name
   description: What it does, then "Use when..." and the situations or error messages that should trigger it.
   ---
   ```

   - `name`: exactly the folder name, max 64 characters, must not contain `claude` or `anthropic`.
   - `description`: max 1024 characters. Say **what** it does and **when** to use it. This is the only part the agent reads before deciding to load your skill, so include the words people actually type.

4. **Write the instructions** below the frontmatter. Aim for 80 to 200 lines with:
   - a one-paragraph intro and the most important rule,
   - step-by-step guidance with real file paths,
   - short, correct code examples (mark the realm: server, client or shared),
   - a **Common mistakes** section,
   - a **References** list linking the wiki pages you checked.

   Longer reference material can go in extra `.md` files in the same folder (for example `skills/your-skill-name/REFERENCE.md`); link to them from `SKILL.md`.

5. **Validate and open a pull request.**

   ```bash
   pip install pyyaml
   python3 scripts/validate_skills.py
   ```

   Add your skill to the table in `README.md` (and remove it from "Skills wanted" if it was there), then open a PR. The same check runs automatically on every PR.

## Quality checklist

Before you open the PR, make sure:

- [ ] Every function, hook, field and console command exists and is spelled exactly as on the [Garry's Mod wiki](https://wiki.facepunch.com/gmod/) (or the project's official docs/source for DarkRP, TTT2, Helix, Wiremod, etc.).
- [ ] Realms are right: server-only code is never shown in client files, and vice versa.
- [ ] Code examples were run in game where possible (say in the PR if you could not test something).
- [ ] Examples validate client input on the server and do not teach unsafe patterns.
- [ ] The description says what the skill does **and** when to use it.
- [ ] There is a "Common mistakes" section.
- [ ] Wording is plain and beginner-friendly. Explain jargon the first time.
- [ ] The validator passes.

## Rules

1. **Accuracy.** Do not invent APIs. If you are not sure something is right, check the wiki or source, or leave it out and mention it in the PR.
2. **Tested where possible.** Tell reviewers what you tested and how (singleplayer, listen server, dedicated server).
3. **No exploits, cheats, backdoors or anti-anticheat content.** Security skills must be defensive: how to protect a server or audit an addon, never how to attack one.
4. **No leaked or paid code.** Do not paste code from paid addons (gmodstore etc.) or from leaks. Write your own examples. Respect the licences of open-source projects you reference.
5. **No copyrighted wiki dumps.** Summarise in your own words and link the source.
6. **One skill per PR** where possible, so reviews stay quick.
7. Be kind. See the [Code of Conduct](CODE_OF_CONDUCT.md).

## Fixing an existing skill

Small fixes are welcome without an issue. In the PR, link the wiki page or source that shows the correct behaviour so the reviewer can check it quickly.

## Questions

Open an issue or start a discussion. There are no silly questions.
