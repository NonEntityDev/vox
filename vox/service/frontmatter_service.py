from logging import Logger
import logging

import frontmatter
from markdown import markdown
from typing import Any

class FrontMatterService:
    """Provides high level and abstract access to handle FrontMatter documents."""

    def __init__(self):
        self.__logger: Logger = logging.getLogger(__name__)

    def load_and_render_from(self, path: str) -> dict[str, Any]:
        """
        Load properties and content from a FrontMatter document, renders the Markdown content and
        returns a dictionary with the loaded properties, the original content in the content
        entry and the markdown rendered content in the body entry.

        Parameters:
            path (str): Path to the FrontMatter document to be loaded and rendered.

        Returns:
            result (dict[str, Any]): A dictionary containing all the document metadata,
            plus, content entry containing the FrontMatter markdown content and the
            body entry containing the FrontMatter markdown content rendered.

        """
        self.__logger.info("Loading FrontMatter document from file '%s'...", path)
        document = frontmatter.load(path)

        result: dict[str, Any] = {}
        result = {**document.metadata}
        result["content"] = document.content

        self.__logger.info("Rendering FrontMatter document markdown content...")
        rendered_content: str = markdown(
            document.content,
            extensions=[
                "abbr",
                "attr_list",
                "fenced_code",
                "footnotes",
                "md_in_html",
                "tables",
                "admonition",
                "codehilite",
                "legacy_attrs",
                "legacy_em",
                "meta",
                "sane_lists",
                "smarty",
                "toc",
                "wikilinks",
            ],
        )
        result["body"] = rendered_content

        self.__logger.debug("FrontMatter document loaded structure: %s", str(result))
        return result
