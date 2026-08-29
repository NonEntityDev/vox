from pathlib import Path

import pytest
import typer
from assertpy import assert_that
from typer.testing import CliRunner

from vox.commands.index_command import prepare_index_command


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def app() -> typer.Typer:
    app = typer.Typer()
    prepare_index_command(app)
    return app


@pytest.fixture
def theme_folder(tmp_path: Path) -> Path:
    theme_path = tmp_path / "theme"
    theme_path.mkdir()
    (theme_path / "index.html").write_text(
        "<ul>{% for item in items %}<li>{{ item.title }}</li>{% endfor %}</ul>"
        "<span>page {{ pagination.page }} of {{ pagination.total_pages }}</span>"
        "<span>next: {{ pagination.next_page }}</span>"
        "<span>previous: {{ pagination.previous_page }}</span>"
    )
    return theme_path


def _write_indexable_content(
    path: Path, title: str, date_published: str, content_type: str = "Post"
) -> None:
    path.write_text(
        '<html><head><script type="application/ld+json">'
        f'{{"@type": "{content_type}", "title": "{title}", '
        f'"datePublished": "{date_published}"}}'
        "</script></head><body></body></html>"
    )


def test_index_writes_a_single_page_when_content_fits_within_the_page_size(
    runner: CliRunner, app: typer.Typer, theme_folder: Path, tmp_path: Path
):
    # Arrange
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    _write_indexable_content(source_folder / "a.html", "A", "2026-01-01")
    _write_indexable_content(source_folder / "b.html", "B", "2026-01-02")

    target_folder = tmp_path / "target"
    target_folder.mkdir()

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_folder),
            "--target",
            str(target_folder),
            "--theme",
            str(theme_folder),
            "--settings",
            str(tmp_path / "settings.yaml"),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)
    index_content = (target_folder / "index.html").read_text()
    assert_that(index_content).contains("<li>B</li>").contains("<li>A</li>")
    assert_that(str(target_folder / "index_page1.html")).does_not_exist()


def test_index_sorts_content_descending_by_the_sort_field(
    runner: CliRunner, app: typer.Typer, theme_folder: Path, tmp_path: Path
):
    # Arrange
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    _write_indexable_content(source_folder / "a.html", "A", "2026-01-01")
    _write_indexable_content(source_folder / "b.html", "B", "2026-01-02")

    target_folder = tmp_path / "target"
    target_folder.mkdir()

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_folder),
            "--target",
            str(target_folder),
            "--theme",
            str(theme_folder),
            "--settings",
            str(tmp_path / "settings.yaml"),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)
    index_content = (target_folder / "index.html").read_text()
    assert_that(index_content.index("<li>B</li>")).is_less_than(
        index_content.index("<li>A</li>")
    )


def test_index_splits_content_into_multiple_linked_pages(
    runner: CliRunner, app: typer.Typer, theme_folder: Path, tmp_path: Path
):
    # Arrange
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    _write_indexable_content(source_folder / "a.html", "A", "2026-01-01")
    _write_indexable_content(source_folder / "b.html", "B", "2026-01-02")
    _write_indexable_content(source_folder / "c.html", "C", "2026-01-03")

    target_folder = tmp_path / "target"
    target_folder.mkdir()

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_folder),
            "--target",
            str(target_folder),
            "--theme",
            str(theme_folder),
            "--items-per-page",
            "2",
            "--settings",
            str(tmp_path / "settings.yaml"),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)

    first_page = (target_folder / "index.html").read_text()
    assert_that(first_page).contains("<li>C</li>").contains("<li>B</li>")
    assert_that(first_page).contains("next: index_page1.html")
    assert_that(first_page).contains("previous: None")

    second_page = (target_folder / "index_page1.html").read_text()
    assert_that(second_page).contains("<li>A</li>")
    assert_that(second_page).contains("previous: index.html")
    assert_that(second_page).contains("next: None")


def test_index_ignores_content_of_the_ignored_types(
    runner: CliRunner, app: typer.Typer, theme_folder: Path, tmp_path: Path
):
    # Arrange
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    _write_indexable_content(source_folder / "a.html", "A", "2026-01-01")
    _write_indexable_content(
        source_folder / "about.html", "About", "2026-01-01", content_type="Page"
    )

    target_folder = tmp_path / "target"
    target_folder.mkdir()

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_folder),
            "--target",
            str(target_folder),
            "--theme",
            str(theme_folder),
            "--settings",
            str(tmp_path / "settings.yaml"),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)
    index_content = (target_folder / "index.html").read_text()
    assert_that(index_content).contains("<li>A</li>").does_not_contain("<li>About</li>")


def test_index_honors_the_max_pages_limit(
    runner: CliRunner, app: typer.Typer, theme_folder: Path, tmp_path: Path
):
    # Arrange
    source_folder = tmp_path / "source"
    source_folder.mkdir()
    _write_indexable_content(source_folder / "a.html", "A", "2026-01-01")
    _write_indexable_content(source_folder / "b.html", "B", "2026-01-02")
    _write_indexable_content(source_folder / "c.html", "C", "2026-01-03")

    target_folder = tmp_path / "target"
    target_folder.mkdir()

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_folder),
            "--target",
            str(target_folder),
            "--theme",
            str(theme_folder),
            "--items-per-page",
            "1",
            "--max-pages",
            "1",
            "--settings",
            str(tmp_path / "settings.yaml"),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)
    assert_that(str(target_folder / "index.html")).exists()
    assert_that(str(target_folder / "index_page1.html")).does_not_exist()
