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


def _write_ld_json(path: Path, metadata: str) -> None:
    path.write_text(
        f'<html><head><script type="application/ld+json">{metadata}'
        "</script></head><body></body></html>"
    )


def test_extract_content_metadata_parses_the_ld_json_block(
    source_service, tmp_path: Path
):
    # Arrange
    content_file = tmp_path / "post.html"
    _write_ld_json(content_file, '{"@type": "Post", "title": "Hello World"}')

    # Act
    metadata = source_service.extract_content_metadata(file_path=str(content_file))

    # Assert
    assert_that(metadata).is_equal_to({"@type": "Post", "title": "Hello World"})


def test_extract_content_metadata_returns_none_when_there_is_no_ld_json_block(
    source_service, tmp_path: Path
):
    # Arrange
    content_file = tmp_path / "post.html"
    content_file.write_text("<html><body>No metadata here</body></html>")

    # Act
    metadata = source_service.extract_content_metadata(file_path=str(content_file))

    # Assert
    assert_that(metadata).is_none()


def test_extract_content_metadata_returns_none_when_the_file_is_missing(
    source_service, tmp_path: Path
):
    # Arrange
    missing_file = tmp_path / "does_not_exist.html"

    # Act
    metadata = source_service.extract_content_metadata(file_path=str(missing_file))

    # Assert
    assert_that(metadata).is_none()


def test_extract_content_metadata_returns_none_when_the_ld_json_is_invalid(
    source_service, tmp_path: Path
):
    # Arrange
    content_file = tmp_path / "post.html"
    _write_ld_json(content_file, "{not valid json")

    # Act
    metadata = source_service.extract_content_metadata(file_path=str(content_file))

    # Assert
    assert_that(metadata).is_none()


def test_collect_content_metadata_filters_out_ignored_types(
    source_service, tmp_path: Path
):
    # Arrange
    post_file = tmp_path / "post.html"
    _write_ld_json(post_file, '{"@type": "Post", "title": "A Post"}')
    page_file = tmp_path / "page.html"
    _write_ld_json(page_file, '{"@type": "Page", "title": "A Page"}')

    # Act
    content_entries = source_service.collect_content_metadata(
        file_paths=[str(post_file), str(page_file)], ignoring_types=["page"]
    )

    # Assert
    assert_that(content_entries).is_length(1)
    assert_that(content_entries[0]["title"]).is_equal_to("A Post")


def test_collect_content_metadata_skips_files_without_metadata(
    source_service, tmp_path: Path
):
    # Arrange
    post_file = tmp_path / "post.html"
    _write_ld_json(post_file, '{"@type": "Post", "title": "A Post"}')
    no_metadata_file = tmp_path / "no_metadata.html"
    no_metadata_file.write_text("<html><body>No metadata</body></html>")

    # Act
    content_entries = source_service.collect_content_metadata(
        file_paths=[str(post_file), str(no_metadata_file)], ignoring_types=[]
    )

    # Assert
    assert_that(content_entries).is_length(1)
    assert_that(content_entries[0]["title"]).is_equal_to("A Post")


def test_collect_content_metadata_returns_an_empty_list_for_no_files(source_service):
    # Act
    content_entries = source_service.collect_content_metadata(
        file_paths=[], ignoring_types=[]
    )

    # Assert
    assert_that(content_entries).is_empty()
