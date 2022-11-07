from __future__ import annotations

from pathlib import Path, PurePath
from typing import Iterable, Mapping

from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment, Segments
from rich.style import Style

try:
    from PIL import Image
    from PIL.Image import Resampling

    _PIL_INSTALLED = True
except ImportError:
    _PIL_INSTALLED = False


class PixelsError(Exception):
    pass


class Pixels:
    def __init__(self) -> None:
        self._segments: Segments | None = None

    @staticmethod
    def from_image(
        image: "Image",
    ):
        segments = Pixels._segments_from_image(image)
        return Pixels.from_segments(segments)

    @staticmethod
    def from_image_path(
        path: PurePath | str,
        resize: tuple[int, int] | None = None,
    ) -> Pixels:
        """Create a Pixels object from an image. Requires 'image' extra dependencies.

        Args:
            path: The path to the image file.
            resize: A tuple of (width, height) to resize the image to.
        """
        with Image.open(Path(path)) as image:
            segments = Pixels._segments_from_image(image, resize)

        return Pixels.from_segments(segments)

    @staticmethod
    def _segments_from_image(
        image: "Image", resize: tuple[int, int] | None = None
    ) -> list[Segment]:
        if not _PIL_INSTALLED:
            raise PixelsError(
                "Methods like from_image and from_image_path require "
                "the 'image' extra dependencies to be installed."
            )

        if resize:
            image = image.resize(resize, resample=Resampling.NEAREST)

        width, height = image.width, image.height
        rgba_image = image.convert("RGBA")
        get_pixel = rgba_image.getpixel
        parse_style = Style.parse
        null_style = Style.null()
        segments = []

        for y in range(height):
            this_row = []
            row_append = this_row.append

            for x in range(width):
                r, g, b, a = get_pixel((x, y))
                style = parse_style(f"on rgb({r},{g},{b})") if a > 0 else null_style
                row_append(Segment("  ", style))

            row_append(Segment("\n", null_style))

            # TODO: Double-check if this is required - I've forgotten...
            if not all(t[1] == "" for t in this_row[:-1]):
                segments += this_row

        return segments

    @staticmethod
    def from_segments(
        segments: Iterable[Segment],
    ) -> Pixels:
        """Create a Pixels object from an Iterable of Segments instance."""
        pixels = Pixels()
        pixels._segments = Segments(segments)
        return pixels

    @staticmethod
    def from_ascii(grid: str, mapping: Mapping[str, Segment] | None = None) -> Pixels:
        """
        Create a Pixels object from a 2D-grid of ASCII characters.
        Each ASCII character can be mapped to a Segment (a character and style combo),
        allowing you to add a splash of colour to your grid.

        Args:
            grid: A 2D grid of characters (a multi-line string).
            mapping: Maps ASCII characters to Segments. Occurrences of a character
                will be replaced with the corresponding Segment.
        """
        if mapping is None:
            mapping = {}

        if not grid:
            return Pixels.from_segments([])

        segments = []
        for character in grid:
            segment = mapping.get(character, Segment(character))
            segments.append(segment)

        return Pixels.from_segments(segments)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield self._segments or ""


if __name__ == '__main__':
    console = Console()
    images_path = Path(__file__).parent / "../.sample_data/images"
    pixels = Pixels.from_image_path(images_path / "1.png")
    console.print(pixels)

    grid = """\
         xx   xx
         ox   ox
         Ox   Ox
    xx             xx
    xxxxxxxxxxxxxxxxx
    """

    mapping = {
        "x": Segment(" ", Style.parse("yellow on yellow")),
        "o": Segment(" ", Style.parse("on white")),
        "O": Segment("O", Style.parse("white on blue")),
    }
    pixels = Pixels.from_ascii(grid, mapping)
    console.print(pixels)
