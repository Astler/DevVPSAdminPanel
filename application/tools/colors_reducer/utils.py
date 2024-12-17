import numpy as np
from PIL import Image
from flask import current_app
from sklearn.cluster import KMeans


def reduce_image_colors(original_path: str, num_colors: int, output_path: str) -> None:
    try:
        with Image.open(original_path) as img:
            original_format = img.format
            has_alpha = 'A' in img.getbands()

            if has_alpha:
                # Store original alpha for later
                alpha = np.array(img.split()[-1])
                # Process only RGB data
                img = img.convert('RGB')

            # Convert to array without any preprocessing
            pixels = np.asarray(img, dtype=np.float32)
            original_shape = pixels.shape
            pixels = pixels.reshape(-1, 3)

            # Exact clustering without any randomness
            kmeans = KMeans(
                n_clusters=num_colors,
                random_state=42,
                n_init=1,
                max_iter=1000,
                tol=0
            ).fit(pixels)

            # Get exact colors without any rounding
            colors = np.uint8(np.round(kmeans.cluster_centers_))
            labels = kmeans.labels_
            new_pixels = colors[labels]
            new_pixels = new_pixels.reshape(original_shape)

            # Convert back to image without any interpolation
            new_image = Image.fromarray(new_pixels, mode='RGB')

            if has_alpha:
                new_image = new_image.convert('RGBA')
                # Binary alpha for perfect edges
                alpha_binary = np.uint8(alpha > 127) * 255
                alpha_layer = Image.fromarray(alpha_binary, mode='L')
                new_image.putalpha(alpha_layer)

            # Format-specific perfect quality saves
            if original_format in ('JPEG', 'JPG'):
                new_image = new_image.convert('RGB')
                new_image.save(output_path, original_format,
                               quality=100,
                               subsampling=0,
                               optimize=False)
            elif original_format == 'PNG':
                new_image.save(output_path, format='PNG',
                               optimize=False,
                               compress_level=0)
            elif original_format == 'GIF':
                new_image.save(output_path, format='GIF',
                               optimize=False)
            elif original_format == 'WEBP':
                new_image.save(output_path, format='WEBP',
                               quality=100,
                               lossless=True,
                               method=6)
            else:
                new_image.save(output_path, format='PNG',
                               optimize=False,
                               compress_level=0)

    except Exception as e:
        current_app.logger.error(f"Error processing image {original_path}: {str(e)}")
        raise