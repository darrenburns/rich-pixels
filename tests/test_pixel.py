from pathlib import Path

import pytest
from rich.align import Align
from rich.console import Console
from rich.segment import Segment
from rich.style import Style
from syrupy.extensions.image import SVGImageSnapshotExtension

from rich_pixels import Pixels

SAMPLE_DATA_DIR = Path(__file__).parent / ".sample_data/"


@pytest.fixture
def svg_snapshot(snapshot):
    return snapshot.use_extension(SVGImageSnapshotExtension)


def get_console():
    console = Console(record=True)
    return console


def test_png_image_path(svg_snapshot):
    console = get_console()
    pixels = Pixels.from_image_path(SAMPLE_DATA_DIR / "images/bulbasaur.png")
    console.print(pixels)
    svg = console.export_svg()
    assert svg == svg_snapshot


def test_ascii_text(svg_snapshot):
    console = get_console()
    ascii = (SAMPLE_DATA_DIR / "ascii/rich_pixels.txt").read_text(encoding="utf-8")
    mapping = {"#": Segment(" ", Style.parse("on #50b332")),
               "=": Segment(" ", Style.parse("on #10ada3"))}
    pixels = Pixels.from_ascii(
        ascii,
        mapping=mapping,
    )
    console.print(Align.center(pixels))
    svg = console.export_svg(title="pixels in the terminal")
    assert svg == svg_snapshot
