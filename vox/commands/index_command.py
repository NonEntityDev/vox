import logging
from logging import Logger
from typing import Annotated, Any

import typer

from vox.service.file_system_service import FileSystemService
from vox.service.pagination_service import PaginationService
from vox.service.settings_service import SettingsService
from vox.service.source_service import SourceService
from vox.service.template_service import TemplateService


def prepare_index_command(app: typer.Typer):
    """Prepares a typer command to index the generated content."""

    logger: Logger = logging.getLogger(__name__)
    file_system_service: FileSystemService = FileSystemService()
    source_service: SourceService = SourceService()
    template_service: TemplateService = TemplateService()
    settings_service: SettingsService = SettingsService()
    pagination_service: PaginationService = PaginationService()

    @app.command()
    def index(  # noqa: PLR0913, PLR0917 - Typer commands are naturally option-heavy.
        source: Annotated[
            str,
            typer.Option(
                help="Path to the folder containing the generated content to be "
                "indexed."
            ),
        ],
        target: Annotated[
            str,
            typer.Option(
                help="Path to the target folder where the generated index page will "
                "be saved."
            ),
        ],
        items_per_page: Annotated[
            int,
            typer.Option(
                help="Optional number of items listed per index page. Default: 10"
            ),
        ] = 10,
        max_pages: Annotated[
            int,
            typer.Option(
                help="Optional max number of pages to be generated. Default: 0 (no "
                "max limit)"
            ),
        ] = 0,
        theme: Annotated[
            str,
            typer.Option(
                help="Optional path to the folder containing the theme to generate "
                "the index page. Default: ./theme"
            ),
        ] = "./theme",
        template: Annotated[
            str,
            typer.Option(
                help="Optional template name file to be used. Default: index.html"
            ),
        ] = "index",
        ignore_types: Annotated[
            str,
            typer.Option(
                help="Optional comma separated string with types of content to not "
                "be indexed. Default: page"
            ),
        ] = "page",
        sort_by: Annotated[
            str,
            typer.Option(
                help="Optional name of the field to be used to sort the indexed "
                "content. Default: datePublished"
            ),
        ] = "datePublished",
        sort_direction: Annotated[
            str,
            typer.Option(
                help="Optional sorting direction to be applied to the indexed "
                "content. Default: desc"
            ),
        ] = "desc",
        settings: Annotated[
            str, typer.Option(help="Optional path to the settings file.")
        ] = "./settings.yaml",
    ):
        """
        Indexes the generated contend and produces a paginated index page.
        """

        logger.info("Generating index for the available content...")
        logger.debug("Source folder: %s", source)
        logger.debug("Target folder: %s", target)
        logger.debug("Items per page: %s", items_per_page)
        logger.debug("Max pages: %s", max_pages)
        logger.debug("Theme folder path: %s", theme)
        logger.debug("Template file to be used: %s", template)
        logger.debug("Ignored types: %s", ignore_types)
        logger.debug("Sort by: %s", sort_by)
        logger.debug("Sort direction: %s", sort_direction)
        logger.debug("Settings file path: %s", settings)

        # Converting list of types to ignore to a list.
        ignoring_types: list[str] = [
            type.lower().strip() for type in ignore_types.split(",")
        ]

        # List and collect the metadata of all static content from the source folder.
        files_to_index: list[str] = file_system_service.list_files_from(
            folder_path=source, pattern="*.html"
        )
        content_entries: list[dict[str, Any]] = source_service.collect_content_metadata(
            file_paths=files_to_index, ignoring_types=ignoring_types
        )

        pages: list[dict[str, Any]] = pagination_service.paginate_content(
            content=content_entries,
            page_size=items_per_page,
            max_pages=max_pages,
            sort_by=sort_by,
            reverse=sort_direction.lower().strip() == "desc",
            template_name=template,
        )
        settings_parameters: dict[str, Any] = settings_service.fetch_from(settings)

        for page in pages:
            context: dict[str, Any] = {**page, "settings": settings_parameters}
            logger.info("Context: %s", str(context))

            final_content: str = template_service.render_using_theme(
                theme_path=theme, context=context, template_name=f"{template}.html"
            )
            file_system_service.write_to_file(
                path=f"{target}/{page['pagination']['current_page']}",
                content=final_content,
            )
