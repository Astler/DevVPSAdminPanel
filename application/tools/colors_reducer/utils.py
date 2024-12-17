import numpy as np
from PIL import Image
from flask import current_app
from sklearn.cluster import KMeans

def reduce_image_colors(original_path: str, num_colors: int, output_path: str) -> None:
    with Image.open(original_path) as img:
        original_format = img.format
        has_alpha = 'A' in img.getbands()

        if has_alpha:
            alpha = img.split()[-1]
            img = img.convert('RGB')

        # Force exact number of colors using quantize
        img = img.quantize(colors=num_colors, method=0, dither=0)  # method=0 is MEDIANCUT
        img = img.convert('RGB')

        if has_alpha:
            img = img.convert('RGBA')
            img.putalpha(alpha)

        if original_format == 'PNG':
            img.save(output_path, optimize=False, compress_level=0)
        else:
            img.save(output_path)