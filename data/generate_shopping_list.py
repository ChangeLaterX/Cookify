#!/usr/bin/env python3
"""
Generate a handwritten-style shopping list image for OCR testing.
"""

import random

from PIL import Image, ImageDraw, ImageFont


def create_shopping_list_image():
    """Create a shopping list image that simulates handwritten text."""

    # Image dimensions
    width = 300
    height = 500

    # Create white background with slight texture
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Add some light horizontal lines like notebook paper
    for i in range(20, height, 25):
        draw.line([(20, i), (width - 20, i)], fill="lightblue", width=1)

    # Shopping list items
    shopping_items = [
        "Shopping List",
        "",
        "□ Tomatoes",
        "□ Onions",
        "□ Garlic",
        "□ Bell peppers",
        "□ Carrots",
        "□ Potatoes",
        "□ Spinach",
        "□ Bananas",
        "□ Apples",
        "□ Chicken",
        "□ Ground beef",
        "□ Fish",
        "□ Milk",
        "□ Eggs",
        "□ Cheese",
        "□ Bread",
        "□ Rice",
        "□ Pasta",
        "□ Olive oil",
        "□ Salt",
        "□ Pepper",
    ]

    # Try to use a handwriting-like font, fallback to default
    try:
        font_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18
        )
        font_normal = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14
        )
    except:
        font_title = font_normal = ImageFont.load_default()

    y_pos = 40
    line_height = 22

    for i, item in enumerate(shopping_items):
        if item == "Shopping List":
            # Title
            if font_title:
                bbox = draw.textbbox((0, 0), item, font=font_title)
                text_width = bbox[2] - bbox[0]
                x_pos = (width - text_width) // 2
            else:
                x_pos = 80
            draw.text((x_pos, y_pos), item, fill="darkblue", font=font_title)
        elif item == "":
            # Skip empty lines
            pass
        else:
            # Add slight random offset to simulate handwriting
            x_offset = random.randint(-2, 2)
            y_offset = random.randint(-1, 1)
            x_pos = 30 + x_offset
            draw.text((x_pos, y_pos + y_offset), item, fill="black", font=font_normal)

        y_pos += line_height

    return img


def main():
    """Generate and save the shopping list image."""
    shopping_list_img = create_shopping_list_image()

    # Save the image
    output_path = "/home/cipher/dev/Cookify/data/sample_shopping_list.png"
    shopping_list_img.save(output_path)
    print(f"Shopping list image saved to: {output_path}")


if __name__ == "__main__":
    main()
