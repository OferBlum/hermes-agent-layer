# Hermes Agent Layer

**Run Hermes on my vault without a second copy of anything — same rules, same skills, same memory,
same privacy guard.**

Part of [Digital Brain](https://github.com/OferBlum/personal-digital-brain-with-ai).

## Why Hermes

I use [Hermes](https://github.com/NousResearch/hermes-agent) because it trains and improves
itself. The more I use it, the more skills and memory it builds, and the smarter it gets.

## The problem

Every agent keeps its own stuff in its own home folder: skills in one place, memory in another,
hooks in a third. Add a second agent and you have two copies of everything, and they drift apart.

My fix: **the vault is the only source.** Hermes only holds pointers, and the files stay in the
vault.

## The idea

- **The vault owns everything, the agent only points to it.** To swap Hermes for another agent,
  I point the new one at the same files. Nothing moves.
- **One skill folder for every agent.** Skills are [agentskills.io](https://agentskills.io)
  `SKILL.md` folders in `.claude/skills/`. Claude Code reads them there, and Hermes loads the same
  folder through `skills.external_dirs`. No sync script, no second copy.
- **Memory in the vault.** Hermes' memory path is hardcoded, so `~/.hermes/memories` becomes a
  symlink into `0 - System/memories/`. Plain markdown that the next agent can read too.
- **The same privacy guard, and it fails closed.** Hermes runs on its own, without me watching.
  That's exactly when a guard that "lets things through so it never gets stuck" is dangerous. So
  if the guard can't load its policy, it blocks every call, and `fail_closed: true` makes Hermes
  block if the hook crashes or times out.

## How it works

| What | Lives in the vault | How Hermes finds it |
|------|--------------------|---------------------|
| Rules | `AGENTS.md` | read at the vault root, like every agent |
| Skills | `.claude/skills/<name>/SKILL.md` | `skills.external_dirs` in `~/.hermes/config.yaml` |
| Memory | `0 - System/memories/USER.md`, `MEMORY.md` | `~/.hermes/memories` is a symlink to it |
| Sub-agent roles | `0 - System/agents/<name>.md` | the role file points to the skill |
| Privacy | `0 - System/scripts/privacy_guard.py` | `hooks.pre_tool_call` runs the wrapper, which loads it |

**Roles:** one file per role in `0 - System/agents/` says which skill to load, and adds no rules
of its own. Each agent keeps a small pointer to it (in Claude Code, `.claude/agents/<name>.md`),
so the procedure is written only once.

**The wrapper only translates.** Hermes sends the tool call as JSON on stdin. The wrapper hands it
to the vault's `privacy_guard.py` (`--mode hermes`) and prints `{"decision": "block", ...}` or `{}`.

## Files

```text
hermes-home/                       # goes to ~/.hermes
  agent-hooks/privacy-guard.py     # Hermes adapter for the vault's guard; fails closed
  config.example.yaml              # skills.external_dirs, hooks.pre_tool_call, memory
0 - System/                        # goes into the vault
  memories/README.md               # the symlink setup and the memory format
  memories/USER.md, MEMORY.md      # templates (entries separated by a line holding only §)
  agents/wiki-librarian.md         # example role file
tests/test_hermes_layer.py         # wrapper fails closed; templates parse as Hermes entries
```

The guard itself comes from [vault-privacy-guard](https://github.com/OferBlum/vault-privacy-guard),
the librarian skill from
[llm-wiki-youtube-transcript](https://github.com/OferBlum/llm-wiki-youtube-transcript), and the
vault layout from [agentic-vault-skeleton](https://github.com/OferBlum/agentic-vault-skeleton).

## Quickstart

1. Copy `0 - System/` into your vault, and `hermes-home/agent-hooks/privacy-guard.py` to
   `~/.hermes/agent-hooks/`. Install the guard from vault-privacy-guard if you haven't yet.
2. Merge `hermes-home/config.example.yaml` into `~/.hermes/config.yaml` with absolute paths, then
   run the symlink commands in `0 - System/memories/README.md`.
3. Start `hermes chat` from the vault, approve the hook when asked, and ask it to read a file in
   the private folder. It gets blocked.

Tests: `python3 -m unittest discover -s tests` (Python 3.8+, standard library only).

## License

MIT, see [LICENSE](LICENSE).
