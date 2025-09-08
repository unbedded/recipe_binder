Start GitFlow branch workflow: $ARGUMENTS

Required arguments:
- `<branch_type>` - Branch type: `feature`, `release`, `hotfix`, `bugfix`
- `<branch_name>` - Name for the new branch

Examples:
- `/gitflow-start feature user-authentication` → Creates `feature/user-authentication`
- `/gitflow-start release 1.2.0` → Creates `release/1.2.0`  
- `/gitflow-start hotfix critical-security-fix` → Creates `hotfix/critical-security-fix`
- `/gitflow-start bugfix login-error` → Creates `bugfix/login-error`

Branch creation rules:
- `feature/*` - Branches from `develop`, merges back to `develop`
- `release/*` - Branches from `develop`, merges to `main` and `develop`  
- `hotfix/*` - Branches from `main`, merges to `main` and `develop`
- `bugfix/*` - Branches from `develop`, merges back to `develop`

Executes: `git flow <branch_type> start <branch_name>`
Automatically switches to the new branch after creation.