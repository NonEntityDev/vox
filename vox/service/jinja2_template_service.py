from logging import Logger
import logging
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

logger: Logger = logging.getLogger(__name__)


class Jinja2TemplateService:

    def __init__(self, theme_path: str):
        logger.info(
            "Initializing Jinja2 template environment using '%s' path...", theme_path
        )
        self.__environment: Environment = Environment(
            loader=FileSystemLoader(theme_path), autoescape=select_autoescape()
        )

    def render_content_using_template(
        self, template_name: str, context: dict[str, Any]
    ) -> str:
        logger.info("Rendering content using template '%s'...", template_name)
        template: Template = self.__environment.get_template(template_name)
        return template.render(**context)
