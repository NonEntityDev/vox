from pathlib import Path
from unittest.mock import MagicMock

import pytest
import typer
from assertpy import assert_that
from typer.testing import CliRunner

import vox.commands.generate_command as generate_command_module
from vox.commands.generate_command import prepare_generate_command


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def app() -> typer.Typer:
    app = typer.Typer()
    prepare_generate_command(app)
    return app


@pytest.fixture
def theme_folder(tmp_path: Path) -> Path:
    theme_path = tmp_path / "theme"
    theme_path.mkdir()
    (theme_path / "post.html").write_text("<h1>{{ content.title }}</h1>")
    return theme_path


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    source_path = tmp_path / "source.md"
    source_path.write_text(
        "---\ntitle: Hello World\ntype: post\nrelative_path: /output/index.html\n---\n# Body\n"
    )
    return source_path


def test_generate_writes_the_rendered_content_to_the_target_path(
    runner: CliRunner,
    app: typer.Typer,
    source_file: Path,
    theme_folder: Path,
    tmp_path: Path,
):
    # Arrange
    target_path = tmp_path
    (tmp_path / "output").mkdir()
    missing_settings_path = tmp_path / "settings.yaml"

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_file),
            "--target",
            str(target_path),
            "--theme",
            str(theme_folder),
            "--settings",
            str(missing_settings_path),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)
    assert_that((target_path / "output" / "index.html").read_text()).is_equal_to(
        "<h1>Hello World</h1>"
    )


def test_generate_honors_the_content_type_override(
    runner: CliRunner, app: typer.Typer, theme_folder: Path, tmp_path: Path
):
    # Arrange
    source_path = tmp_path / "source.md"
    source_path.write_text(
        "---\ntitle: Untyped\nrelative_path: /output/index.html\n---\n# Body\n"
    )
    target_path = tmp_path
    (tmp_path / "output").mkdir()

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_path),
            "--target",
            str(target_path),
            "--theme",
            str(theme_folder),
            "--content-type",
            "post",
            "--settings",
            str(tmp_path / "settings.yaml"),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)
    assert_that((target_path / "output" / "index.html").read_text()).is_equal_to(
        "<h1>Untyped</h1>"
    )


def test_generate_aborts_when_the_content_type_cannot_be_inferred(
    runner: CliRunner, app: typer.Typer, theme_folder: Path, tmp_path: Path
):
    # Arrange
    source_path = tmp_path / "source.md"
    source_path.write_text("---\ntitle: Untyped\n---\n# Body\n")
    target_path = tmp_path / "output" / "index.html"

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_path),
            "--target",
            str(target_path),
            "--theme",
            str(theme_folder),
            "--settings",
            str(tmp_path / "settings.yaml"),
        ],
    )

    # Assert
    assert_that(result.exit_code).is_not_equal_to(0)


def test_generate_with_preview_starts_the_preview_service(
    runner: CliRunner,
    monkeypatch: pytest.MonkeyPatch,
    source_file: Path,
    theme_folder: Path,
    tmp_path: Path,
):
    # Arrange
    preview_service_instance = MagicMock()
    preview_service_class = MagicMock(return_value=preview_service_instance)
    monkeypatch.setattr(
        generate_command_module, "PreviewService", preview_service_class
    )

    app = typer.Typer()
    prepare_generate_command(app)

    target_path = tmp_path
    (target_path / "output").mkdir()
    settings_path = tmp_path / "settings.yaml"

    # Act
    result = runner.invoke(
        app,
        [
            "--source",
            str(source_file),
            "--target",
            str(target_path),
            "--theme",
            str(theme_folder),
            "--settings",
            str(settings_path),
            "--preview",
            "--server-port",
            "9100",
        ],
    )

    # Assert
    assert_that(result.exit_code).is_equal_to(0)
    call_kwargs = preview_service_instance.start_preview_mode.call_args.kwargs
    assert_that(call_kwargs["watch_file_list"]).is_equal_to(
        [str(source_file), str(settings_path), f"{theme_folder}/post.html"]
    )
    assert_that(call_kwargs["content_folder"]).is_equal_to(str(target_path))
    assert_that(call_kwargs["tcp_port"]).is_equal_to(9100)
    assert_that(callable(call_kwargs["on_change"])).is_true()
