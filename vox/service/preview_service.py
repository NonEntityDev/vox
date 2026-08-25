from http.server import ThreadingHTTPServer
from logging import Logger
import logging
from threading import Thread
from typing import Callable

from vox.service.file_system_service import FileSystemService
from vox.service.http_server_service import HTTPServerService


class PreviewService:

    def __init__(self, file_system_service: FileSystemService, http_server_service: HTTPServerService):
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)
        self.__file_system_service: FileSystemService = file_system_service
        self.__http_server_service: HTTPServerService = http_server_service

    def start_preview_mode(self,
                           watch_file_list: list[str],
                           on_change: Callable[..., None],
                           content_folder: str,
                           tcp_port: int | None = 7890):
        self.__logger.info("Starting preview mode...")
        observer = self.__file_system_service.watch_for_changes_on(
            watch_list=watch_file_list,
            on_change=on_change
        )

        server: ThreadingHTTPServer = self.__http_server_service.serve_content(
            content_folder=content_folder,
            server_port=tcp_port
        )

        server_thread: Thread = Thread(
            target=server.serve_forever,
            daemon=True
        )
        server_thread.start()

        try:
            observer.join()

        finally:
            self.__logger.info("Stopping preview mode...")
            observer.stop()
            observer.join()
            server.shutdown()
            server.server_close()
