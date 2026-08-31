import logging
from logging import Logger
from pathlib import Path
from typing import Any


class PaginationService:
    """Splits indexed content into ordered pages and prepares the pagination metadata
    needed to render and link between the generated index pages."""

    def __init__(self) -> None:
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)

    def paginate_content(  # noqa: PLR0913, PLR0917 - one argument per pagination knob.
        self,
        content: list[dict[str, Any]],
        page_size: int,
        max_pages: int,
        sort_by: str,
        reverse: bool,
        template_name: str,
    ) -> list[dict[str, Any]]:
        """
        Sorts the received content and splits it into pages, returning for each page a
        dictionary with its "items" and "pagination" metadata, ready to be merged into
        the rendering context.

        Parameters:
            content (list[dict[str, Any]]): Content entries to be paginated.
            page_size (int): Number of items per page.
            max_pages (int): Optional max number of pages to keep. 0 means no limit.
            sort_by (str): Name of the field used to sort the content.
            reverse (bool): Whether the content should be sorted in descending order.
            template_name (str): Base template name used to derive each page's target
                file name.

        Return:
            list[dict[str, Any]]: One entry per page, each with "items" (the page's
                content entries) and "pagination" (page metadata, including the file
                names of the previous/next/current page).
        """
        self.__logger.info("Paginating indexed content...")
        content.sort(reverse=reverse, key=lambda entry: entry[sort_by])

        pages: list[list[dict[str, Any]]] = [
            content[index : index + page_size]
            for index in range(0, len(content), page_size)
        ]

        if max_pages > 0:
            pages = pages[:max_pages]

        total_pages: int = len(pages)
        return [
            {
                "items": page,
                "pagination": self.__build_page_info(
                    page_index=page_index,
                    page=page,
                    total_pages=total_pages,
                    items_per_page=page_size,
                    template_name=template_name,
                ),
            }
            for page_index, page in enumerate(pages)
        ]

    def __build_page_info(
        self,
        page_index: int,
        page: list[dict[str, Any]],
        total_pages: int,
        items_per_page: int,
        template_name: str,
    ) -> dict[str, Any]:
        """Builds the pagination metadata for a single page, including the file names
        used to link to the previous and next pages."""
        return {
            "total_pages": total_pages,
            "page": page_index,
            "items_per_page": items_per_page,
            "total_items": len(page),
            "previous_page": (
                self.__page_file_name(template_name, page_index - 1)
                if page_index > 0
                else None
            ),
            "current_page": self.__page_file_name(template_name, page_index),
            "next_page": (
                self.__page_file_name(template_name, page_index + 1)
                if page_index < total_pages - 1
                else None
            ),
        }

    def __page_file_name(self, template_name: str, page_index: int) -> str:
        """The first page keeps the bare template name; every following page gets a
        "_page{n}" suffix. Either way, the extension is the one carried by
        `template_name`, defaulting to ".html" when it has none."""
        stem, extension = self.__split_template_name(template_name)
        if page_index == 0:
            return f"{stem}{extension}"
        return f"{stem}_page{page_index}{extension}"

    def template_file_name(self, template_name: str) -> str:
        """Normalizes a template name into the actual template file name: the stem
        and extension carried by `template_name`, defaulting to the ".html"
        extension when it has none. This is the file the theme's template engine
        should render, as opposed to `current_page`/`previous_page`/`next_page`,
        which name the paginated output files.

        Parameters:
            template_name (str): Template name to be normalized, e.g. "index" or
                "rss.xml".

        Return:
            str: The normalized template file name, e.g. "index.html" or "rss.xml".
        """
        stem, extension = self.__split_template_name(template_name)
        return f"{stem}{extension}"

    def __split_template_name(self, template_name: str) -> tuple[str, str]:
        """Splits a template name into its stem and extension, defaulting the
        extension to ".html" when the template name has none."""
        template_path: Path = Path(template_name)
        return template_path.stem, template_path.suffix or ".html"
