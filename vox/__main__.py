import logging
import os
from logging import Logger

import typer

from vox.commands.generate_command import prepare_generate_command

if __name__ == "__main__":
    # Initializing the application logging.
    logging_level_name: str = os.environ.get("VOX.LOGGING.LEVEL", "INFO")
    logging_level = logging.getLevelNamesMapping().get(logging_level_name.upper())

    logging.basicConfig(level=logging_level, format="%(levelname)s: %(message)s")
    logger: Logger = logging.getLogger(__name__)
    logger.info("Starting vox...")

    app: typer.Typer = typer.Typer()
    prepare_generate_command(app)

    app()
