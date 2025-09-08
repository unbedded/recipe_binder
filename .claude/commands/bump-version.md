Bump project version using PEP 440 semantic versioning: $ARGUMENTS

Required argument:
- `<level>` - Version level to bump: `patch`, `minor`, `major`

Optional arguments:
- `--pre-release <type>` - Add pre-release identifier: `alpha`, `beta`, `rc` (or shortcuts: `a`, `b`, `rc`)

Examples:
- `/bump-version patch` → 1.0.0 → 1.0.1
- `/bump-version minor` → 1.0.0 → 1.1.0  
- `/bump-version major` → 1.0.0 → 2.0.0
- `/bump-version minor --pre-release alpha` → 1.0.0 → 1.1.0a1
- `/bump-version patch --pre-release beta` → 1.0.0 → 1.0.1b1

Actions performed:
1. Read current version from VERSION file
2. Calculate new version based on level and pre-release
3. Update VERSION file
4. Update CHANGELOG.md with new version entry
5. Display new version number

Uses: `python .claude/tools/version_bump.py --bump $1 --pre-release $2`