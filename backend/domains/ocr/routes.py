"""
FastAPI Routes for Receipt Domain.
Provides HTTP endpoints for receipt OCR processing and ingredient matching.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.responses import JSONResponse

from .schemas import (
    OCRTextResponse,
    OCRProcessedResponse,
    OCRApiResponse,
    MessageResponse,
    ErrorResponse,
)
from .services import (
    extract_text_from_image,
    process_receipt_image,
    OCRError,
)

logger = logging.getLogger(__name__)

# Create router for receipt endpoints
router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post(
    "/extract-text",
    response_model=OCRTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract text from receipt image",
    description="Extract raw text from receipt image using OCR",
)
async def extract_receipt_text(
    image: UploadFile = File(..., description="Receipt image file"),
) -> OCRTextResponse:
    """
    Extract raw text from receipt image using OCR.

    Args:
        image: Uploaded image file (JPEG, PNG, etc.)

    Returns:
        OCRTextResponse with extracted text and metadata

    Raises:
        HTTPException: 400 if file invalid, 500 if OCR processing fails
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "File must be an image",
                    "error_code": "INVALID_FILE_TYPE",
                },
            )

        # Read image data
        image_data = await image.read()

        if len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Empty file uploaded", "error_code": "EMPTY_FILE"},
            )

        logger.info(
            f"Processing OCR for image: {image.filename} ({len(image_data)} bytes)"
        )

        # Extract text using OCR
        result = await extract_text_from_image(image_data)

        logger.info(
            f"OCR text extraction completed: {len(result.extracted_text)} characters"
        )
        return result

    except OCRError as e:
        logger.error(f"OCR error processing {image.filename}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error processing {image.filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error", "error_code": "INTERNAL_ERROR"},
        )


@router.post(
    "/process",
    response_model=OCRApiResponse,
    status_code=status.HTTP_200_OK,
    summary="Process receipt with ingredient suggestions",
    description="Extract text from receipt and provide ingredient matching suggestions",
)
async def process_receipt_with_ocr(
    image: UploadFile = File(..., description="Receipt image file"),
) -> OCRApiResponse:
    """
    Process receipt image and provide ingredient suggestions.

    Args:
        image: Uploaded image file (JPEG, PNG, etc.)

    Returns:
        OCRApiResponse with processed items and ingredient suggestions

    Raises:
        HTTPException: 400 if file invalid, 500 if processing fails
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "File must be an image",
                    "error_code": "INVALID_FILE_TYPE",
                },
            )

        # Read image data
        image_data = await image.read()

        if len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Empty file uploaded", "error_code": "EMPTY_FILE"},
            )

        logger.info(
            f"Processing receipt with OCR: {image.filename} ({len(image_data)} bytes)"
        )

        # Process receipt with ingredient suggestions
        result = await process_receipt_image(image_data)

        logger.info(
            f"Receipt processing completed: {result.total_items_detected} items detected"
        )

        return OCRApiResponse(
            success=True,
            data=result,
            message=f"Receipt processed successfully. Found {result.total_items_detected} items.",
            error=None,
        )

    except OCRError as e:
        logger.error(f"OCR error processing receipt {image.filename}: {e.message}")
        return OCRApiResponse(
            success=False,
            data=None,
            message="Failed to process receipt",
            error=f"{e.message} ({e.error_code})",
        )
    except Exception as e:
        logger.error(f"Unexpected error processing receipt {image.filename}: {str(e)}")
        return OCRApiResponse(
            success=False,
            data=None,
            message="Failed to process receipt",
            error="Internal server error",
        )
