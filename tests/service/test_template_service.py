from pathlib import Path

import pytest
import typer
from assertpy import assert_that

from vox.service.template_service import TemplateService


@pytest.fixture
def template_service():
    return TemplateService()


@pytest.fixture
def theme_folder(tmp_path: Path) -> Path:
    theme_path = tmp_path / "theme"
    theme_path.mkdir()
    (theme_path / "post.html").write_text("<h1>{{ content.title }}</h1>")
    return theme_path


def test_render_using_theme_renders_the_template_matching_the_content_type(
    template_service, theme_folder: Path
):
    # Arrange
    context = {"content": {"type": "post", "title": "Hello World"}}

    # Act
    result = template_service.render_using_theme(
        theme_path=str(theme_folder), context=context
    )

    # Assert
    assert_that(result).is_equal_to("<h1>Hello World</h1>")


def test_render_using_theme_reuses_the_environment_for_the_same_theme_path(
    template_service, theme_folder: Path
):
    # Arrange
    first_context = {"content": {"type": "post", "title": "First"}}
    second_context = {"content": {"type": "post", "title": "Second"}}

    # Act
    first_result = template_service.render_using_theme(
        theme_path=str(theme_folder), context=first_context
    )
    second_result = template_service.render_using_theme(
        theme_path=str(theme_folder), context=second_context
    )

    # Assert
    assert_that(first_result).is_equal_to("<h1>First</h1>")
    assert_that(second_result).is_equal_to("<h1>Second</h1>")


def test_render_using_theme_switches_environment_when_the_theme_path_changes(
    template_service, theme_folder: Path, tmp_path: Path
):
    # Arrange
    other_theme_path = tmp_path / "other_theme"
    other_theme_path.mkdir()
    (other_theme_path / "post.html").write_text(
        "<article>{{ content.title }}</article>"
    )
    context = {"content": {"type": "post", "title": "Hello World"}}

    # Act
    template_service.render_using_theme(theme_path=str(theme_folder), context=context)
    result = template_service.render_using_theme(
        theme_path=str(other_theme_path), context=context
    )

    # Assert
    assert_that(result).is_equal_to("<article>Hello World</article>")


def test_render_using_theme_uses_the_explicit_template_name_when_provided(
    template_service, theme_folder: Path
):
    # Arrange
    (theme_folder / "index.html").write_text("<ul>{{ items | length }}</ul>")
    context = {"content": {"type": "post"}, "items": [1, 2, 3]}

    # Act
    result = template_service.render_using_theme(
        theme_path=str(theme_folder), context=context, template_name="index.html"
    )

    # Assert
    assert_that(result).is_equal_to("<ul>3</ul>")


def test_render_using_theme_aborts_when_the_template_is_missing(
    template_service, theme_folder: Path
):
    # Arrange
    context = {"content": {"type": "missing"}}

    # Act / Assert
    with pytest.raises(typer.Abort):
        template_service.render_using_theme(
            theme_path=str(theme_folder), context=context
        )
