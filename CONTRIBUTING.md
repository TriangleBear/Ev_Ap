# Contributing

## Branch hierarchy

```
lower:  patch/* , fix/* , feature/*   (deleted once merged to mid)
mid:    dev/* , latest/*               (version lives in dev/* branch name)
high:   main                           (triggers build + release on merge)
```

- **Lower** branches (`patch/*`, `fix/*`, `feature/*`) are temporary — deleted once merged into `dev/*` or `latest/*`.
- **Mid** branches (`dev/*`, `latest/*`) hold the version number in the branch name (e.g. `dev/1.2.3`). `latest/*` is the staging/pre-release branch.
- **High** (`main`) is production. When `latest/*` is approved and merged to `main`, the full build + release pipeline runs.

## Workflow

1. Create a lower branch from `dev/*` or `latest/*`:
   - `patch/*` for bug fixes
   - `fix/*` for fixes
   - `feature/*` for new features

2. Open a pull request targeting `latest/*` from your `dev/*` branch. The PR title should include the version number for releases (e.g., `Release v1.0.1`).

3. PRs to `latest/*` automatically run tests. If tests pass, the PR is eligible for merge (no auto-merge). If tests fail, a GitHub Issue is created automatically.

4. Once approved and merged to `latest/*`, open a PR from `latest/*` to `main`.

5. Merging to `main` triggers:
   - Tests
   - Version detection (in priority order):
     1. PR title in the merge commit body (e.g., `Release v1.0.1`)
     2. Branch name version (e.g., `dev/1.0.1`)
     3. Latest git tag as fallback
   - Version bump per branch prefix:
     - `major/*` → major bump (1.0.0 → 2.0.0)
     - `feature/*` or `feat/*` → minor bump (1.0.0 → 1.1.0)
     - `dev/*`, `fix/*`, `patch/*`, `latest`, or anything else → patch bump (1.0.0 → 1.0.1)
   - PyInstaller build
   - GitHub Release with the new version

## Version examples

| Branch name | Base version | Bump type | Result |
|-------------|-------------|-----------|--------|
| `patch/1.0.1` | 1.0.1 | patch | v1.0.2 |
| `fix/1.0.1` | 1.0.1 | patch | v1.0.2 |
| `feature/1.3.0` | 1.3.0 | minor | v1.4.0 |
| `feat/1.3.0` | 1.3.0 | minor | v1.4.0 |
| `major/2.0.0` | 2.0.0 | major | v3.0.0 |
| `dev/1.0.1` | 1.0.1 | patch | v1.0.2 |
| `latest` (from PR title "Release v2.0.0") | 2.0.0 | patch | v2.0.1 |
