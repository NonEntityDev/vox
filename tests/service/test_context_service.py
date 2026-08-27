import pytest
import typer
from assertpy import assert_that

from vox.service.context_service import ContextService


@pytest.fixture
def context_service():
    return ContextService()


def test_infer_content_type_prefers_the_informed_content_type(context_service):
    # Arrange
    source_content = {"type": "page"}

    # Act
    content_type = context_service.infer_content_type(
        informed_content_type="post", source_content=source_content
    )

    # Assert
    assert_that(content_type).is_equal_to("post")


def test_infer_content_type_falls_back_to_the_source_content_type(context_service):
    # Arrange
    source_content = {"type": "page"}

    # Act
    content_type = context_service.infer_content_type(
        informed_content_type="", source_content=source_content
    )

    # Assert
    assert_that(content_type).is_equal_to("page")


def test_infer_content_type_aborts_when_no_content_type_is_available(context_service):
    # Arrange
    source_content = {}

    # Act / Assert
    with pytest.raises(typer.Abort):
        context_service.infer_content_type(
            informed_content_type="", source_content=source_content
        )


def test_prepare_context_combines_source_content_type_and_url_and_settings(
    context_service,
):
    # Arrange
    source_content = {
        "type": "post",
        "title": "Hello World",
        "relative_path": "/blog/post.html",
    }
    settings_content = {"baseUrl": "https://example.com"}
    target_path = "/target/blog/post.html"

    # Act
    context = context_service.prepare_context(
        source_content=source_content,
        settings_content=settings_content,
        informed_content_type="",
        target_path=target_path,
    )

    # Assert
    assert_that(context).is_equal_to(
        {
            "content": {
                "type": "post",
                "title": "Hello World",
                "relative_path": "/blog/post.html",
                "permalink_path": "https://example.com/blog/post.html",
            },
            "settings": settings_content,
        }
    )
