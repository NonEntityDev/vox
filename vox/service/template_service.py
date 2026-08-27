import logging
from logging import Logger
from typing import Any

import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateService:
    """
    Provides an abstract and high-level way to interact with the template engine used
    to render the final content.
    """

    __theme_path: str = None
    __environment: Environment = None

    def __init__(self) -> None:
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)

    def render_using_theme(self, theme_path: str, context: dict[str, Any]) -> str:
        """
        Renders the final content based on the theme to be used and the context. The
        theme template to be used is infered based on the the "type" entry in the
        received context.

        Parameters:
            theme (str): Path to the folder containing the theme to be used.
            context (dict[str, Any]): Dictionary containing all the details required
                to properly render the final content.

        Return:
            str: Final content.
        """
        self.__logger.info(
            "Rendering final content using theme from '%s'...", theme_path
        )
        if not self.__theme_path or self.__theme_path != theme_path:
            self.__theme_path: str = theme_path
            self.__environment: Environment = Environment(
                loader=FileSystemLoader(theme_path), autoescape=select_autoescape()
            )

        template_name: str = f"{context['content']['type']}.html"
        try:
            self.__logger.info("Applying '%s' template...", template_name)
            return self.__environment.get_template(template_name).render(**context)

        except Exception as ex:
            self.__logger.error(
                "It was not possible to render the final content using the template "
                "'%s' of theme '%s' due the following error: %s",
                template_name,
                theme_path,
                str(ex),
            )
            self.__logger.debug("Error details:", exc_info=True)
            raise typer.Abort(-1) from ex
