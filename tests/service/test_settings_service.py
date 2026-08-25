from pathlib import Path

import pytest
import typer
from assertpy import assert_that

from vox.service.settings_service import SettingsService


@pytest.fixture
def settings_service():
    return SettingsService()


def test_fetch_from_parses_an_existing_yaml_file(settings_service, tmp_path: Path):
    # Arrange
    settings_file = tmp_path / "settings.yaml"
    settings_file.write_text("baseUrl: https://example.com\ntitle: My Site\n")

    # Act
    settings_content = settings_service.fetch_from(path=str(settings_file))

    # Assert
    assert_that(settings_content).is_equal_to(
        {"baseUrl": "https://example.com", "title": "My Site"}
    )


def test_fetch_from_returns_an_empty_dict_when_the_file_is_missing(
    settings_service, tmp_path: Path
):
    # Arrange
    missing_file = tmp_path / "does_not_exist.yaml"

    # Act
    settings_content = settings_service.fetch_from(path=str(missing_file))

    # Assert
    assert_that(settings_content).is_equal_to({})


def test_fetch_from_aborts_on_a_malformed_yaml_file(settings_service, tmp_path: Path):
    # Arrange
    malformed_file = tmp_path / "malformed.yaml"
    malformed_file.write_text("key: [unterminated\n")

    # Act / Assert
    with pytest.raises(typer.Abort):
        settings_service.fetch_from(path=str(malformed_file))
