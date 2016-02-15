from PIL import Image

import random


def create_water_sign(in_path, out_path, seed, n, delta):
    if delta < 0:
        delta = -delta

    img = Image.open(in_path)
    (width, height) = img.size

    conv = img.convert("RGBA").getdata()

    steg_img = Image.new('RGBA', (width, height))
    data_img = steg_img.getdata()

    for (x1, y1), (x2, y2) in generate_points(seed, width, height, n):
        (r1, g1, b1, a1) = conv.getpixel((x1, y1))
        (r2, g2, b2, a2) = conv.getpixel((x2, y2))
        r1 = min(255, r1 + delta)
        g1 = min(255, g1 + delta)
        b1 = min(255, b1 + delta)
        r2 = max(0, r2 - delta)
        g2 = max(0, g2 - delta)
        b2 = max(0, b2 - delta)
        conv.putpixel((x1, y1), (r1, g1, b1, a1))
        conv.putpixel((x2, y2), (r2, g2, b2, a2))

    for w in range(width):
        for h in range(height):
            data_img.putpixel((w, h), conv.getpixel((w, h)))

    steg_img.save(out_path, 'PNG')


def check_water_sign(input_img_file, seed, n, delta):
    sum = 0  # 2 * delta * n

    if delta < 0:
        delta = -delta

    img = Image.open(input_img_file)
    (width, height) = img.size

    conv = img.convert("RGBA").getdata()
    for (x1, y1), (x2, y2) in generate_points(seed, width, height, n):
        (r1, g1, b1, a1) = conv.getpixel((x1, y1))
        (r2, g2, b2, a2) = conv.getpixel((x2, y2))
        sum += ((r1 + g1 + b1) - (r2 + g2 + b2)) / 3

    return sum


def generate_points(seed, width, height, n):
    random.seed(seed)
    for _ in range(n):
        yield (random.randint(0, width - 1), random.randint(0, height - 1)), \
              (random.randint(0, width - 1), random.randint(0, height - 1))


def rotate(in_path, out_path):
    img = Image.open(in_path)
    img.rotate(90).save(out_path, 'PNG')


if __name__ == "__main__":
    SEED = 228
    n = 10000
    delta = 5
    in_path = 'image.png'
    out_path = 'out_image.png'
    rotated_img = 'rotated.png'

    create_water_sign(in_path, out_path, SEED, n, delta)
    print('Expected value', 2 * n * delta)
    print('Checking watersign with right params', check_water_sign(out_path, SEED, n, delta))
    print('Checking watersign with incorrect params', check_water_sign(out_path, 0, n, delta))

    rotate(out_path, rotated_img)
    print('Checking watersign on rotated image', check_water_sign(rotated_img, SEED, n, delta))
