# Agent memory — lives in the vault, not in the agent

Hermes keeps two memory files: `USER.md` (who you are) and `MEMORY.md` (working notes it
writes as it learns). They live **here**, inside the vault, so the memory survives switching
agents. Hermes' memory path is hardcoded, so a symlink points it here:

```bash
VAULT="/path/to/vault"
mv ~/.hermes/memories/USER.md ~/.hermes/memories/MEMORY.md "$VAULT/0 - System/memories/"
rmdir ~/.hermes/memories
ln -s "$VAULT/0 - System/memories" ~/.hermes/memories
```

On a fresh Hermes install with no memories yet, skip the `mv` and keep the two templates.

**Format:** Hermes splits each file into entries on a line holding only `§`. Don't add vault
frontmatter. Size limits and toggles live under `memory:` in `~/.hermes/config.yaml`.

**Privacy:** these files hold personal data once Hermes starts writing. The two here are
templates; don't commit the real ones to a public repo.

- If the vault is on iCloud, set this folder to "Keep Downloaded". Optimize Mac Storage can
  evict a file mid-session.
- To swap Hermes for another agent, point (or symlink) the new agent's memory location here.
