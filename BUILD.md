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
