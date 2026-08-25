from unittest.mock import create_autospec

import pytest
from assertpy import assert_that

from vox.service.file_system_service import FileSystemService
from vox.service.http_server_service import HTTPServerService
from vox.service.preview_service import PreviewService


@pytest.fixture
def file_system_service():
    return create_autospec(FileSystemService, instance=True)


@pytest.fixture
def http_server_service():
    return create_autospec(HTTPServerService, instance=True)


@pytest.fixture
def preview_service(file_system_service, http_server_service):
    return PreviewService(file_system_service, http_server_service)


def test_start_preview_mode_serves_the_received_content_folder_unchanged(
    preview_service, http_server_service
):
    # Arrange
    content_folder = "output"
    tcp_port = 9000

    # Act
    preview_service.start_preview_mode(
        watch_file_list=["source.md"],
        on_change=lambda: None,
        content_folder=content_folder,
        tcp_port=tcp_port,
    )

    # Assert
    assert_that(http_server_service.serve_content.call_args.kwargs).is_equal_to(
        {"content_folder": content_folder, "server_port": tcp_port}
    )


def test_start_preview_mode_watches_the_received_file_list(
    preview_service, file_system_service
):
    # Arrange
    watch_file_list = ["source.md", "settings.yaml"]
    on_change = lambda: None

    # Act
    preview_service.start_preview_mode(
        watch_file_list=watch_file_list,
        on_change=on_change,
        content_folder="output",
        tcp_port=9000,
    )

    # Assert
    assert_that(file_system_service.watch_for_changes_on.call_args.kwargs).is_equal_to(
        {"watch_list": watch_file_list, "on_change": on_change}
    )
