Finish GitFlow branch workflow: $ARGUMENTS

Required arguments:
- `<branch_type>` - Branch type: `feature`, `release`, `hotfix`, `bugfix`
- `<branch_name>` - Name of the branch to finish

Options:
- `--keep-branch` - Keep the branch after merging (don't delete)
- `--no-ff` - Force no fast-forward merge

Examples:
- `/gitflow-finish feature user-authentication` - Finish and delete feature branch
- `/gitflow-finish release 1.2.0` - Finish release, merge to main and develop
- `/gitflow-finish hotfix critical-fix --keep-branch` - Finish but keep branch

Merge behavior:
- `feature/*` - Merges to `develop`, deletes branch
- `release/*` - Merges to both `main` and `develop`, creates version tag, deletes branch
- `hotfix/*` - Merges to both `main` and `develop`, creates version tag, deletes branch
- `bugfix/*` - Merges to `develop`, deletes branch

For releases/hotfixes: Automatically creates git tag using VERSION file content.
Executes: `git flow <branch_type> finish <branch_name>`