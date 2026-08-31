import logging
from logging import Logger
from pathlib import Path
from typing import Any

import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateService:
    """
    Provides an abstract and high-level way to interact with the template engine used
    to render the final content.
    """

    def __init__(self) -> None:
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)
        self.__theme_path: str | None = None
        self.__environment: Environment | None = None

    def render_using_theme(
        self,
        theme_path: str,
        context: dict[str, Any],
        template_name: str | None = None,
    ) -> str:
        """
        Renders the final content based on the theme to be used and the context. The
        theme template to be used is infered based on the the "type" entry in the
        received context.

        Parameters:
            theme (str): Path to the folder containing the theme to be used.
            context (dict[str, Any]): Dictionary containing all the details required
                to properly render the final content.
            template_name (str | None): Optional name of the template within the theme
                to be used. If not provided, the template name will be inferred by the
                content type if available. Default: None

        Return:
            str: Final content.
        """
        self.__logger.info(
            "Rendering final content using theme from '%s'...", theme_path
        )
        environment: Environment = self.__environment_for(theme_path)

        template_file_name: str = self.resolve_template_file_name(
            context=context, template_name=template_name
        )

        try:
            self.__logger.info("Applying '%s' template...", template_file_name)
            return environment.get_template(template_file_name).render(**context)

        except Exception as ex:
            self.__logger.error(
                "It was not possible to render the final content using the template "
                "'%s' of theme '%s' due the following error: %s",
                template_file_name,
                theme_path,
                str(ex),
            )
            self.__logger.debug("Error details:", exc_info=True)
            raise typer.Abort(-1) from ex

    def resolve_template_file_name(
        self, context: dict[str, Any], template_name: str | None = None
    ) -> str:
        """
        Resolves the theme template file to be used to render the given context.

        When `template_name` is provided, it is used as-is. Otherwise the template
        file name is inferred from the content "type", using the same extension as
        the content's own "relative_path" target (falling back to ".html" when the
        context carries no "relative_path"), so the by-convention template a piece
        of content is rendered with matches the extension it is written to.

        Parameters:
            context (dict[str, Any]): Rendering context, expected to include a
                "content" entry with a "type" and, optionally, a "relative_path".
            template_name (str | None): Optional explicit template file name.
                Default: None.

        Return:
            str: The template file name to look up within the theme.
        """
        if template_name:
            return template_name

        content: dict[str, Any] = context["content"]
        relative_path: str = content.get("relative_path", "")
        extension: str = Path(relative_path).suffix or ".html"
        return f"{content['type']}{extension}"

    def __environment_for(self, theme_path: str) -> Environment:
        """
        Returns the Jinja2 environment for the received theme path, reusing the
        previously built one whenever the theme path has not changed.
        """
        if self.__environment is None or self.__theme_path != theme_path:
            self.__theme_path = theme_path
            self.__environment = Environment(
                loader=FileSystemLoader(theme_path), autoescape=select_autoescape()
            )

        return self.__environment
