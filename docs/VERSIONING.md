# Versioning policy for ePICRPG

This project stores the authoritative game name and version in `version.py`:

- `GAME_NAME` — displayed game name.
- `VERSION` — displayed and saved version string.

Policy:
- The version must be changed manually by editing `version.py`.
- Use one decimal place (example: `1.3`, `1.4`).
- Do NOT create or enable scripts that auto-increment the version on each run.
- The version in `save_system.py` is taken from `version.py` when saving.

How to bump the version:
1. Open `version.py`.
2. Update `VERSION = "1.3"` to the new value (for example, `"1.4"`).
3. Commit the change to your repository as part of the release.

