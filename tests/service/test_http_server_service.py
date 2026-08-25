from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.request import urlopen

import pytest
from assertpy import assert_that

from vox.service.http_server_service import HTTPServerService


@pytest.fixture
def http_server_service():
    return HTTPServerService()


@pytest.fixture
def content_folder(tmp_path: Path) -> Path:
    (tmp_path / "index.html").write_text("<h1>Hello World</h1>")
    return tmp_path


def test_serve_content_serves_files_from_the_received_folder(
    http_server_service, content_folder: Path
):
    # Arrange
    server: ThreadingHTTPServer = http_server_service.serve_content(
        content_folder=str(content_folder), server_port=0
    )
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        # Act
        port = server.server_address[1]
        with urlopen(f"http://localhost:{port}/index.html") as response:
            body = response.read().decode("UTF-8")

        # Assert
        assert_that(body).is_equal_to("<h1>Hello World</h1>")

    finally:
        server.shutdown()
        server.server_close()
        server_thread.join()
