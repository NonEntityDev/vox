import logging
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from logging import Logger


class HTTPServerService:
    def __init__(self) -> None:
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)

    def serve_content(
        self, content_folder: str, server_port: int = 7890
    ) -> ThreadingHTTPServer:
        self.__logger.info(
            "Provinding web static content from folder '%s' on http://localhost:%s...",
            content_folder,
            server_port,
        )

        def handler(*args, **kwargs):
            return SimpleHTTPRequestHandler(*args, directory=content_folder, **kwargs)

        return ThreadingHTTPServer(("localhost", server_port), handler)
