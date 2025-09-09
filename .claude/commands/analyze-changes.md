# Analyze Changes - Generate Release Notes and Change Summary

**Description:** Examines current branch changes versus base branch and generates comprehensive release notes and change summaries.

**Usage:** `/analyze-changes [--branch <name>]`

## Options

- `--branch <name>`: Compare against specific branch (default: main or master)

## How it works

1. **Compare Branches**: Analyzes differences between current branch and base
2. **Categorize Changes**: Groups changes by type (features, fixes, improvements)
3. **Generate Notes**: Creates formatted release notes
4. **Impact Assessment**: Evaluates scope and impact of changes

## Implementation

This command will:
- Run `git diff` and `git log` to compare branches
- Analyze modified files and their purposes
- Extract meaningful change descriptions from commits
- Categorize changes using conventional commit patterns
- Generate structured release notes
- Assess breaking changes and compatibility

## Change Categories

- **🚀 Features**: New functionality and capabilities
- **🐛 Bug Fixes**: Error corrections and issue resolutions  
- **⚡ Improvements**: Performance and usability enhancements
- **📚 Documentation**: Documentation updates and additions
- **🔧 Maintenance**: Refactoring, cleanup, and internal changes
- **💥 Breaking Changes**: Incompatible API changes

## Example Output

```
📋 Change Analysis Report

Branch: feature/user-auth → main
Files Changed: 12 files (+234 -56 lines)
Commits: 8 commits

## 🚀 New Features
- **User Authentication**: JWT-based login/logout system
- **User Profiles**: Complete user profile management
- **Role-based Access**: Permission system with admin/user roles

## 🐛 Bug Fixes  
- Fixed validation error in user registration
- Resolved session timeout handling
- Corrected password reset email formatting

## ⚡ Improvements
- Enhanced error messages for better UX
- Optimized database queries for user lookup
- Added comprehensive logging for auth events

## 📚 Documentation
- Updated API documentation with auth endpoints
- Added user management guide
- Created deployment configuration examples

## 🔧 Technical Changes
- Refactored authentication middleware
- Updated database schema with user tables
- Added comprehensive test coverage for auth flow
```