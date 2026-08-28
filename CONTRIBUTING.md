# Contributing

**Read [CLAUDE.md](CLAUDE.md) first.** It is the source of truth for architecture and conventions; this file only points at the essentials.

## Language

Bulgarian for user-facing content (the agent's replies, the guide, templates, mode playbooks). English for everything else — code, config, docs, and commit messages.

## Architecture

One **orchestrator** ([agent/orchestrator.md](agent/orchestrator.md)) holds the relationship and routes work to **subagents** ([.claude/agents/](.claude/agents/)), which are bounded tools it calls. The `freshness-checker` subagent independently verifies institutional facts (НАП / НОИ / Бюро по труда) in another subagent's output — producer ≠ checker.

## Versioning & workflow

This project follows [SemVer](https://semver.org/). Every change bumps the top-level `VERSION` file, gets an annotated tag (`git tag -a vX.Y.Z -m "…"`), and adds a [CHANGELOG.md](CHANGELOG.md) entry ([Keep a Changelog](https://keepachangelog.com/) format).

## Licensing

By contributing you agree that code contributions are licensed under [MIT](LICENSE), and contributions to `knowledge-base/` content under [CC BY-NC 4.0](knowledge-base/LICENSE).

## Never commit person data

All files generated for a person live under `Personal/` (git-ignored). Never commit them.
