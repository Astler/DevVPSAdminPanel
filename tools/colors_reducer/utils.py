import numpy as np
from PIL import Image
from flask import current_app
from sklearn.cluster import KMeans


def reduce_image_colors(
        original_path,
        num_colors: int,
        output_path
) -> None:
    try:
        with Image.open(original_path) as img:
            img = img.convert('RGBA')

            color_data = np.array(img.convert('RGB'))
            alpha_channel = np.array(img.split()[-1])

            pixels = color_data.reshape(-1, 3)

            kmeans = KMeans(
                n_clusters=num_colors,
                random_state=0,
                n_init=10
            ).fit(pixels)

            new_colors = kmeans.cluster_centers_[kmeans.labels_]
            new_image = new_colors.reshape(color_data.shape).astype(np.uint8)

            result = Image.fromarray(new_image).convert('RGBA')
            result.putalpha(Image.fromarray(alpha_channel))

            # Save the result
            result.save(output_path)
    except Exception as e:
        current_app.logger.error(f"Error processing image {original_path}: {str(e)}")