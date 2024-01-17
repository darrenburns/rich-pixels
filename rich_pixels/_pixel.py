from __future__ import annotations
import math

from pathlib import Path, PurePath
from typing import Iterable, Mapping, Tuple, Union, Optional, List

from PIL import Image as PILImageModule
from PIL.Image import Image
from PIL.Image import Resampling
from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment, Segments
from rich.style import Style


class Pixels:
    DEFAULT_COLOR = "black"

    def __init__(self) -> None:
        self._segments: Segments | None = None

    @staticmethod
    def _get_color(pixel: Tuple[int, int, int, int], default_color: str = None) -> Style:
        r, g, b, a = pixel
        return f"rgb({r},{g},{b})" if a > 0 else default_color or Pixels.DEFAULT_COLOR

    @staticmethod
    def from_image(
        image: Image,
        use_halfpixels: bool = False,
    ):
        segments = Pixels._segments_from_image(image, use_halfpixels=use_halfpixels)
        return Pixels.from_segments(segments)

    @staticmethod
    def from_image_path(
        path: Union[PurePath, str],
        resize: Optional[Tuple[int, int]] = None,
        use_halfpixels: bool = False,
    ) -> Pixels:
        """Create a Pixels object from an image. Requires 'image' extra dependencies.

        Args:
            path: The path to the image file.
            resize: A tuple of (width, height) to resize the image to.
            use_halfpixels: Whether to use halfpixels or not. Defaults to False.
        """
        with PILImageModule.open(Path(path)) as image:
            segments = Pixels._segments_from_image(image, resize, use_halfpixels)

        return Pixels.from_segments(segments)

    @staticmethod
    def _segments_from_image(
        image: Image, resize: Optional[Tuple[int, int]] = None, use_halfpixels: bool = False
    ) -> list[Segment]:
        if use_halfpixels:
            # because each row is 2 lines high, so we need to make sure the height is even
            target_height = resize[1] if resize else image.size[1]
            if target_height % 2 != 0:
                target_height += 1

            if not resize and image.size[1] != target_height:
                resize = (image.size[0], target_height)

        if resize:
            image = image.resize(resize, resample=Resampling.NEAREST)

        width, height = image.width, image.height
        rgba_image = image.convert("RGBA")
        get_pixel = rgba_image.getpixel
        parse_style = Style.parse
        null_style = Style.null()
        segments = []

        def render_halfpixels(x: int, y: int) -> None:
            """
            Render 2 pixels per character.
            """
            
            # get upper pixel
            upper_color = Pixels._get_color(get_pixel((x, y)))
            # get lower pixel
            lower_color = Pixels._get_color(get_pixel((x, y + 1)))
            # render upper pixel use foreground color, lower pixel use background color
            style = parse_style(f"{upper_color} on {lower_color}")
            # use upper halfheight block to render
            row_append(Segment("▀", style))

        def render_fullpixels(x: int, y: int) -> None:
            """
            Render 1 pixel per 2character.
            """

            pixel = get_pixel((x, y))
            style = parse_style(f"on {Pixels._get_color(pixel)}") if pixel[3] > 0 else null_style
            row_append(Segment("  ", style))

        render = render_halfpixels if use_halfpixels else render_fullpixels
        # step=2 if use halfpixels, because each row is 2 lines high
        seq = range(0, height, 2) if use_halfpixels else range(height)

        for y in seq:
            this_row: List[Segment] = []
            row_append = this_row.append

            for x in range(width):
                render(x, y)

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
    def from_ascii(
        grid: str, mapping: Optional[Mapping[str, Segment]] = None
    ) -> Pixels:
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


if __name__ == "__main__":
    console = Console()
    images_path = Path(__file__).parent / "../tests/.sample_data/images"
    pixels = Pixels.from_image_path(images_path / "bulbasaur.png")
    console.print("\[case.1] print fullpixels")
    console.print(pixels)

    pixels = Pixels.from_image_path(images_path / "bulbasaur.png", use_halfpixels=True)
    console.print("\[case.2] print halfpixels")
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
    console.print("\[case.3] print ascii")
    console.print(pixels)
