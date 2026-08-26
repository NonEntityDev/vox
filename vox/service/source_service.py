import logging
from logging import Logger
from typing import Any

import frontmatter
import typer
from frontmatter import Post
from markdown import markdown


class SourceService:
    """Handles everything necessary to fetch and render the content from a FrontMatter
    source file."""

    def __init__(self) -> None:
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)

    def fetch_and_render_from(self, path: str) -> dict[str, Any]:
        """
        Reads the content of a FrontMatter file, parses it, renders its markdown content
        into HTML and returns a dictionary composed by the parsed FrontMatter metadata
        section and the rendered markdown content in the "content" entry of the
        dictionary.

        Parameters:
            path (str): Path to the FrontMatter source file to be read and rendered.

        Returns:
            dict[str, Any]: A dictionary containing the parsed FrontMatter metadata
                section and an addition entry with "content" as key and the markdown
                rendered content as value.
        """

        try:
            self.__logger.info(
                "Fetching and rendering content from source file '%s'...", path
            )
            document: Post = frontmatter.load(path)

        except Exception as ex:
            self.__logger.error(
                "It was not possible to fetch the souce file from '%s' due the "
                "following error: %s",
                path,
                str(ex),
            )
            self.__logger.debug("Error details:", exc_info=True)
            raise typer.Abort(-1) from ex

        try:
            self.__logger.info("Rendering content from source file '%s'...", path)
            content: str = markdown(
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

        except Exception as ex:
            self.__logger.error(
                "It was not possible to render the content of source file '%s' due "
                "the following error: %s",
                path,
                str(ex),
            )
            self.__logger.debug("Error details:", exc_info=True)
            raise typer.Abort(-1) from ex

        return {**document.metadata, "content": content}
