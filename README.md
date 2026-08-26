# vox

Ultra minimal static site generator powered by FrontMatter and Jinja2.

## Building locally

vox uses [Poetry](https://python-poetry.org/) to manage dependencies and packaging.

```bash
git clone https://github.com/NonEntityDev/vox.git
cd vox
poetry install
```

This installs both the runtime and development dependency groups into a Poetry-managed virtual environment.

### Dependencies

Runtime:

- [typer](https://typer.tiangolo.com/)
- [python-frontmatter](https://python-frontmatter.readthedocs.io/)
- [Jinja2](https://jinja.palletsprojects.com/)
- [Markdown](https://python-markdown.github.io/)
- [PyYAML](https://pyyaml.org/)
- [Pygments](https://pygments.org/)
- [watchdog](https://python-watchdog.readthedocs.io/)

Development:

- [pytest](https://docs.pytest.org/), pytest-sugar, pytest-randomly
- [coverage](https://coverage.readthedocs.io/)
- [mypy](https://mypy-lang.org/)
- [bandit](https://bandit.readthedocs.io/)
- [ruff](https://docs.astral.sh/ruff/)
- [basedpyright](https://docs.basedpyright.com/)
- [poethepoet](https://poethepoet.natn.io/)
- [assertpy](https://assertpy.github.io/)
- [debugpy](https://github.com/microsoft/debugpy)

### Common tasks

Project tasks are defined as [Poe the Poet](https://poethepoet.natn.io/) tasks:

```bash
poetry run poe format             # Format the code base with ruff
poetry run poe type-check         # Type-check with mypy
poetry run poe vulnerability-check # Scan for vulnerabilities with bandit
poetry run poe lint               # Lint with pylint
poetry run poe tests              # Run the test suite with coverage instrumentation
poetry run poe coverage           # Generate an HTML coverage report
poetry run poe check-coverage     # Fail if coverage is below the required threshold
poetry run poe build              # Run all of the above, in order
```

## Usage

Once installed, run vox as a module:

```bash
poetry run python -m vox [OPTIONS]
```

### `generate`

Generates a static page by combining a FrontMatter document, a Jinja2 template and, optionally, additional parameters from a YAML settings file.

```bash
poetry run python -m vox --source content/hello-world.md --target public/hello-world/index.html
```

Options:

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `--source` | Yes | — | Path to the source FrontMatter document. |
| `--target` | Yes | — | Target path for the generated static page. |
| `--content-type` | No | — | Overrides the `type` property from the FrontMatter document. |
| `--theme` | No | `./theme` | Path to the folder containing the theme templates. The template file used is resolved from the content type (e.g. `post.html`). |
| `--settings` | No | `./settings.yaml` | Path to a YAML file with extra data made available to the template. The command does not fail if this file is missing. |
| `--preview` | No | `false` | Starts a local web server that serves the target folder and regenerates the page whenever the source file, settings file or theme template change. |
| `--server-port` | No | `8000` | TCP port for the `--preview` web server. |

Example with live preview:

```bash
poetry run python -m vox --source content/hello-world.md --target public/hello-world/index.html --preview
```

## License

Distributed under the [MIT License](LICENSE).
