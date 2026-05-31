# Security Policy

## Supported versions

This project is pre-1.0; only the latest `main` is supported.

## Reporting a vulnerability

Please report security issues privately via GitHub's
["Report a vulnerability"](https://github.com/supersfera-online/18676/security/advisories/new)
advisory flow, or by email to the maintainers. Do **not** open a public issue
for security problems.

Please include:
- a description of the issue and its impact,
- steps to reproduce,
- affected version/commit.

We aim to acknowledge reports within a few business days.

## Notes on this project's threat model

`claude-phone` executes shell commands on the device via `shell=True`. By design
every command is a **trusted literal** defined in `src/claude_phone/actions.py`;
user-supplied input (such as the CLI `--target`) is never interpolated into a
command. If you find a path where untrusted input reaches a shell, that is a
vulnerability — please report it.
