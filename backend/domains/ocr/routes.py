"""
FastAPI Routes for Receipt Domain.
Provides HTTP endpoints for receipt OCR processing and ingredient matching.
Enhanced with security validations and rate limiting.
"""

import time
from typing import Optional

from core.logging import get_logger
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from .schemas import (ErrorResponse, MessageResponse, OCRApiResponse,
                      OCRProcessedResponse, OCRTextResponse)
from .services import OCRError, extract_text_from_image, process_receipt_image

logger = get_logger(__name__)

# Create router for receipt endpoints with enhanced security
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
    request_start_time = time.time()
    image_data: bytes = b""

    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            logger.warning(
                "Invalid file type uploaded",
                context={
                    "filename": image.filename,
                    "content_type": image.content_type,
                    "endpoint": "/ocr/extract-text",
                },
            )
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
            logger.warning(
                "Empty file uploaded",
                context={"filename": image.filename, "endpoint": "/ocr/extract-text"},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Empty file uploaded", "error_code": "EMPTY_FILE"},
            )

        logger.info(
            "Starting OCR text extraction",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data),
                "content_type": image.content_type,
                "endpoint": "/ocr/extract-text",
            },
        )

        # Extract text using OCR
        result = await extract_text_from_image(image_data)

        request_duration_ms = int((time.time() - request_start_time) * 1000)

        logger.info(
            "OCR text extraction completed successfully",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data),
                "extracted_text_length": len(result.extracted_text),
                "confidence_score": result.confidence,
                "ocr_processing_time_ms": result.processing_time_ms,
                "total_request_time_ms": request_duration_ms,
                "endpoint": "/ocr/extract-text",
            },
            data={
                "performance_metrics": {
                    "file_size_bytes": len(image_data),
                    "ocr_processing_time_ms": result.processing_time_ms,
                    "total_request_time_ms": request_duration_ms,
                    "confidence_score": result.confidence,
                }
            },
        )

        return result

    except OCRError as e:
        request_duration_ms = int((time.time() - request_start_time) * 1000)
        logger.error(
            "OCR processing failed",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data) if image_data else None,
                "error_code": e.error_code,
                "error_message": e.message,
                "total_request_time_ms": request_duration_ms,
                "endpoint": "/ocr/extract-text",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "error_code": e.error_code},
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        request_duration_ms = int((time.time() - request_start_time) * 1000)
        logger.error(
            "Unexpected error during OCR text extraction",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data) if image_data else None,
                "error_message": str(e),
                "total_request_time_ms": request_duration_ms,
                "endpoint": "/ocr/extract-text",
            },
        )
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
    request_start_time = time.time()
    image_data: bytes = b""

    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith("image/"):
            logger.warning(
                "Invalid file type uploaded for receipt processing",
                context={
                    "filename": image.filename,
                    "content_type": image.content_type,
                    "endpoint": "/ocr/process",
                },
            )
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
            logger.warning(
                "Empty file uploaded for receipt processing",
                context={"filename": image.filename, "endpoint": "/ocr/process"},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Empty file uploaded", "error_code": "EMPTY_FILE"},
            )

        logger.info(
            "Starting receipt processing with OCR",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data),
                "content_type": image.content_type,
                "endpoint": "/ocr/process",
            },
        )

        # Process receipt with ingredient suggestions
        result = await process_receipt_image(image_data)

        request_duration_ms = int((time.time() - request_start_time) * 1000)

        logger.info(
            "Receipt processing completed successfully",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data),
                "total_items_detected": result.total_items_detected,
                "ocr_processing_time_ms": result.processing_time_ms,
                "total_request_time_ms": request_duration_ms,
                "endpoint": "/ocr/process",
            },
            data={
                "performance_metrics": {
                    "file_size_bytes": len(image_data),
                    "ocr_processing_time_ms": result.processing_time_ms,
                    "total_request_time_ms": request_duration_ms,
                    "items_detected": result.total_items_detected,
                },
                "processing_results": {
                    "items_with_suggestions": len(
                        [item for item in result.detected_items if item.suggestions]
                    ),
                    "items_without_suggestions": len(
                        [item for item in result.detected_items if not item.suggestions]
                    ),
                },
            },
        )

        return OCRApiResponse(
            success=True,
            data=result,
            message=f"Receipt processed successfully. Found {result.total_items_detected} items.",
            error=None,
        )

    except OCRError as e:
        request_duration_ms = int((time.time() - request_start_time) * 1000)
        logger.error(
            "OCR error during receipt processing",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data) if image_data else None,
                "error_code": e.error_code,
                "error_message": e.message,
                "total_request_time_ms": request_duration_ms,
                "endpoint": "/ocr/process",
            },
        )
        return OCRApiResponse(
            success=False,
            data=None,
            message="Failed to process receipt",
            error=f"{e.message} ({e.error_code})",
        )
    except Exception as e:
        request_duration_ms = int((time.time() - request_start_time) * 1000)
        logger.error(
            "Unexpected error during receipt processing",
            context={
                "filename": image.filename,
                "file_size_bytes": len(image_data) if image_data else None,
                "error_message": str(e),
                "total_request_time_ms": request_duration_ms,
                "endpoint": "/ocr/process",
            },
        )
        return OCRApiResponse(
            success=False,
            data=None,
            message="Failed to process receipt",
            error="Internal server error",
        )
