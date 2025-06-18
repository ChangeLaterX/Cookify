# Backend Scripts

This folder contains scripts that are executed when the FastAPI application starts. The scripts are responsible for loading data, initializing files, and other startup tasks.

## Overview

### Files

- **`__init__.py`** - Package initialization
- **`startup.py`** - Main manager for startup scripts
- **`ingredient_file_manager.py`** - Manages ingredient names file with weekly auto-updates
- **`test_integration.py`** - Tests for the ingredient file system
- **`simple_ocr_example.py`** - Example of how to use the ingredient file for OCR matching
- **`README.md`** - This documentation

## Ingredient Names File System

### Purpose

The `ingredient_file_manager.py` script creates and maintains a simple text file (`data/ingredient_names.txt`) containing all ingredient names from the Supabase database. This file is used for OCR matching and is automatically updated once per week.

### Functionality

- **Automatic File Creation**: On FastAPI startup, ensures the ingredient file exists and is current
- **Weekly Updates**: File is automatically refreshed every 7 days
- **Simple Text Format**: Easy-to-read file with one ingredient name per line
- **Metadata Tracking**: Maintains update timestamps and ingredient count
- **OCR Integration**: Ready for matching OCR-recognized text against known ingredients
- **Health Check Integration**: File status is monitored via `/api/health/` endpoint

### Main Functions

```python
# Initialize/update ingredient file at startup
success = await initialize_ingredient_file()

# Get all ingredient names from file
ingredient_names = get_ingredient_names()

# Check file status for monitoring
status = get_ingredient_file_status()
```

## File Structure

The ingredient file (`data/ingredient_names.txt`) has a simple format:

```
# Cookify Ingredient Names
# Generated: 2025-06-18T13:51:19.195669
# Total ingredients: 850
# Auto-updated weekly

Almond Milk
Apples
Avocado
Banana
Black Beans
...
```

## Health Check Integration

The ingredient file status is integrated into the health check system under the "cache" section:

```json
{
  "name": "cache",
  "status": "healthy",
  "message": "Ingredient file cache is healthy",
  "details": {
    "file_exists": "True",
    "file_path": "data/ingredient_names.txt",
    "last_updated": "2025-06-18T13:51:19.195669",
    "ingredient_count": "850",
    "needs_update": "False",
    "update_interval_days": "7"
  }
}
```

Check via: `GET /api/health/` - look for the service with `name: "cache"`

## Startup Manager

### Concept

The `StartupScriptManager` manages the execution of all startup scripts:

1. Scripts are registered
2. On FastAPI startup, all scripts are executed
3. Results are logged and can be monitored

### Adding New Scripts

1. Create script function (must be `async` and return `bool`)
2. Register in `register_startup_scripts()`:

```python
def register_startup_scripts() -> None:
    startup_manager.register_script(initialize_ingredient_file)
    startup_manager.register_script(your_new_script)  # Add here
```

## For OCR Integration

### Usage Example

When OCR matching is implemented, you can use these functions:

```python
from scripts.ingredient_file_manager import get_ingredient_names

# In OCR service:
def match_ocr_to_ingredients(ocr_text: str) -> List[str]:
    # Get all known ingredients from file
    known_ingredients = get_ingredient_names()
    
    # Implement fuzzy matching logic here
    matches = []
    for ingredient in known_ingredients:
        if ingredient.lower() in ocr_text.lower():
            matches.append(ingredient)
    
    return matches
```

### File Management

The file is automatically managed:
- Created/updated on startup if needed
- Checked weekly for updates
- Contains metadata about last update
- Monitored via health checks

## Logging

All script activities are logged:
- Startup success/errors
- File operations
- Database access
- Performance metrics

## Error Handling

- Scripts can fail individually without stopping the entire application
- Errors are logged but not fatal
- File errors lead to warnings, not crashes
- Fallback mechanisms for critical operations

## Next Steps

1. **OCR Integration**: Use the ingredient names file in the OCR service
2. **Fuzzy Matching**: Implement advanced string matching algorithms
3. **Performance Optimization**: Optimize file reading strategies
4. **Additional Files**: Create similar scripts for other data types

## Testing

Run the integration test to verify the system:

```bash
cd backend
python scripts/test_integration.py
```

This will test file creation, updates, and verification of content.
