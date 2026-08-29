import logging
from collections.abc import Callable
from glob import glob
from logging import Logger
from typing import override

import typer
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class FileChangeHandler(FileSystemEventHandler):
    """Handle changes in observed files."""

    def __init__(self, on_change: Callable[..., None]):
        """
        Default class constructor. Expects a reference to a Callable used to handle
        changes in a observed file.

        Parameters:
            on_chage (Callable[..., None]): Callable to be invoked when a change in an
                observed file is detected.
        """
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)
        self.__on_change = on_change

    @override
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        """
        Invokes the constructor received callable whenever a change is detected in one
        of the observer files. Directories are ignored anyway.
        """
        if not event.is_directory:
            self.__logger.info("Change detected on file '%s'...", event.src_path)
            self.__on_change()


class FileSystemService:
    """Provides a high level and abstract API to handle file system operations."""

    def __init__(self) -> None:
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)

    def write_to_file(self, path: str, content: str, encoding: str = "UTF-8") -> None:
        """
        Write a text content into a file.

        Parameters:
            path (str): Target file path.
            content (str): Content to written into the target file.
            encoding (str): Optional file encoding. Default: UTF-8
        """
        try:
            self.__logger.info("Writting content on '%s' file...", path)
            with open(path, mode="w", encoding=encoding) as file_output:
                file_output.writelines(content)
                file_output.flush()

        except Exception as ex:
            self.__logger.error(
                "It was not possible to write the content into file '%s' due the "
                "following error: %s",
                path,
                str(ex),
            )
            self.__logger.debug("Error details:", exc_info=True)
            raise typer.Abort(-1) from ex

    def watch_for_changes_on(
        self, watch_list: list[str], on_change: Callable[..., None]
    ):
        """
        Watch for changes in files. Whenever a change is detected, the received
        callable is invoked to handle that.

        Parameters:
            watch_list (list[str]): List with path of files to be watched. Directories
                will be ignored.
            on_change (Callable[..., None]): Callable to be invoked whenever a changed
                is detected in one of the observer files.

        Return:
            observer: Observer configured to watch for file changes in the received
                list of files to observe. The returned observer is already started.
        """
        self.__logger.info("Watching for changes on '%s'...", watch_list)
        observer = Observer()
        handler: FileChangeHandler = FileChangeHandler(on_change=on_change)

        for file_to_watch in watch_list:
            observer.schedule(handler, file_to_watch, recursive=False)

        observer.start()
        return observer

    def list_files_from(self, folder_path: str, pattern: str) -> list[str]:
        """
        Recursively list all files matching the received pattern within the received
        folder path.

        Parameters:
            folder_path (str): Path to the folder to lookup for matching files.
            pattern (str): Lookup pattern to match against the file name.

        Return:
            list[str]: List of files found in the received path that matches the
                received pattern.
        """
        self.__logger.info(
            "Listing content to index matching the pattern '%s' from '%s'...",
            pattern,
            folder_path,
        )

        try:
            return [
                str(file)
                for file in glob(f"{folder_path}/**/{pattern}", recursive=True)
            ]

        except Exception as ex:
            self.__logger.error(
                "It was not possible to list files matching the pattern '%s' from "
                "'%s' due the following error: %s",
                pattern,
                folder_path,
                str(ex),
            )
            self.__logger.debug("Error details:", exc_info=True)
            raise typer.Abort(-1) from ex
