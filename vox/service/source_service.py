import json
import logging
from logging import Logger
from typing import Any

import frontmatter
import typer
from bs4 import BeautifulSoup
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

        return {**document.metadata, "body": content}

    def extract_content_metadata(self, file_path: str) -> dict[str, Any] | None:
        """
        Extracts the structured (ld+json) metadata embedded in a generated content
        file.

        Parameters:
            file_path (str): Path to the generated HTML file to extract metadata from.

        Return:
            dict[str, Any] | None: The parsed ld+json metadata, or None if the file has
                no ld+json block or its metadata could not be extracted.
        """
        self.__logger.info("Extracting metadata from file '%s'...", file_path)
        try:
            with open(file_path) as source_file_input:
                document: BeautifulSoup = BeautifulSoup(
                    source_file_input, "html.parser"
                )
                ld_json_blocks = document.find_all(type="application/ld+json")
                if not ld_json_blocks:
                    self.__logger.warning(
                        "File '%s' has no ld+json block. Ignoring...", file_path
                    )
                    return None

                self.__logger.debug("ld+json block: %s", ld_json_blocks[0].text)
                return json.loads(ld_json_blocks[0].text)

        except Exception as ex:
            self.__logger.warning(
                "It was not possible to extract metadata from file '%s' due the "
                "following error: %s",
                file_path,
                str(ex),
            )
            return None

    def collect_content_metadata(
        self, file_paths: list[str], ignoring_types: list[str]
    ) -> list[dict[str, Any]]:
        """
        Extracts the metadata of every received file and filters out entries whose
        content type is in the received list of types to ignore.

        Parameters:
            file_paths (list[str]): Paths to the generated HTML files to extract
                metadata from.
            ignoring_types (list[str]): Lowercased, stripped content types that should
                be excluded from the result.

        Return:
            list[dict[str, Any]]: Metadata of every file that has a ld+json block and
                whose content type is not in `ignoring_types`.
        """
        self.__logger.info("Collecting metadata from %s file(s)...", len(file_paths))
        content_entries: list[dict[str, Any]] = []

        for file_path in file_paths:
            self.__logger.info("Indexing file: %s", file_path)
            metadata: dict[str, Any] | None = self.extract_content_metadata(
                file_path=file_path
            )
            if not metadata:
                continue

            content_type: str = str(metadata["@type"]).lower().strip()
            if content_type in ignoring_types:
                self.__logger.warning(
                    "File '%s' is of type '%s'. Ignoring...", file_path, content_type
                )
                continue

            content_entries.append(metadata)

        return content_entries
