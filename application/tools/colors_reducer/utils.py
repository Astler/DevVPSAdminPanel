import numpy as np
from PIL import Image
from flask import current_app
from sklearn.cluster import KMeans

def count_colors(image_path):
    with Image.open(image_path) as img:
        if 'A' in img.getbands():
            img = img.convert('RGB')
        colors = img.getcolors()
        return len(colors) if colors else 0


def reduce_image_colors(original_path: str, num_colors: int, output_path: str) -> None:
    try:
        with Image.open(original_path) as img:
            has_alpha = 'A' in img.getbands()

            if has_alpha:
                alpha = img.split()[-1]
                img = img.convert('RGB')

            # Convert to numpy array
            img_array = np.array(img)
            pixels = img_array.reshape(-1, 3)

            # Use KMeans with careful initialization
            kmeans = KMeans(
                n_clusters=num_colors,
                init='k-means++',  # Better initialization
                n_init=10,
                max_iter=300
            ).fit(pixels)

            # Get color palette
            palette = np.uint8(kmeans.cluster_centers_)

            # Map to new colors
            quantized = palette[kmeans.labels_].reshape(img_array.shape)
            new_img = Image.fromarray(quantized)

            if has_alpha:
                new_img = new_img.convert('RGBA')
                alpha = Image.eval(alpha, lambda x: 255 if x > 127 else 0)
                new_img.putalpha(alpha)

            new_img.save(output_path, 'PNG', optimize=False, compress_level=0)

    except Exception as e:
        print(f"Error: {str(e)}")
        raise


def count_colors(image_path):
    with Image.open(image_path) as img:
        if 'A' in img.getbands():
            # Convert to RGB to count colors without alpha
            img = img.convert('RGB')

        # Get unique colors
        colors = img.getcolors()
        return len(colors) if colors else 0


if __name__ == "__main__":
    input_image = "input.jpg"  # Put your image name here
    output_image = "output.png"
    target_colors = 4  # Change this to test different color counts

    print(f"Original colors: {count_colors(input_image)}")

    reduce_image_colors(input_image, target_colors, output_image)

    result_colors = count_colors(output_image)
    print(f"Result colors: {result_colors}")
    print(f"Target met: {result_colors == target_colors}")