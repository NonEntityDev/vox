from logging import Logger
import logging
import yaml
from typing import Any


logger: Logger = logging.getLogger(__name__)

class YAMLService:
    """Provides high level access and abstract access to YAML content."""

    @staticmethod
    def load_from(path: str) -> dict[str, Any]:
        """
        Deserialize an YAML file into a dictionary. If the file was not found,
        returns an empty dictionary.

        Parameters:
            path (str): Path to the YAML to be deserialized.

        Return:
            result (dict[str, Any]): Either a dictionary containing the deserialized
            YAML properties or an empty dictionary when the YAML file to be
            deserialized was not found.
        """
        logger.info("Loading YAML parameters from file '%s'...", path)
        result: dict[str, Any] = {}

        try:
            with open(path, "r") as yaml_file:
                result = yaml.safe_load(yaml_file)

        except FileNotFoundError:
            logger.warning("Settings file '%s' not found. Proceeding anyway.", path)

        except Exception as ex:
            raise ex

        return result
