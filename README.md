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

Once installed, run vox as a module. It exposes two commands, `generate` and `index`:

```bash
poetry run python -m vox COMMAND [OPTIONS]
```

### `generate`

Generates a static page by combining a FrontMatter document, a Jinja2 template and, optionally, additional parameters from a YAML settings file.

```bash
poetry run python -m vox generate --source content/hello-world.md --target public/hello-world/index.html
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
poetry run python -m vox generate --source content/hello-world.md --target public/hello-world/index.html --preview
```

### `index`

Scans a folder of **already generated** static pages (i.e. the output of `generate`, not FrontMatter source files), collects their metadata, and renders one or more paginated index pages from it.

For a page to be picked up, its theme template must embed a `<script type="application/ld+json">` block with the page's structured metadata — this is what `index` reads to build each listing entry. At minimum it needs an `@type` entry (used for the `--ignore-types` filter) and whichever field `--sort-by` points at (`datePublished` by default). For example, a `post.html` theme template used by `generate` could include:

```html
<script type="application/ld+json">
{
    "@type": "Post",
    "title": "{{ content.title }}",
    "datePublished": "{{ content.datePublished }}",
    "permalink": "{{ content.permalink_path }}"
}
</script>
```

```bash
poetry run python -m vox index --source public --target public
```

Options:

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `--source` | Yes | — | Path to the folder containing the generated content to be indexed. Scanned recursively for `*.html` files. |
| `--target` | Yes | — | Path to the target folder where the generated index page(s) will be saved. |
| `--items-per-page` | No | `10` | Number of indexed items listed per index page. |
| `--max-pages` | No | `0` | Max number of index pages to generate. `0` means no limit. |
| `--theme` | No | `./theme` | Path to the folder containing the theme to use to render the index page(s). |
| `--template` | No | `index` | Name (without the `.html` extension) of the template within the theme used to render the index. Also used as the base name for the generated file(s), see naming below. |
| `--ignore-types` | No | `page` | Comma separated list of `@type` values to exclude from the index. |
| `--sort-by` | No | `datePublished` | Name of the metadata field used to sort indexed items. |
| `--sort-direction` | No | `desc` | Sort direction: `asc` or `desc`. |
| `--settings` | No | `./settings.yaml` | Path to a YAML file with extra data made available to the template. The command does not fail if this file is missing. |

Generated page naming: the first page is written as `{template}.html`; every following page gets a `_page{n}` suffix, e.g. `index.html`, `index_page1.html`, `index_page2.html`, ...

The index template is rendered with:

| Context key | Description |
| --- | --- |
| `items` | List of the current page's indexed content metadata (the parsed `ld+json` for each entry). |
| `pagination.page` | Zero-based index of the current page. |
| `pagination.total_pages` | Total number of generated pages. |
| `pagination.items_per_page` | The `--items-per-page` value used. |
| `pagination.total_items` | Number of items on the current page. |
| `pagination.current_page` | File name of the current page. |
| `pagination.previous_page` | File name of the previous page, or `None` on the first page. |
| `pagination.next_page` | File name of the next page, or `None` on the last page. |
| `settings` | Parsed contents of the `--settings` YAML file. |

A minimal `index.html` theme template:

```html
<ul>
{% for item in items %}
    <li><a href="{{ item.permalink }}">{{ item.title }}</a></li>
{% endfor %}
</ul>

{% if pagination.previous_page %}<a href="{{ pagination.previous_page }}">Newer</a>{% endif %}
{% if pagination.next_page %}<a href="{{ pagination.next_page }}">Older</a>{% endif %}
```

More examples:

```bash
# 5 items per page, oldest first
poetry run python -m vox index --source public --target public --items-per-page 5 --sort-direction asc

# Only keep the first 2 pages, and also exclude drafts from the index
poetry run python -m vox index --source public --target public --max-pages 2 --ignore-types page,draft

# Use a dedicated template/file name, e.g. to build a separate "featured.html" index
poetry run python -m vox index --source public --target public --template featured
```

## License

Distributed under the [MIT License](LICENSE).
