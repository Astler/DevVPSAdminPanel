import numpy as np
from PIL import Image
from flask import current_app
from sklearn.cluster import KMeans

def reduce_image_colors(
        original_path: str,
        num_colors: int,
        output_path: str
) -> None:
    """
    Reduce the number of colors in an image using KMeans clustering while maintaining
    pixel-perfect quality suitable for pixel art.

    Args:
        original_path (str): Path to the input image
        num_colors (int): Target number of colors
        output_path (str): Path to save the processed image
    """
    try:
        with Image.open(original_path) as img:
            # Store original format and size
            original_format = img.format
            has_alpha = 'A' in img.getbands()

            # Disable antialiasing by using nearest neighbor resampling
            img = img.resize(img.size, Image.NEAREST)

            # Handle alpha channel
            if has_alpha:
                alpha_channel = np.array(img.split()[-1])
                # Convert to RGB without any interpolation
                color_data = np.array(img.convert('RGB', colors=256))
            else:
                color_data = np.array(img.convert('RGB', colors=256))

            # Reshape for KMeans
            pixels = color_data.reshape(-1, 3)

            # Use KMeans with exact centroids and increased max iterations
            kmeans = KMeans(
                n_clusters=num_colors,
                random_state=0,
                n_init='auto',  # Let sklearn choose the optimal number of initializations
                max_iter=300,  # Increase max iterations for better convergence
                tol=1e-4  # Tighter tolerance for more precise colors
            ).fit(pixels)

            # Get new colors
            new_colors = kmeans.cluster_centers_

            # Round the colors to integers to avoid interpolation artifacts
            new_colors = np.round(new_colors).astype(np.uint8)

            # Map pixels to nearest color center
            new_image = new_colors[kmeans.labels_].reshape(color_data.shape)

            # Create image with nearest neighbor interpolation
            result = Image.fromarray(new_image, mode='RGB')

            # Ensure no interpolation during any transformations
            result = result.resize(result.size, Image.NEAREST)

            # Handle alpha channel if present
            if has_alpha:
                result = result.convert('RGBA')
                # Use binary threshold for alpha to maintain sharp edges
                alpha_threshold = np.where(alpha_channel > 127, 255, 0).astype(np.uint8)
                result.putalpha(Image.fromarray(alpha_threshold))

            # Save with pixel-perfect settings
            if original_format in ('JPEG', 'JPG'):
                result = result.convert('RGB')
                # Save with no compression for maximum quality
                result.save(output_path, original_format, quality=100,
                            subsampling=0)  # Disable chroma subsampling
            elif original_format == 'PNG':
                # Save PNG with no compression for perfect quality
                result.save(output_path, original_format,
                            optimize=False,  # Disable optimization to prevent artifacts
                            compress_level=0)  # No compression
            elif original_format == 'GIF':
                result.save(output_path, original_format,
                            optimize=False)  # Disable optimization
            elif original_format == 'WEBP':
                result.save(output_path, original_format,
                            quality=100,
                            method=6,  # Highest quality encoding
                            lossless=True)  # Use lossless compression
            else:
                # Default to uncompressed PNG
                result.save(output_path, 'PNG',
                            optimize=False,
                            compress_level=0)

    except Exception as e:
        current_app.logger.error(f"Error processing image {original_path}: {str(e)}")
        raise