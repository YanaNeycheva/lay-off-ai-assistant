# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2026-08-28

### Added
- `CHANGELOG.md` in Keep a Changelog format, covering the 0.1.x history.

### Changed
- Versioning policy in `CLAUDE.md` now requires a changelog entry per release.

## [0.1.1] - 2026-08-28

### Changed
- Moved all per-person files under a git-ignored `Personal/<date>-<slug>/` root.
- Corrected the `CLAUDE.md` dev-commit convention and the person-data rule.

## [0.1.0] - 2026-08-27

### Added
- Full Bulgarian guide (`knowledge-base/guide.md`).
- Orchestrator + subagents architecture.
- Vendored `/tailor-cv` skill as the CV engine.
- `/comeback` entry-point skill (front door + per-person dossier bootstrap).
- `freshness-checker` verification gate for institutional facts.
- SemVer adoption and top-level `VERSION` file.
