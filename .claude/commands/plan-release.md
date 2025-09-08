# Plan Release - Create Release Strategy and Checklist

**Description:** Analyzes unreleased changes and creates a comprehensive release plan with checklist, version recommendation, and deployment strategy.

**Usage:** `/plan-release [--target <version>]`

## Options

- `--target <version>`: Plan for specific target version (e.g., "1.2.0", "2.0.0")

## How it works

1. **Change Analysis**: Reviews unreleased commits and modifications
2. **Impact Assessment**: Evaluates breaking changes and compatibility
3. **Version Strategy**: Recommends version number if not specified
4. **Release Checklist**: Creates comprehensive pre-release checklist
5. **Deployment Plan**: Suggests deployment and rollback strategies

## Implementation

This command will:
- Analyze commits since last release tag
- Assess scope and impact of changes
- Generate version recommendation using semantic versioning
- Create release checklist based on project structure
- Suggest testing and validation steps
- Provide deployment guidance

## Release Planning Components

### 📊 Change Impact Analysis
- Breaking changes and migration requirements
- New features and their dependencies  
- Bug fixes and security updates
- Performance and compatibility considerations

### 📋 Release Checklist
- Code quality validation (linting, tests, type checking)
- Documentation updates
- Version file and changelog updates
- Security and dependency reviews
- Deployment preparation

### 🚀 Deployment Strategy
- Environment preparation steps
- Rollback procedures
- Monitoring and validation points
- Communication plan

## Example Output

```
📋 Release Plan for v1.3.0

## 📊 Release Summary
**Target Version:** 1.3.0 (Minor Release)  
**Changes Since:** v1.2.5 (2 weeks ago)
**Commits:** 23 commits across 8 files
**Risk Level:** LOW - No breaking changes identified

## 🔄 Change Impact
### 🚀 New Features (3)
- User authentication system with JWT tokens
- Profile management with avatar uploads  
- Email notification system

### 🐛 Bug Fixes (5)
- Fixed memory leak in data processing
- Resolved race condition in async handlers
- Corrected validation logic for user input

### ⚡ Improvements (4)
- Enhanced error messages and logging
- Optimized database query performance
- Updated dependencies to latest versions

## ✅ Pre-Release Checklist

### Code Quality
- [ ] Run full test suite (`/run-tests --coverage`)
- [ ] Execute code quality pipeline (`/check-code --fix --report`)  
- [ ] Verify type checking passes (`mypy .`)
- [ ] Review security scan results

### Documentation  
- [ ] Update CHANGELOG.md with release notes
- [ ] Review and update API documentation
- [ ] Verify README.md reflects current features
- [ ] Update version references in docs

### Release Preparation
- [ ] Update VERSION file to 1.3.0
- [ ] Tag release commit (`git tag v1.3.0`)
- [ ] Build and test deployment package
- [ ] Prepare rollback procedures

### Deployment Validation
- [ ] Deploy to staging environment
- [ ] Execute smoke tests and integration tests
- [ ] Verify backward compatibility
- [ ] Monitor performance metrics

## 🚀 Deployment Plan

### Pre-Deployment
1. Notify stakeholders of planned release
2. Prepare rollback scripts and procedures
3. Schedule maintenance window if needed

### Deployment Steps  
1. Deploy to staging → validate → deploy to production
2. Monitor application health and error rates
3. Verify key functionality works as expected
4. Update monitoring dashboards

### Post-Deployment
1. Monitor for 24 hours after release
2. Collect user feedback and issue reports
3. Document lessons learned and process improvements

## 🔄 Rollback Strategy
- Database migrations: Reversible schema changes prepared
- Code rollback: Previous version tagged and deployable
- Configuration: Environment-specific rollback procedures ready

**Estimated Release Timeline:** 2-3 days
**Recommended Release Window:** Tuesday-Thursday (avoiding Fridays)
```