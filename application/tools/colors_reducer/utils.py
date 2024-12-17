import numpy as np
from PIL import Image
from flask import current_app
from sklearn.cluster import KMeans

def reduce_image_colors(original_path: str, num_colors: int, output_path: str) -> None:
    try:
        with Image.open(original_path) as img:
            original_format = img.format
            has_alpha = 'A' in img.getbands()

            # Convert to palette mode with exact number of colors
            if has_alpha:
                alpha = img.split()[-1]
                img = img.convert('RGB')

            # This forces exact color reduction without dithering
            img = img.convert('P', palette=Image.Palette.ADAPTIVE, colors=num_colors)
            img = img.convert('RGB')

            # Restore alpha if needed
            if has_alpha:
                img = img.convert('RGBA')
                img.putalpha(alpha)

            # Save with no compression
            if original_format == 'PNG':
                img.save(output_path, optimize=False, compress_level=0)
            else:
                img.save(output_path)

    except Exception as e:
        current_app.logger.error(f"Error processing image {original_path}: {str(e)}")
        raise