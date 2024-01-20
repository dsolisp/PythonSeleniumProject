from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch


def compare_images(image_path1, image_path2, diff_output_path):
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)
    img_diff = Image.new("RGBA", img1.size)
    mismatch = 0
    try:
        mismatch = pixelmatch(img1, img2, img_diff, includeAA=True)
        img_diff.save(diff_output_path)
    except ValueError:
        print("ValueError")
        return 1
    return mismatch
