import logging
from logging import Logger
from pathlib import PurePosixPath
from typing import Annotated, Any

import typer

from vox.service.context_service import ContextService
from vox.service.file_system_service import FileSystemService
from vox.service.http_server_service import HTTPServerService
from vox.service.preview_service import PreviewService
from vox.service.settings_service import SettingsService
from vox.service.source_service import SourceService
from vox.service.template_service import TemplateService


def prepare_generate_command(app: typer.Typer):
    """Prepares a typer command to execute the generate static content logic."""

    logger: Logger = logging.getLogger(__name__)
    source_service: SourceService = SourceService()
    settings_service: SettingsService = SettingsService()
    context_service: ContextService = ContextService()
    template_service: TemplateService = TemplateService()
    file_system_service: FileSystemService = FileSystemService()
    http_server_service: HTTPServerService = HTTPServerService()
    preview_service: PreviewService = PreviewService(
        file_system_service=file_system_service,
        http_server_service=http_server_service,
    )

    @app.command()
    def generate(  # noqa: PLR0913, PLR0917 - Typer commands are naturally option-heavy.
        source: Annotated[
            str, typer.Option(help="Path to the source FrontMatter document.")
        ],
        target: Annotated[
            str, typer.Option(help="Target path to the final static page.")
        ],
        content_type: Annotated[
            str, typer.Option(help="Optional content type being generated.")
        ] = "",
        theme: Annotated[
            str, typer.Option(help="Optional path to the theme folder.")
        ] = "./theme",
        settings: Annotated[
            str, typer.Option(help="Optional path to the settings file.")
        ] = "./settings.yaml",
        preview: Annotated[bool, typer.Option("--preview")] = False,
        server_port: Annotated[
            int,
            typer.Option(
                help=(
                    "TCP port used to provide the live editing when the --preview "
                    "flag is provided"
                )
            ),
        ] = 8000,
    ):
        """
        Generates a static web page based by combining a FrontMatter document, a Jinja2
        template and optionally additional parameters from a YAML settings file.

        Parameters:
            source (str): Path to the FrontMatter document to be used to generate the
                target static content.
            target (str): Final path for the static generated content.
            content_type (str): Optional type of the content being generated. Overrides
                the type propery in the FrontMatter document.
            theme (str): Optional path to the folder containing the theme to be used to
                generate the static content. Default: ./theme
            settings (str): Optional path to a yaml file containing additional
                parameters to help to generate the static content. Default:
                ./settings.yaml. The process will not fail if this file were not found.
            preview (bool): Optional flag that starts a web-server to provide the
                content of the root of the target folder and automatically rebuild when
                either the source file or the user theme file were changed.
                Default: false
            server_port (int): Optional argument to set the TCP port where the live
                preview web server will be listening to. Default: 8000
        """
        logger.info("Generating content...")
        logger.debug("Source file: %s", source)
        logger.debug("Target path: %s", target)
        logger.debug("Theme path: %s", theme)
        logger.debug("Content type: %s", content_type)
        logger.debug("Settings file path: %s", settings)
        logger.debug("Preview: %s", preview)
        logger.debug("Server port: %s", server_port)

        source_content: dict[str, Any] = source_service.fetch_and_render_from(
            path=source
        )

        settings_content: dict[str, Any] = settings_service.fetch_from(path=settings)

        context: dict[str, Any] = context_service.prepare_context(
            source_content=source_content,
            settings_content=settings_content,
            informed_content_type=content_type,
            target_path=target,
        )

        final_content: str = template_service.render_using_theme(
            theme_path=theme, context=context
        )

        file_system_service.write_to_file(path=target, content=final_content)

        logger.info("Content successfully generated on '%s'.", target)

        # Starts the live preview mode.
        if preview:
            target_root_path: PurePosixPath = PurePosixPath(target).parent
            logger.info(
                "Providing live preview of directory '%s' on 'http://localhost:%s'...",
                str(target_root_path),
                server_port,
            )

            files_watch_list: list[str] = [
                source,
                settings,
                f"{theme}/{context['content']['type']}.html",
            ]
            preview_service.start_preview_mode(
                watch_file_list=files_watch_list,
                on_change=lambda: generate(
                    source=source,
                    target=target,
                    settings=settings,
                    theme=theme,
                    preview=False,
                ),
                content_folder=str(target_root_path),
                tcp_port=server_port,
            )
