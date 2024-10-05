import base64
import io
import json
import os

from PIL import Image, ImageColor, ImageChops

import config
from application import get_db

def get_layers_from_web(banner_id):
    banner_data = get_mock_banner_data(banner_id)
    if banner_data is None:
        return None
    return banner_data['mlayers']

def get_image_data_url_by_id(banner_id, scale=10):
    banner_data = get_mock_banner_data(banner_id)
    if banner_data is None:
        return None
    return get_image_data_url(banner_data['mlayers'], scale)


def get_image_data_url(layers, scale=10):
    if not layers:
        return None

    banner_image_io = create_banner(layers, scale)

    img_base64 = base64.b64encode(banner_image_io.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"


def get_banner_data_from_firestore(banner_id):
    firestore_db = get_db(config.MC_PROJECT_ID)

    try:
        banner_ref = firestore_db.collection('shared_banners').document(banner_id)
        banner_doc = banner_ref.get()
        if banner_doc.exists:
            return banner_doc.to_dict()
        else:
            print(f"No such banner with ID {banner_id}")
            return None
    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")
        return None


# Mock function to simulate getting banner data_old
def get_mock_banner_data(banner_id):
    banner_json = json.dumps(get_banner_data_from_firestore(banner_id))
    return json.loads(banner_json)


def apply_color_to_image(image, color_name):
    # Convert the hex color to an RGBA tuple
    color_name = ImageColor.getrgb(get_minecraft_color_by_name(color_name)) + (255,)

    # Create a solid color image and composite it using the source alpha
    color_layer = Image.new('RGBA', image.size, color_name)
    colored_image = ImageChops.multiply(image, color_layer)

    return colored_image


def get_minecraft_color_by_name(item_name: str) -> str:
    colors = {
        "white": "#FFFFFF",
        "light_gray": "#999999",
        "light_blue": "#6699D8",
        "orange": "#D87F33",
        "magenta": "#B24CD8",
        "yellow": "#E5E533",
        "lime": "#7FCC19",
        "pink": "#F27FA5",
        "gray": "#4C4C4C",
        "cyan": "#4C7F99",
        "purple": "#7F3FB2",
        "blue": "#334CB2",
        "brown": "#664C33",
        "green": "#667F33",
        "red": "#993333",
        "black": "#191919"
    }

    for color_name, hex_value in colors.items():
        if color_name in item_name:
            return hex_value
    return "#FFFFFF"  # default color if no match found


def upscale_image(image, factor):
    # Upscale the image using the nearest neighbor algorithm
    new_size = (image.size[0] * factor, image.size[1] * factor)
    return image.resize(new_size, Image.NEAREST)


def create_banner(layers, upscale_factor=1):
    # Base directory for patterns - adjust the path to where your app is running
    base_pattern_path = os.path.join('banners', 'assets', 'patterns')

    # Assume the base banner size from the first image
    first_image_path = os.path.join(base_pattern_path, layers[0]['patternName'] + ".png")

    with Image.open(first_image_path) as first_image:
        width, height = first_image.size

        banner = Image.new('RGBA', (width, height))

    # Composite layers onto the banner
    for layer in layers:
        show_it = layer.get('mIsVisible', True)  # Correct key name from 'misVisible' to 'mIsVisible'

        if not show_it:
            continue

        filename = layer['patternName'] + ".png"  # Ensure this is just the filename, not a URL
        pattern_file_path = os.path.join(base_pattern_path, filename)

        with Image.open(pattern_file_path) as layer_image:
            layer_image = layer_image.convert('RGBA')
            layer_image = layer_image.resize((width, height))  # Resize layer to match banner size

            colored_layer = apply_color_to_image(layer_image, layer['patternColor'])

            banner = Image.alpha_composite(banner, colored_layer)

    if upscale_factor != 1:
        banner = upscale_image(banner, upscale_factor)

    # Save the banner image to a bytes buffer
    img_byte_arr = io.BytesIO()
    banner.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr
