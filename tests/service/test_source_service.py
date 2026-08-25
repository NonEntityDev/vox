from pathlib import Path

import pytest
import typer
from assertpy import assert_that

from vox.service.source_service import SourceService


@pytest.fixture
def source_service():
    return SourceService()


def test_fetch_and_render_from_parses_metadata_and_renders_markdown(
    source_service, tmp_path: Path
):
    # Arrange
    source_file = tmp_path / "post.md"
    source_file.write_text(
        "---\n"
        "title: Hello World\n"
        "type: post\n"
        "---\n"
        "# Heading\n"
    )

    # Act
    result = source_service.fetch_and_render_from(path=str(source_file))

    # Assert
    assert_that(result["title"]).is_equal_to("Hello World")
    assert_that(result["type"]).is_equal_to("post")
    assert_that(result["content"]).contains("<h1").contains("Heading")


def test_fetch_and_render_from_aborts_when_the_file_is_missing(
    source_service, tmp_path: Path
):
    # Arrange
    missing_file = tmp_path / "does_not_exist.md"

    # Act / Assert
    with pytest.raises(typer.Abort):
        source_service.fetch_and_render_from(path=str(missing_file))
