# MDR

MDR is a terminal-based file archive and refinement animation. The project is
also a small learning lab for Python packaging, testing, Docker, CI/CD, version
control, and release management.

## Run locally

The application needs Python 3.9 or newer and a real terminal.

```bash
python3 -m pip install -r requirements.txt
python3 app/index.py
```

Quit with `q` or `Ctrl+C`.

Use a custom configuration or artwork:

```bash
python3 app/index.py --config app/config.json
python3 app/index.py --image path/to/art.png
```

## Tests and linting

Install development dependencies and run the checks locally:

```bash
python3 -m pip install -r requirements-dev.txt
ruff check app tests
python3 -m unittest discover -s tests -v
```

The reusable custom action at [.github/actions/checks/action.yml](.github/actions/checks/action.yml)
runs these same checks in GitHub Actions.

## Docker

Build and run the Linux container:

```bash
docker compose build
docker compose up
```

Run the tests inside the container:

```bash
docker compose run --rm app python3 -m unittest discover -s tests -v
```

Docker provides a reproducible Linux environment. It does not create native
Windows or macOS binaries.

### Publish the Docker image

The `docker.yml` workflow builds the image on pull requests and publishes it to
Docker Hub on pushes to `main` and on version tags. Configure these repository
secrets before pushing:

- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token, not your password

The published image is available as:

```bash
docker pull ahmadabdelwhab/sodiummdr:latest
```

Version tags such as `v0.1.0` publish both `v0.1.0` and `0.1.0` image tags.

## Build binaries

PyInstaller must build on the operating system targeted by the binary.

macOS and Linux:

```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

Windows PowerShell:

```powershell
.\scripts\build.ps1
```

The output is `dist/mdr` on macOS and Linux, or `dist/mdr.exe` on Windows.

Download the latest ready-to-run binaries from the [GitHub Releases page](https://github.com/Ahmadabdelwhab/MDR/releases/latest):

- Linux: `mdr-linux`
- macOS: `mdr-macos`
- Windows: `mdr-windows.exe`

The build script bundles the default JSON configuration and Pillow support.
See [BUILD.md](BUILD.md) for more details.

macOS may warn that an unsigned binary cannot be verified. For a binary you
built yourself, run `xattr -d com.apple.quarantine ./dist/mdr`, or approve it
with Finder's **Open** command. Public macOS releases require Apple Developer
ID signing and notarization.

## GitHub Actions

The repository has two workflows:

- `actions.yml` runs linting and unit tests on pushes and pull requests.
- `build.yml` builds Linux, macOS, and Windows binaries and uploads temporary
  workflow artifacts.

## Releases

Release Please manages versioning and releases. Push commits to `main`, then
it creates or updates a release pull request using the commit history. Merging
that pull request creates the version tag and GitHub Release. The binary build
workflow then uploads the Linux, macOS, and Windows binaries to that release.

The initial manifest version is `0.1.0`. Release Please ignores older commits
that do not use its expected format, so the next change should use a
Conventional Commit message such as `feat: add image controls` or
`fix: handle small terminals`. It will then create the release PR.

If you need to create a version manually, push a semantic version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Generated binaries are kept out of Git history and attached to the GitHub
Release as downloadable assets.

## Project layout

```text
app/                    Application modules and bundled config
tests/                  Unit tests
scripts/                Platform build entrypoints
.github/actions/        Reusable lint-and-test custom action
.github/workflows/      CI, build, and release automation
Dockerfile              Linux container image
docker-compose.yaml     Local container commands
requirements*.txt       Runtime, development, and build dependencies
```
