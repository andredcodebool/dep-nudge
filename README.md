# dep-nudge

> Python utility that scans requirements files and flags outdated or vulnerable packages with upgrade suggestions.

---

## Installation

```bash
pip install dep-nudge
```

---

## Usage

Run `dep-nudge` against your requirements file:

```bash
dep-nudge scan requirements.txt
```

**Example output:**

```
Scanning requirements.txt...

[OUTDATED]   requests 2.20.0  →  2.31.0
[VULNERABLE] urllib3 1.24.1   →  2.0.7   CVE-2023-43804
[OK]         click 8.1.3

2 issue(s) found. Run with --fix to auto-update.
```

### Options

| Flag | Description |
|------|-------------|
| `--fix` | Automatically update flagged packages |
| `--json` | Output results as JSON |
| `--ignore PKG` | Skip a specific package |

```bash
# Output as JSON
dep-nudge scan requirements.txt --json

# Ignore a package
dep-nudge scan requirements.txt --ignore requests
```

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

This project is licensed under the [MIT License](LICENSE).