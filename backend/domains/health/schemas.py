"""
Pydantic Schemas for Health Domain.
Defines request/response models for health check endpoints.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class ServiceStatus(str, Enum):
    """Enum for service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServiceHealthStatus(BaseModel):
    """Schema for individual service health status."""
    
    name: str = Field(..., description="Service name")
    status: ServiceStatus = Field(..., description="Service health status")
    message: str = Field(..., description="Health status message")
    response_time_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    details: Optional[Dict[str, str]] = Field(None, description="Additional service details")
    error: Optional[str] = Field(None, description="Error message if unhealthy")


class HealthResponse(BaseModel):
    """Schema for basic health check response."""
    
    status: ServiceStatus = Field(..., description="Overall system health status")
    message: str = Field(..., description="Overall health message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")


class DetailedHealthResponse(BaseModel):
    """Schema for detailed health check response with all services."""
    
    status: ServiceStatus = Field(..., description="Overall system health status")
    message: str = Field(..., description="Overall health message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    services: List[ServiceHealthStatus] = Field(..., description="Individual service health statuses")
    system_info: Dict[str, str] = Field(..., description="System information")
    uptime_seconds: Optional[int] = Field(None, description="Application uptime in seconds")


# Export schemas
__all__ = [
    "ServiceStatus",
    "ServiceHealthStatus", 
    "HealthResponse",
    "DetailedHealthResponse",
]
