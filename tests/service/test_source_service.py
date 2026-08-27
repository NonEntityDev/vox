from pathlib import Path

import pytest
import typer
from assertpy import assert_that

import vox.service.source_service as source_service_module
from vox.service.source_service import SourceService


@pytest.fixture
def source_service():
    return SourceService()


def test_fetch_and_render_from_parses_metadata_and_renders_markdown(
    source_service, tmp_path: Path
):
    # Arrange
    source_file = tmp_path / "post.md"
    source_file.write_text("---\ntitle: Hello World\ntype: post\n---\n# Heading\n")

    # Act
    result = source_service.fetch_and_render_from(path=str(source_file))

    # Assert
    assert_that(result["title"]).is_equal_to("Hello World")
    assert_that(result["type"]).is_equal_to("post")
    assert_that(result["body"]).contains("<h1").contains("Heading")


def test_fetch_and_render_from_aborts_when_the_file_is_missing(
    source_service, tmp_path: Path
):
    # Arrange
    missing_file = tmp_path / "does_not_exist.md"

    # Act / Assert
    with pytest.raises(typer.Abort):
        source_service.fetch_and_render_from(path=str(missing_file))


def test_fetch_and_render_from_aborts_when_markdown_rendering_fails(
    source_service, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    # Arrange
    source_file = tmp_path / "post.md"
    source_file.write_text("---\ntitle: Hello World\ntype: post\n---\n# Heading\n")

    def broken_markdown(*args, **kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(source_service_module, "markdown", broken_markdown)

    # Act / Assert
    with pytest.raises(typer.Abort):
        source_service.fetch_and_render_from(path=str(source_file))
