from vox.service.frontmatter_service import FrontMatterService
from assertpy import assert_that, fail
from typing import Any


def test_file_not_found():
    try:
        FrontMatterService.load_and_render_from("not_found.md")
        fail("A FileNotFoundError was expected by this test case.")

    except FileNotFoundError as ex:
        assert_that(str(ex)).contains("No such file or directory: 'not_found.md'")

    except Exception as ex:
        fail(f"An unexpected exception occurred: {str(ex)}")


def test_parse_render_file():
    result: dict[str, Any] = FrontMatterService.load_and_render_from(
        "tests/resources/valid_frontmatter.md"
    )
    assert_that(result["title"]).is_equal_to("Valid FrontMatter document.")
    assert_that(result["content"]).is_equal_to("# Hello World!")
    assert_that(result["body"]).is_equal_to('<h1 id="hello-world">Hello World!</h1>')
