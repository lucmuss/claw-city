# Git Workflow

This repository uses a lightweight trunk based workflow.

## Branches

- `main` is always release ready.
- Create feature branches from `main`.

## Changes

1. Create a branch: `git checkout -b feat/short-description`.
2. Commit focused changes with clear messages.
3. Open a pull request to `main`.
4. Merge after CI is green.

## Release tags

- Tag releases as `vX.Y.Z`.
- Push tags to trigger the release workflow.

## Hotfixes

1. Branch from `main`.
2. Apply the fix and add tests.
3. Tag a patch release.
