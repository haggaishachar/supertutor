"""Skill and strategy prose, packaged so a non-file consumer (e.g.
`tutorapp`'s Agent Runtime) can load it via `importlib.resources` instead of
reading a git checkout at runtime. See docs/superpowers/plans/
2026-09-02-state-model-decoupling-plan.md, C8.

This package deliberately contains no importable Python beyond this
docstring — every other file under here is data (`SKILL.md`,
`strategies/*.md`), read as text, never executed.
"""
