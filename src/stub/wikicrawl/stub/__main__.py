import click
from wikicrawl.core import logging

logging.setup()

from wikicrawl.stub import Stub  # noqa: E402


@click.group()
def stub():
    pass


@stub.command(help="Generate wikipedia stubs.")
@click.option(
    "--entry-point",
    type=str,
    required=True,
    help="Name of the wikipedia page to start crawling.",
)
@click.option("--pages-count", type=int, required=True, help="Number of page in the stub.")
def generate(entry_point, pages_count):
    Stub(entry_point=entry_point, pages_count=pages_count).generate()


if __name__ == "__main__":
    stub()
