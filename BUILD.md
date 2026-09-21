# Build the `mdr` binary

The project can be packaged as a single command-line executable with PyInstaller.

## Build

```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

The output is:

```text
dist/mdr
```

Run it from a terminal:

```bash
./dist/mdr
```

### macOS Gatekeeper

A locally built or GitHub Actions-built macOS binary is not notarized by Apple,
so macOS may show a message saying it cannot verify `mdr`. For a binary you
built yourself, remove the quarantine attribute from that file:

```bash
xattr -d com.apple.quarantine ./dist/mdr
./dist/mdr
```

You can also use Finder's **Open** command once and confirm the prompt. Do not
disable Gatekeeper globally.

For public macOS releases, the binary needs an Apple Developer ID signature
and Apple notarization. That requires an Apple Developer account and signing
credentials; ad-hoc signing alone will not remove this warning for downloads.

The application is a curses interface, so it must run in a real terminal or an
interactive shell. Quit with `q` or `Ctrl+C`.

## Custom configuration

The default JSON configuration is bundled into the binary. To use another file:

```bash
./dist/mdr --config path/to/config.json
```

Artwork can be supplied directly:

```bash
./dist/mdr --image path/to/art.png
```

Build on the operating system where the binary will run. A macOS executable is
not portable to Linux, and vice versa.

## Run tests in Docker

```bash
docker compose build
docker compose run --rm app python3 -m unittest discover -s tests -v
```

This runs the same tests in the clean Python environment used by the container.
