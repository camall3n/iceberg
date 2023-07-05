from iceberg import Renderer, Drawable
from PIL import Image

import numpy as np
import os
from pixelmatch.contrib.PIL import pixelmatch


def check_render(
    drawable: Drawable, expected_filename: str, generate_expected: bool = False
):
    """Checks that the given Drawable renders to the expected image.

    Args:
        drawable: The Drawable to render.
        expected_filename: The filename of the expected image.
        generate_expected: Whether to generate the expected image if it does not exist.

    Raises:
        AssertionError: If the rendered image does not match the expected image.
    """

    expected_full_filename = os.path.join("tests", "testdata", expected_filename)

    renderer = Renderer()
    renderer.render(drawable)
    rendered_image = renderer.get_rendered_image()

    if generate_expected:
        renderer.save_rendered_image(expected_full_filename)
        return

    expected_image = Image.open(expected_full_filename)
    rendered_image = Image.fromarray(rendered_image)
    img_diff = Image.new("RGBA", expected_image.size)

    mismatch = pixelmatch(expected_image, rendered_image, img_diff, 0.1)
    percent_mismatch = mismatch / (expected_image.size[0] * expected_image.size[1])

    if percent_mismatch > 0.01:
        # Save the rendered image, the expected image, and the diff image.
        debug_dir = os.path.join("tests", "testoutput")
        os.makedirs(debug_dir, exist_ok=True)
        rendered_image.save(os.path.join(debug_dir, f"rendered_{expected_filename}"))
        expected_image.save(os.path.join(debug_dir, f"expected_{expected_filename}"))
        img_diff.save(os.path.join(debug_dir, f"diff_{expected_filename}"))
        assert False, f"Image mismatch: {percent_mismatch * 100:.2f}%"
