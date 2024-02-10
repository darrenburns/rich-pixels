from __future__ import annotations

from pathlib import Path, PurePath
from typing import Iterable, Mapping, Tuple, Union, Optional

from PIL import Image as PILImageModule
from PIL.Image import Image
from rich.console import Console, ConsoleOptions, RenderResult
from rich.segment import Segment, Segments
from rich.style import Style

from rich_pixels._renderer import Renderer, HalfcellRenderer, FullcellRenderer


class Pixels:
    def __init__(self) -> None:
        self._segments: Segments | None = None

    @staticmethod
    def from_image(
        image: Image,
        resize: Optional[Tuple[int, int]] = None,
        renderer: Renderer | None = None,
    ):
        """Create a Pixels object from a PIL Image.
        Requires 'image' extra dependencies.

        Args:
            image: The PIL Image
            resize: A tuple of (width, height) to resize the image to.
            renderer: The renderer to use. If None, the default half-cell renderer will
                be used.
        """
        segments = Pixels._segments_from_image(image, resize, renderer=renderer)
        return Pixels.from_segments(segments)

    @staticmethod
    def from_image_path(
        path: Union[PurePath, str],
        resize: Optional[Tuple[int, int]] = None,
        renderer: Renderer | None = None,
    ) -> Pixels:
        """Create a Pixels object from an image path.
        Requires 'image' extra dependencies.

        Args:
            path: The path to the image file.
            resize: A tuple of (width, height) to resize the image to.
            renderer: The renderer to use. If None, the default half-cell renderer will
                be used.
        """
        with PILImageModule.open(Path(path)) as image:
            segments = Pixels._segments_from_image(image, resize, renderer=renderer)

        return Pixels.from_segments(segments)

    @staticmethod
    def _segments_from_image(
        image: Image,
        resize: Optional[Tuple[int, int]] = None,
        renderer: Renderer | None = None,
    ) -> list[Segment]:
        if renderer is None:
            renderer = HalfcellRenderer()
        return renderer.render(image, resize)

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
    pixels = Pixels.from_image_path(
        images_path / "bulbasaur.png", renderer=FullcellRenderer()
    )
    console.print("\\[case.1] print with fullpixels renderer")
    console.print(pixels)

    pixels = Pixels.from_image_path(
        images_path / "bulbasaur.png", renderer=FullcellRenderer(default_color="black")
    )
    console.print("\\[case.2] print with fullpixels renderer and default_color")
    console.print(pixels)

    pixels = Pixels.from_image_path(
        images_path / "bulbasaur.png", renderer=HalfcellRenderer()
    )
    console.print("\\[case.3] print with halfpixels renderer")
    console.print(pixels)

    pixels = Pixels.from_image_path(
        images_path / "bulbasaur.png", renderer=HalfcellRenderer(default_color="black")
    )
    console.print("\\[case.4] print with halfpixels renderer and default_color")
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
    console.print("\\[case.5] print ascii")
    console.print(pixels)
