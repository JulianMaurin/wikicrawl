import os
import tempfile
from pathlib import Path
from unittest import mock

from wikicrawl.stub.generators import WireMock, create_directory


def test_generate():
    generator = WireMock(pages_files_paths=[])
    with (
        mock.patch("wikicrawl.stub.generators.settings") as mock_settings,
        mock.patch("wikicrawl.stub.generators.WireMock.build") as mock_build,
        tempfile.TemporaryDirectory() as temp_directory,
    ):
        mock_settings.STUB_OUTPUT_DIRECTORY = temp_directory
        generator.generate()
        mock_build.assert_called_once_with(
            file_destination_directory_path=Path(temp_directory, "__files"),
            mapping_destination_directory_path=Path(temp_directory, "mappings"),
        )


def test_build():
    with (
        mock.patch("wikicrawl.stub.generators.WireMock.add_page_file") as mock_add_page_file,
        mock.patch("wikicrawl.stub.generators.WireMock.add_page_mapping") as mock_add_page_mapping,
        tempfile.TemporaryDirectory() as temp_directory,
        tempfile.NamedTemporaryFile() as temp_file_1,
        tempfile.NamedTemporaryFile() as temp_file_2,
    ):
        generator = WireMock(pages_files_paths=[temp_file_1.name, temp_file_2.name])

        file_destination_directory_path = (Path(temp_directory, "__files"),)
        mapping_destination_directory_path = Path(temp_directory, "mappings")
        generator.build(
            file_destination_directory_path=file_destination_directory_path,
            mapping_destination_directory_path=mapping_destination_directory_path,
        )

        add_page_file_calls = [
            mock.call(
                page_name=os.path.basename(temp_file_1.name),
                page_file_path=temp_file_1.name,
                file_destination_directory_path=str(file_destination_directory_path),
            ),
            mock.call(
                page_name=os.path.basename(temp_file_2.name),
                page_file_path=temp_file_2.name,
                file_destination_directory_path=str(file_destination_directory_path),
            ),
        ]
        mock_add_page_file.assert_has_calls(add_page_file_calls, any_order=True)

        add_page_mapping_calls = [
            mock.call(
                page_name=os.path.basename(temp_file_1.name),
                mapping_destination_directory_path=str(mapping_destination_directory_path),
            ),
            mock.call(
                page_name=os.path.basename(temp_file_2.name),
                mapping_destination_directory_path=str(mapping_destination_directory_path),
            ),
        ]
        mock_add_page_mapping.assert_has_calls(add_page_mapping_calls, any_order=True)


def test_add_page_file():
    page_name = "page name"
    generator = WireMock(pages_files_paths=[])
    with (
        tempfile.TemporaryDirectory() as temp_directory,
        mock.patch("wikicrawl.stub.generators.shutil.copyfile") as mock_copyfile,
    ):
        page_file_path = str(Path(temp_directory, "file"))
        generator.add_page_file(
            page_name=page_name, page_file_path=page_file_path, file_destination_directory_path=temp_directory
        )
        mock_copyfile.assert_called_once_with(src=page_file_path, dst=Path(temp_directory, page_name))


def test_add_page_mapping():
    page_name = "page name"
    mock_open = mock.mock_open()
    generator = WireMock(pages_files_paths=[])
    with (
        tempfile.TemporaryDirectory() as temp_directory,
        mock.patch("wikicrawl.stub.generators.open", mock_open),
        mock.patch("wikicrawl.stub.generators.json.dump") as mock_dump,
    ):
        generator.add_page_mapping(page_name=page_name, mapping_destination_directory_path=temp_directory)
        mock_open.assert_called_once_with(str(Path(temp_directory, f"{page_name}.json")), "w+")
        mock_dump.assert_called_once_with(mock.ANY, mock.ANY, indent=4, sort_keys=True)


def test_create_directory():
    path = mock.MagicMock()
    path.exists.return_value = True
    path.__str__.return_value = "path_str"
    with mock.patch("wikicrawl.stub.generators.shutil.rmtree") as mock_rmtree:
        create_directory(path)
        mock_rmtree.assert_called_once_with(path="path_str")
        path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
