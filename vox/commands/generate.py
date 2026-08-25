import frontmatter
import logging
import typer
import yaml

from logging import Logger
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown import markdown
from typing import Annotated, Any


def prepare_generate_command(app: typer.Typer):

    logger: Logger = logging.getLogger(__name__)

    @app.command()
    def generate(
        source: Annotated[
            str, typer.Option(help="Path to the source FrontMatter document.")
        ],
        target: Annotated[
            str, typer.Option(help="Target path to the final static page.")
        ],
        content_type: Annotated[
            str, typer.Option(help="Optional content type being generated.")
        ] = "none",
        theme: Annotated[
            str, typer.Option(help="Optional path to the theme folder.")
        ] = "./theme",
        settings: Annotated[
            str, typer.Option(help="Optional path to the settings file.")
        ] = "./settings.yaml",
    ):
        """
        Generates a static web page based by combining a FrontMatter document, a Jinja2 template
        and optionally additional parameters from a YAML settings file.
        """
        logger.info("Generating content for source '%s'...", source)

        logger.debug("Source file: %s", source)
        logger.debug("Target path: %s", target)
        logger.debug("Theme path: %s", theme)
        logger.debug("Content type: %s", content_type)
        logger.debug("Settings file path: %s", settings)

        # Loads the FrontMatter source file.
        try:
            source_content = frontmatter.load(source)

        except FileNotFoundError:
            logger.error("The source file '%s' could not be found.", source)
            raise typer.Exit(-1)

        except Exception as ex:
            logger.error(
                "It was not possible to open the source file '%s' due the following error: %s",
                source,
                str(ex),
                exc_info=True,
            )
            raise typer.Exit(-1)

        # Validate if either source file type or content type are defined.
        source_content_type: str | None = (
            str(source_content["type"]) if "type" in source_content.keys() else None
        )
        override_content_type: str | None = (
            None if content_type.lower().strip() == "none" else content_type
        )

        if not source_content_type and not override_content_type:
            logger.error(
                "The content type must be either defined as a parameter of the source file or defined in the command line."
            )
            raise typer.Exit(-1)

        elif override_content_type:
            source_content_type = override_content_type

        # Try to load the settings file.
        settings_attributes = {}
        try:
            with open(settings, "r") as settings_file:
                settings_attributes = yaml.safe_load(settings_file)

        except FileNotFoundError:
            logger.warning("Settings file not found on '%s' path.", settings)

        except Exception as ex:
            logger.error(
                "It was not possible to load the settings file from '%s' path due the following error: %s",
                settings,
                str(ex),
                exc_info=True,
            )
            raise typer.Exit(-1)

        # Preparing context.
        context: dict[str, Any] = {}
        context["content"] = source_content.metadata
        context["content"]["type"] = source_content_type
        context["settings"] = settings_attributes

        # Generating source content.
        source_raw_html: str = markdown(
            source_content.content,
            extensions=[
                "abbr",
                "attr_list",
                "fenced_code",
                "footnotes",
                "md_in_html",
                "tables",
                "admonition",
                "codehilite",
                "legacy_attrs",
                "legacy_em",
                "meta",
                "sane_lists",
                "smarty",
                "toc",
                "wikilinks",
            ],
        )
        context["content"]["body"] = source_raw_html

        # Initialize template engine with theme path.
        template_environment: Environment = Environment(
            loader=FileSystemLoader(theme), autoescape=select_autoescape()
        )

        # Loading the template based on the content type.
        try:
            template_name: str = f"{source_content_type}.html"
            template = template_environment.get_template(template_name)

        except Exception as ex:
            logger.error(
                "It was not possible to load the template '%s' from '%s' path due the following error: %s",
                template_name,
                theme,
                str(ex),
                exc_info=True,
            )
            raise typer.Abort(-1)

        # Generate final content.
        try:
            logger.info("Writting content on '%s'...", target)
            with open(target, "w") as target_file:
                target_file.writelines(template.render(**context))
                target_file.flush()

        except Exception as ex:
            logger.error(
                "It was not possible to write the resulting content on '%s' path due the following error: %s",
                target,
                str(ex),
                exc_info=True,
            )
            raise typer.Abort(-1)

        logger.info("Content successfully on '%s'.", target)
