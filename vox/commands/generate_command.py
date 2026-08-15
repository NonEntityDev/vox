import logging
import typer

from logging import Logger
from typing import Annotated, Any

from vox.service.frontmatter_service import FrontMatterService
from vox.service.jinja2_template_service import Jinja2TemplateService
from vox.service.yaml_service import YAMLService


def prepare_generate_command(app: typer.Typer):

    logger: Logger = logging.getLogger(__name__)

    @app.command()
    def generate(source: Annotated[str, typer.Option(help = "Path to the source FrontMatter document.")],
                 target: Annotated[str, typer.Option(help = "Target path to the final static page.")],
                 content_type: Annotated[str, typer.Option(help = "Optional content type being generated.")] = "",
                 theme: Annotated[str, typer.Option(help = "Optional path to the theme folder.")] = "./theme",
                 settings: Annotated[str, typer.Option(help = "Optional path to the settings file.")] = "./settings.yaml"):
        """
        Generates a static web page based by combining a FrontMatter document, a Jinja2 template
        and optionally additional parameters from a YAML settings file.
        """
        logger.info("Generating content...")

        logger.debug("Source file: %s", source)
        logger.debug("Target path: %s", target)
        logger.debug("Theme path: %s", theme)
        logger.debug("Content type: %s", content_type)
        logger.debug("Settings file path: %s", settings)

        # Loads the FrontMatter source file.
        try:
            source_document: dict[str, Any] = FrontMatterService.load_and_render_from(source)

        except FileNotFoundError:
            logger.error("The source file '%s' could not be found.", source)
            raise typer.Exit(-1)

        except Exception as ex:
            logger.error("It was not possible to open the source file '%s' due the following error: %s", source, str(ex), exc_info=True)
            raise typer.Exit(-1)

        # Validate if either source file type or content type are defined.
        source_content_type:str | None = source_document.get("type", None)
        override_content_type: str | None = None if not content_type else content_type

        source_content_type = override_content_type or source_content_type
        if not source_content_type:
            logger.error("The content type must be either defined as a parameter of the source file or defined in the command line.")
            raise typer.Exit(-1)

        # Try to load the settings file.
        try:
            settings_attributes: dict[str, Any] = YAMLService.load_from(settings)

        except Exception as ex:
            logger.error("It was not possible to load the settings file from '%s' path due the following error: %s", settings, str(ex), exc_info=True)
            raise typer.Exit(-1)

        # Preparing context.
        context: dict[str, Any] = {}
        context["content"] = source_document
        context["content"]["type"] = source_content_type
        context["settings"] = settings_attributes

        # Rendering the final content.
        template_service: Jinja2TemplateService = Jinja2TemplateService(theme)
        template_name: str = f"{source_content_type}.html"

        try:
            final_content: str = template_service.render_content_using_template(
                template_name=template_name,
                context=context
            )

        except Exception as ex:
            logger.error("It was not possible to render the final content using the template '%s' from theme '%s' due the following error: %s", template_name, theme, str(ex), exc_info=True)
            raise typer.Abort(-1)

        # Saving the final content to the target file.
        try:
            logger.info("Writting content on '%s'...", target)
            with open(target, "w") as target_file:
                target_file.writelines(final_content)
                target_file.flush()

        except Exception as ex:
            logger.error("It was not possible to write the resulting content on '%s' path due the following error: %s", target, str(ex), exc_info=True)
            raise typer.Abort(-1)

        logger.info("Content successfully on '%s'.", target)
