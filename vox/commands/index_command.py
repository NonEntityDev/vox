import logging
from glob import glob
from logging import Logger
from typing import Annotated

import typer


def prepare_index_command(app: typer.Typer):
    """Prepares a typer command to index the generated content."""

    logger: Logger = logging.getLogger(__name__)

    @app.command()
    def index(
        source: Annotated[
            str,
            typer.Option(
                help="Path to the folder containing the generated content to be indexed."
            ),
        ],
        target: Annotated[
            str,
            typer.Option(
                help="Path to the target folder where the generated index page will be saved."
            ),
        ],
        items_per_page: Annotated[
            int,
            typer.Option(
                help="Optional number of items listed per index page. Default: 10"
            ),
        ] = 10,
        theme: Annotated[
            str,
            typer.Option(
                help="Optional path to the folder containing the theme to generate the index page. Default: ./theme"
            ),
        ] = "./theme",
        template: Annotated[
            str,
            typer.Option(
                help="Optional template name file to be used. Default: index.html"
            ),
        ] = "index.html",
        ignore_types: Annotated[
            str,
            typer.Option(
                help="Optional comma separated string with types of content to not be indexed. Default: page"
            ),
        ] = "page",
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
        logger.debug("Theme folder path: %s", theme)
        logger.debug("Template file to be used: %s", template)
        logger.debug("Ignored types: %s", ignore_types)
        logger.debug("Settings file path: %s", settings)

        # List all static content from the source file.
        for source_file in glob(f"{source}/**/*.html", recursive=True):
            logger.info("File: %s", source_file)
