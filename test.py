import requests
from PIL import Image
from io import BytesIO

url_1 = 'https://d2ey9sqrvkqdfs.cloudfront.net/0qZF/2.jpg'
url_2 = 'https://d2ey9sqrvkqdfs.cloudfront.net/0qZF/2.jpg'

def _compare_images(url_1, url_2):
    # Fetch images from URLs
    img_a = Image.open(requests.get(url_1, stream=True).raw)
    img_b = Image.open(requests.get(url_2, stream=True).raw)

    # Convert both images to RGB (to avoid issues with transparency or different formats)
    img_a = img_a.convert("RGB")
    img_b = img_b.convert("RGB")

    # Compare the sizes first (optional but faster)
    if img_a.size != img_b.size:
        return False  # Images have different sizes, so they're not the same

    # Compare pixel values
    return list(img_a.getdata()) == list(img_b.getdata())  # Compare pixel data directly

print(_compare_images(url_1, url_2))
