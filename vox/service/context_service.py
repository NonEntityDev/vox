import logging
from logging import Logger
from pathlib import PurePosixPath
from typing import Any

import typer


class ContextService:
    """Handles the preparing of the context provided to generate the final content."""

    def __init__(self) -> None:
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)

    def prepare_context(
        self,
        source_content: dict[str, Any],
        settings_content: dict[str, Any],
        informed_content_type: str,
        target_path: str,
    ) -> dict[str, Any]:

        self.__logger.info("Preparing the data context to render the final content...")
        content_type: str = self.infer_content_type(
            informed_content_type=informed_content_type, source_content=source_content
        )

        relative_path, permalink_path = self.infer_content_url(
            target_path=target_path, settings_content=settings_content
        )

        return {
            "content": {
                **source_content,
                "type": content_type,
                "relative_path": relative_path,
                "permalink_path": permalink_path,
            },
            "settings": settings_content,
        }

    def infer_content_type(
        self, informed_content_type: str, source_content: dict[str, Any]
    ) -> str:
        self.__logger.info("Infering the proper content type...")
        content_type: str | None = (
            informed_content_type
            if informed_content_type
            else None or source_content.get("type")
        )

        if not content_type:
            self.__logger.error(
                "The content type should be either informed using the 'content-type' "
                "argument or the 'type' parameter in the source file."
            )
            raise typer.Abort(-1)

        return content_type

    def infer_content_url(
        self, target_path: str, settings_content: dict[str, Any]
    ) -> tuple[str, str]:
        self.__logger.info("Infering the content url...")
        final_path: PurePosixPath = PurePosixPath(target_path)
        relative_path: str = f"/{PurePosixPath(*final_path.parts[2:])!s}"
        permalink_path: str = f"{settings_content.get('baseUrl', '')}{relative_path}"
        return relative_path, permalink_path
