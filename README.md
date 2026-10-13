# Hermes Agent Layer

**Run a second agent on the same vault without a second copy of anything: same rules, same skills, same memory, same privacy guard.**

Agent runtimes keep their state in their own home folder: skills in one place, memory in
another, hooks in a third. Add a second runtime and you have two copies of everything, and they
drift. This repo connects [Hermes](https://github.com/NousResearch/hermes-agent) to an agentic
vault so the vault stays the only source. Hermes holds pointers, and the files live in the vault.

Part of [Digital Brain](https://github.com/OferBlum/personal-digital-brain-with-ai).

## The idea

- **The vault owns the state; the runtime holds pointers.** Swapping Hermes for another agent
  then means pointing it at the same files, not moving them.
- **One skill folder for every runtime.** Skills are [agentskills.io](https://agentskills.io)
  `SKILL.md` folders in `.claude/skills/`. Claude Code reads them there, and Hermes loads the same
  folder live through `skills.external_dirs`. No sync script, no second copy.
- **Memory in the vault.** Hermes' memory path is hardcoded, so `~/.hermes/memories` becomes a
  symlink into `0 - System/memories/`. Plain markdown, versionable, readable by the next agent.
- **The same privacy guard, failing closed.** Hermes runs unattended, which is exactly when a
  guard that "fails open so it never gets stuck" lets everything through. The wrapper blocks
  every call when it can't load the policy, and `fail_closed: true` makes Hermes block when the
  hook crashes or times out.

## How it works

| What | Lives in the vault | How Hermes finds it |
|------|--------------------|---------------------|
| Rules | `AGENTS.md` | read at the vault root, like every agent |
| Skills | `.claude/skills/<name>/SKILL.md` | `skills.external_dirs` in `~/.hermes/config.yaml` |
| Memory | `0 - System/memories/USER.md`, `MEMORY.md` | `~/.hermes/memories` is a symlink to it |
| Sub-agent roles | `0 - System/agents/<name>.md` | the role binding points at the skill |
| Privacy | `0 - System/scripts/privacy_guard.py` | `hooks.pre_tool_call` runs the wrapper, which loads it |

The role binding pattern: one file per role in `0 - System/agents/` says which skill to load and
adds no rules of its own. Each runtime keeps a thin pointer to it (in Claude Code,
`.claude/agents/<name>.md`), so the procedure is written once.

The wrapper is a translator, not a policy. Hermes sends the tool call as JSON on stdin; the
wrapper hands it to the vault's `privacy_guard.py` (`--mode hermes` contract) and prints
`{"decision": "block", ...}` or `{}`.

Rule of thumb: **Hermes for anything under a minute** (quick questions, "jot this down" into
`2 - Notes/`), **Claude Code for anything that changes the vault.**

## Files

```text
hermes-home/                       # goes to ~/.hermes
  agent-hooks/privacy-guard.py     # Hermes adapter for the vault's guard; fails closed
  config.example.yaml              # skills.external_dirs, hooks.pre_tool_call, memory
0 - System/                        # goes into the vault
  memories/README.md               # the symlink setup and the memory format
  memories/USER.md, MEMORY.md      # templates (entries separated by a line holding only §)
  agents/wiki-librarian.md         # example role binding
tests/test_hermes_layer.py         # wrapper fails closed; templates parse as Hermes entries
```

The guard itself comes from [vault-privacy-guard](https://github.com/OferBlum/vault-privacy-guard),
and the librarian skill from
[llm-wiki-youtube-transcript](https://github.com/OferBlum/llm-wiki-youtube-transcript). The
vault layout is [agentic-vault-skeleton](https://github.com/OferBlum/agentic-vault-skeleton).

## Quickstart

1. Copy `0 - System/` into your vault, and `hermes-home/agent-hooks/privacy-guard.py` to
   `~/.hermes/agent-hooks/`. Install the guard from vault-privacy-guard if you haven't.
2. Merge `hermes-home/config.example.yaml` into `~/.hermes/config.yaml`, using absolute paths,
   then run the symlink commands in `0 - System/memories/README.md`.
3. Start `hermes chat` from the vault, approve the hook when asked, and ask it to read a file in
   the private folder. The call is blocked.

Tests: `python3 -m unittest discover -s tests` (Python 3.8+, standard library only).

## License

MIT, see [LICENSE](LICENSE).
