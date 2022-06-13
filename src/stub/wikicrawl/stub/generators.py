import json
import logging
import os
import shutil
from pathlib import Path

from wikicrawl.stub import settings


def create_directory(path: Path):
    if path.exists():
        shutil.rmtree(path=str(path))
    path.mkdir(parents=True, exist_ok=True)


class WireMock:
    def __init__(self, pages_files_paths: list[str]) -> None:
        self.pages_files_paths = pages_files_paths
        self.logger = logging.getLogger("generator")

    def generate(self) -> None:
        self.logger.info("Wire mock generation start (pages count: %s).", len(self.pages_files_paths))
        file_destination_directory_path = Path(settings.STUB_OUTPUT_DIRECTORY, "__files")
        create_directory(file_destination_directory_path)
        mapping_destination_directory_path = Path(settings.STUB_OUTPUT_DIRECTORY, "mappings")
        create_directory(mapping_destination_directory_path)
        self.build(
            file_destination_directory_path=file_destination_directory_path,
            mapping_destination_directory_path=mapping_destination_directory_path,
        )
        self.logger.info("Wire mock stub generated with success.")

    def build(
        self,
        file_destination_directory_path: Path,
        mapping_destination_directory_path: Path,
    ) -> None:
        for page_file_path in self.pages_files_paths:
            page_name = os.path.basename(page_file_path)
            self.add_page_file(
                page_name=page_name,
                page_file_path=page_file_path,
                file_destination_directory_path=str(file_destination_directory_path),
            )
            self.add_page_mapping(
                page_name=page_name,
                mapping_destination_directory_path=str(mapping_destination_directory_path),
            )

    def add_page_file(self, page_name: str, page_file_path: str, file_destination_directory_path: str):
        destination_page_file_path = Path(file_destination_directory_path, page_name)
        if not destination_page_file_path.exists():
            shutil.copyfile(src=page_file_path, dst=destination_page_file_path)

    def add_page_mapping(self, page_name: str, mapping_destination_directory_path: str) -> None:
        mapping = {
            "request": {"method": "GET", "url": f"/wiki/{page_name}"},
            "response": {"bodyFileName": f"{page_name}", "status": 200},
        }
        with open(str(Path(mapping_destination_directory_path, f"{page_name}.json")), "w+") as stream:
            json.dump(mapping, stream, indent=4, sort_keys=True)
