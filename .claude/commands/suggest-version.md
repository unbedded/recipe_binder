# Suggest Version - Recommend Version Bump Level

**Description:** Examines changes since last version and recommends appropriate version bump level (patch, minor, major).

**Usage:** `/suggest-version [--analyze]`

## Options

- `--analyze`: Show detailed change analysis and reasoning

## How it works

1. **Read Current Version**: Gets current version from VERSION file
2. **Analyze Changes**: Reviews commits since last version tag
3. **Classify Changes**: Categorizes changes as:
   - **Breaking changes** → major bump
   - **New features** → minor bump  
   - **Bug fixes** → patch bump
   - **Documentation/refactor** → patch bump
4. **Recommend Level**: Suggests appropriate version bump

## Implementation

This command will:
- Read VERSION file to get current version
- Run `git log` to get commits since last version tag
- Analyze commit messages and code changes
- Apply semantic versioning rules
- Consider PEP 440 compliance for Python projects
- Recommend version bump level with reasoning

## Semantic Versioning Rules

- **Major (X.0.0)**: Breaking changes, incompatible API changes
- **Minor (0.X.0)**: New features, backwards-compatible additions
- **Patch (0.0.X)**: Bug fixes, backwards-compatible fixes

## Example Output

```
📋 Version Bump Recommendation

Current Version: 1.2.3
Recommended: MINOR bump → 1.3.0

📊 Change Analysis:
- 3 new features added (auth module, user profiles, API endpoints)
- 2 bug fixes (validation, error handling)
- 1 documentation update
- 0 breaking changes

💡 Reasoning:
New features warrant a minor version bump. All changes are backwards-compatible.

Suggested command: /bump-version minor
```