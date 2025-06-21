#!/usr/bin/env python3
"""
Generate a sample receipt image for OCR testing in Cookify.
This creates a realistic grocery receipt with food items.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_receipt_image():
    """Create a sample grocery receipt image for OCR testing."""
    
    # Image dimensions
    width = 400
    height = 800
    
    # Create white background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a monospace font, fallback to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
    except:
        try:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except:
            font_large = font_medium = font_small = None
    
    # Receipt content
    y_pos = 20
    line_height = 20
    
    # Store header
    receipt_text = [
        "FRESH MARKET GROCERY",
        "123 Main Street",
        "Anytown, ST 12345",
        "Tel: (555) 123-4567",
        "",
        "Receipt #: 001234567",
        f"Date: 2024-12-15 14:30:25",
        "Cashier: John D.",
        "",
        "================================",
        "",
        "Tomatoes (2 lbs)      $3.98",
        "Onions (1 lb)         $1.49",
        "Garlic (3 bulbs)      $2.25",
        "Bell Peppers (4)      $4.76",
        "Carrots (2 lbs)       $2.98",
        "Potatoes (5 lbs)      $3.99",
        "Spinach (1 bag)       $2.49",
        "Bananas (6)           $2.94",
        "Apples (3 lbs)        $4.47",
        "Chicken Breast (2lb)  $8.98",
        "Ground Beef (1 lb)    $5.99",
        "Salmon Fillet (1 lb)  $12.99",
        "Milk (1 gallon)       $3.29",
        "Eggs (12 count)       $2.89",
        "Cheddar Cheese (8oz)  $3.99",
        "Bread (whole wheat)   $2.99",
        "Rice (2 lbs)          $3.49",
        "Pasta (1 lb)          $1.99",
        "Olive Oil (500ml)     $6.99",
        "Salt (1 container)    $0.99",
        "Black Pepper          $2.49",
        "Basil (fresh)         $1.99",
        "",
        "================================",
        "",
        "Subtotal:            $79.41",
        "Tax (8.5%):           $6.75",
        "Total:               $86.16",
        "",
        "Payment Method: CARD",
        "Card ending in: 1234",
        "",
        "================================",
        "",
        "Thank you for shopping!",
        "Have a great day!",
        "",
        "Visit us online:",
        "www.freshmarketgrocery.com"
    ]
    
    # Draw each line of text
    for line in receipt_text:
        if line.startswith("FRESH MARKET"):
            font = font_large
        elif line.startswith("Total:") or line.startswith("Subtotal:"):
            font = font_medium
        else:
            font = font_small
            
        # Center store name
        if line.startswith("FRESH MARKET") or line.startswith("123 Main") or line.startswith("Anytown") or line.startswith("Tel:"):
            if font:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_pos = (width - text_width) // 2
            else:
                x_pos = 50
        else:
            x_pos = 20
            
        draw.text((x_pos, y_pos), line, fill='black', font=font)
        y_pos += line_height
    
    return img

def main():
    """Generate and save the receipt image."""
    # Create the receipt image
    receipt_img = create_receipt_image()
    
    # Save the image
    output_path = "/home/cipher/dev/Cookify/data/sample_receipt.png"
    receipt_img.save(output_path)
    print(f"Receipt image saved to: {output_path}")
    
    # Also create a slightly blurred version for testing OCR robustness
    from PIL import ImageFilter
    blurred_img = receipt_img.filter(ImageFilter.GaussianBlur(radius=0.5))
    blurred_path = "/home/cipher/dev/Cookify/data/sample_receipt_blurred.png"
    blurred_img.save(blurred_path)
    print(f"Blurred receipt image saved to: {blurred_path}")
    
    # Create a rotated version
    rotated_img = receipt_img.rotate(2, expand=True, fillcolor='white')
    rotated_path = "/home/cipher/dev/Cookify/data/sample_receipt_rotated.png"
    rotated_img.save(rotated_path)
    print(f"Rotated receipt image saved to: {rotated_path}")

if __name__ == "__main__":
    main()
