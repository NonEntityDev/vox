from pathlib import Path
from threading import Event

import pytest
import typer
from assertpy import assert_that
from watchdog.events import DirModifiedEvent, FileModifiedEvent

from vox.service.file_system_service import FileChangeHandler, FileSystemService


@pytest.fixture
def file_system_service():
    return FileSystemService()


def test_write_to_file_writes_the_content_to_the_target_path(tmp_path: Path):
    # Arrange
    file_system_service = FileSystemService()
    target_path = tmp_path / "output.html"

    # Act
    file_system_service.write_to_file(path=str(target_path), content="<h1>Hello</h1>")

    # Assert
    assert_that(target_path.read_text()).is_equal_to("<h1>Hello</h1>")


def test_write_to_file_aborts_when_the_target_folder_does_not_exist(tmp_path: Path):
    # Arrange
    file_system_service = FileSystemService()
    target_path = tmp_path / "missing_folder" / "output.html"

    # Act / Assert
    with pytest.raises(typer.Abort):
        file_system_service.write_to_file(
            path=str(target_path), content="<h1>Hello</h1>"
        )


def test_file_change_handler_invokes_on_change_for_a_file_event():
    # Arrange
    was_called = Event()
    handler = FileChangeHandler(on_change=was_called.set)
    event = FileModifiedEvent("/tmp/watched-file.txt")

    # Act
    handler.on_modified(event)

    # Assert
    assert_that(was_called.is_set()).is_true()


def test_file_change_handler_ignores_directory_events():
    # Arrange
    was_called = Event()
    handler = FileChangeHandler(on_change=was_called.set)
    event = DirModifiedEvent("/tmp/watched-dir")

    # Act
    handler.on_modified(event)

    # Assert
    assert_that(was_called.is_set()).is_false()


def test_list_files_from_recursively_lists_matching_files(
    file_system_service, tmp_path: Path
):
    # Arrange
    (tmp_path / "nested").mkdir()
    top_level_file = tmp_path / "top.html"
    top_level_file.write_text("<html></html>")
    nested_file = tmp_path / "nested" / "nested.html"
    nested_file.write_text("<html></html>")
    (tmp_path / "ignored.md").write_text("not html")

    # Act
    result = file_system_service.list_files_from(
        folder_path=str(tmp_path), pattern="*.html"
    )

    # Assert
    assert_that(sorted(result)).is_equal_to(
        sorted([str(top_level_file), str(nested_file)])
    )


def test_list_files_from_returns_an_empty_list_when_nothing_matches(
    file_system_service, tmp_path: Path
):
    # Act
    result = file_system_service.list_files_from(
        folder_path=str(tmp_path), pattern="*.html"
    )

    # Assert
    assert_that(result).is_empty()


def test_watch_for_changes_on_starts_an_observer_watching_the_received_files(
    file_system_service, tmp_path: Path
):
    # Arrange
    watched_file = tmp_path / "watched.txt"
    watched_file.write_text("original content")
    was_called = Event()

    # Act
    observer = file_system_service.watch_for_changes_on(
        watch_list=[str(watched_file)], on_change=was_called.set
    )

    try:
        watched_file.write_text("changed content")
        was_called.wait(timeout=2)

        # Assert
        assert_that(observer.is_alive()).is_true()
        assert_that(was_called.is_set()).is_true()

    finally:
        observer.stop()
        observer.join()
