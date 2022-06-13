from typing import Generator


def chunks(collection: list, chunk_size: int) -> Generator[list[list], None, None]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(collection), chunk_size):
        yield collection[i : i + chunk_size]
