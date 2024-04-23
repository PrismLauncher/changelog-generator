# changelog-generator

## How to use

- run `nix develop`
- create a read-only Github Token
- set GITHUB_TOKEN environment variable to that value
- run `python -m changelog_generator {owner}/{repo} {milestone}`

e.g `python -m changelog_generator Prismlauncher/PrismLauncher 8.3`
