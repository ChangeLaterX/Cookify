# OCR Test Images for Cookify

This directory contains sample images for testing OCR (Optical Character Recognition) functionality in the Cookify application.

## Generated Images

### Receipt Images
- **`sample_receipt.png`** - Clean grocery receipt with various food items
- **`sample_receipt_blurred.png`** - Slightly blurred version to test OCR robustness
- **`sample_receipt_rotated.png`** - Slightly rotated version to test OCR alignment

### Shopping List Images
- **`sample_shopping_list.png`** - Handwritten-style shopping list with checkboxes

## Image Content

### Receipt Content
The receipt contains typical grocery items that would be relevant for a cooking app:
- Fresh vegetables (tomatoes, onions, garlic, bell peppers, carrots, potatoes, spinach)
- Fruits (bananas, apples)
- Proteins (chicken breast, ground beef, salmon)
- Dairy (milk, eggs, cheese)
- Pantry staples (bread, rice, pasta, olive oil, salt, pepper, basil)

### Shopping List Content
The shopping list contains similar ingredients organized in a checkbox format.

## Usage for OCR Testing

These images can be used to test:
1. **Text extraction** - Reading ingredient names and quantities
2. **Price parsing** - Extracting cost information from receipts
3. **Format recognition** - Distinguishing between receipts and shopping lists
4. **Robustness testing** - Handling blurred or rotated images
5. **Layout analysis** - Understanding receipt structure and item organization

## Generating New Images

You can regenerate these images by running:
```bash
python3 generate_receipt_image.py
python3 generate_shopping_list.py
```

## OCR Integration Ideas

For the Cookify backend, these images could be used to test:
- Automatic ingredient detection from receipt photos
- Shopping list digitization
- Price tracking and budgeting features
- Inventory management from receipt scanning
- Recipe suggestions based on purchased ingredients

## File Formats

All images are saved as PNG files for optimal OCR quality while maintaining reasonable file sizes.
