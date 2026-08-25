from logging import Logger
import logging
import typer
import yaml
from typing import Any


class SettingsService:
    """Provides an abstract and high-level way to access and parse settings files."""

    def __init__(self):
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)

    def fetch_from(self, path:str) -> dict[str, Any]:
        try:
            self.__logger.info("Fetching settings from file '%s'...", path)
            with open(path, "r") as settings_file:
                return yaml.safe_load(settings_file)

        except FileNotFoundError:
            self.__logger.warning("Setting file not found on '%s'. Proceeding without it...", path)
            return {}

        except Exception as ex:
            self.__logger.error("It was not fetch settings from file '%s' due the following error: %s", path, str(ex))
            self.__logger.debug("Erro details:", exc_info=True)
            raise typer.Abort(-1)
