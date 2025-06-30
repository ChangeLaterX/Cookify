#!/usr/bin/env python3
"""
Endpoint Configuration Demonstration.

This script shows how all API endpoints can be configured centrally
through the settings in core/config.py. This allows for easy customization
of endpoint paths, titles, and descriptions without changing the route code.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings


def show_all_endpoint_configurations():
    """Display all configurable endpoint settings."""

    print("=" * 80)
    print("COOKIFY API - CENTRALIZED ENDPOINT CONFIGURATION")
    print("=" * 80)
    print()

    # Health Endpoints
    print("🔹 HEALTH ENDPOINTS")
    print(f"   Prefix: {settings.HEALTH_PREFIX}")
    print(f"   Tag: {settings.HEALTH_TAG}")
    print()
    health_endpoints = [
        (settings.HEALTH_ROOT_ENDPOINT, settings.HEALTH_ROOT_TITLE),
        (settings.HEALTH_QUICK_ENDPOINT, settings.HEALTH_QUICK_TITLE),
        (settings.HEALTH_LIVENESS_ENDPOINT, settings.HEALTH_LIVENESS_TITLE),
        (settings.HEALTH_READINESS_ENDPOINT, settings.HEALTH_READINESS_TITLE),
        (settings.HEALTH_METRICS_ENDPOINT, settings.HEALTH_METRICS_TITLE),
        (settings.HEALTH_ALERTS_ENDPOINT, settings.HEALTH_ALERTS_TITLE),
        (
            settings.HEALTH_SERVICE_HISTORY_ENDPOINT,
            settings.HEALTH_SERVICE_HISTORY_TITLE,
        ),
    ]

    for endpoint, title in health_endpoints:
        full_path = (
            settings.HEALTH_PREFIX + endpoint
            if endpoint != "/"
            else settings.HEALTH_PREFIX + endpoint
        )
        print(f"   GET {full_path:<50} - {title}")
    print()

    # Ingredients Endpoints
    print("🔹 INGREDIENTS ENDPOINTS")
    print(f"   Prefix: {settings.INGREDIENTS_PREFIX}")
    print(f"   Tag: {settings.INGREDIENTS_TAG}")
    print()
    ingredients_endpoints = [
        (
            settings.INGREDIENTS_MASTER_ENDPOINT,
            "GET",
            settings.INGREDIENTS_MASTER_LIST_TITLE,
        ),
        (
            settings.INGREDIENTS_MASTER_BY_ID_ENDPOINT,
            "GET",
            settings.INGREDIENTS_MASTER_GET_TITLE,
        ),
        (
            settings.INGREDIENTS_MASTER_ENDPOINT,
            "POST",
            settings.INGREDIENTS_MASTER_CREATE_TITLE,
        ),
        (
            settings.INGREDIENTS_MASTER_BY_ID_ENDPOINT,
            "PUT",
            settings.INGREDIENTS_MASTER_UPDATE_TITLE,
        ),
        (
            settings.INGREDIENTS_MASTER_BY_ID_ENDPOINT,
            "DELETE",
            settings.INGREDIENTS_MASTER_DELETE_TITLE,
        ),
        (
            settings.INGREDIENTS_SEARCH_ENDPOINT,
            "GET",
            settings.INGREDIENTS_SEARCH_TITLE,
        ),
        (
            settings.INGREDIENTS_PANTRY_ENDPOINT,
            "GET",
            settings.INGREDIENTS_PANTRY_LIST_TITLE,
        ),
        (
            settings.INGREDIENTS_PANTRY_ENDPOINT,
            "POST",
            settings.INGREDIENTS_PANTRY_CREATE_TITLE,
        ),
        (
            settings.INGREDIENTS_PANTRY_BY_ID_ENDPOINT,
            "PUT",
            settings.INGREDIENTS_PANTRY_UPDATE_TITLE,
        ),
        (
            settings.INGREDIENTS_PANTRY_BY_ID_ENDPOINT,
            "DELETE",
            settings.INGREDIENTS_PANTRY_DELETE_TITLE,
        ),
        (
            settings.INGREDIENTS_SHOPPING_LIST_ENDPOINT,
            "GET",
            settings.INGREDIENTS_SHOPPING_LIST_TITLE,
        ),
        (
            settings.INGREDIENTS_SHOPPING_LIST_ENDPOINT,
            "POST",
            settings.INGREDIENTS_SHOPPING_ADD_TITLE,
        ),
        (
            settings.INGREDIENTS_SHOPPING_LIST_BY_ID_ENDPOINT,
            "PUT",
            settings.INGREDIENTS_SHOPPING_UPDATE_TITLE,
        ),
        (
            settings.INGREDIENTS_SHOPPING_LIST_BY_ID_ENDPOINT,
            "DELETE",
            settings.INGREDIENTS_SHOPPING_DELETE_TITLE,
        ),
        (
            settings.INGREDIENTS_CACHE_UPDATE_ENDPOINT,
            "POST",
            settings.INGREDIENTS_CACHE_UPDATE_TITLE,
        ),
    ]

    for endpoint, method, title in ingredients_endpoints:
        full_path = settings.INGREDIENTS_PREFIX + endpoint
        print(f"   {method:<6} {full_path:<50} - {title}")
    print()

    # OCR Endpoints
    print("🔹 OCR ENDPOINTS")
    print(f"   Prefix: {settings.OCR_PREFIX}")
    print(f"   Tag: {settings.OCR_TAG}")
    print()
    ocr_endpoints = [
        (settings.OCR_EXTRACT_TEXT_ENDPOINT, "POST", settings.OCR_EXTRACT_TEXT_TITLE),
        (
            settings.OCR_PROCESS_RECEIPT_ENDPOINT,
            "POST",
            settings.OCR_PROCESS_RECEIPT_TITLE,
        ),
        (settings.OCR_HEALTH_CHECK_ENDPOINT, "GET", settings.OCR_HEALTH_CHECK_TITLE),
    ]

    for endpoint, method, title in ocr_endpoints:
        full_path = settings.OCR_PREFIX + endpoint
        print(f"   {method:<6} {full_path:<50} - {title}")
    print()

    # Auth Endpoints
    print("🔹 AUTHENTICATION ENDPOINTS")
    print(f"   Prefix: {settings.AUTH_PREFIX}")
    print(f"   Tag: {settings.AUTH_TAG}")
    print()
    auth_endpoints = [
        (settings.AUTH_REGISTER_ENDPOINT, "POST", settings.AUTH_REGISTER_TITLE),
        (settings.AUTH_LOGIN_ENDPOINT, "POST", settings.AUTH_LOGIN_TITLE),
        (settings.AUTH_LOGOUT_ENDPOINT, "POST", settings.AUTH_LOGOUT_TITLE),
        (settings.AUTH_REFRESH_ENDPOINT, "POST", settings.AUTH_REFRESH_TITLE),
        (
            settings.AUTH_RESET_PASSWORD_ENDPOINT,
            "POST",
            settings.AUTH_RESET_PASSWORD_TITLE,
        ),
        (settings.AUTH_VERIFY_EMAIL_ENDPOINT, "POST", settings.AUTH_VERIFY_EMAIL_TITLE),
        (settings.AUTH_PROFILE_ENDPOINT, "GET", settings.AUTH_PROFILE_TITLE),
    ]

    for endpoint, method, title in auth_endpoints:
        full_path = settings.AUTH_PREFIX + endpoint
        print(f"   {method:<6} {full_path:<50} - {title}")
    print()

    # Update Endpoints
    print("🔹 UPDATE ENDPOINTS")
    print(f"   Prefix: {settings.UPDATE_PREFIX}")
    print(f"   Tag: {settings.UPDATE_TAG}")
    print()
    update_endpoints = [
        (
            settings.UPDATE_INGREDIENT_CACHE_ENDPOINT,
            "POST",
            settings.UPDATE_INGREDIENT_CACHE_TITLE,
        ),
        (
            settings.UPDATE_INGREDIENT_CACHE_STATUS_ENDPOINT,
            "GET",
            settings.UPDATE_INGREDIENT_CACHE_STATUS_TITLE,
        ),
        (settings.UPDATE_ALL_CACHES_ENDPOINT, "POST", settings.UPDATE_ALL_CACHES_TITLE),
    ]

    for endpoint, method, title in update_endpoints:
        full_path = settings.UPDATE_PREFIX + endpoint
        print(f"   {method:<6} {full_path:<50} - {title}")
    print()


def show_customization_examples():
    """Show examples of how to customize endpoint configurations."""

    print("=" * 80)
    print("ENDPOINT CUSTOMIZATION EXAMPLES")
    print("=" * 80)
    print()

    print("To customize endpoints, modify the values in core/config.py:")
    print()

    print("🔧 EXAMPLE 1: Change Health Endpoints to Status")
    print("   HEALTH_PREFIX: str = '/status'  # Instead of '/health'")
    print("   HEALTH_TAG: str = 'System Status'  # Instead of 'Health'")
    print("   HEALTH_QUICK_ENDPOINT: str = '/ping'  # Instead of '/quick'")
    print()

    print("🔧 EXAMPLE 2: Localize Endpoint Titles (German)")
    print("   HEALTH_ROOT_TITLE: str = 'Umfassende Systemprüfung'")
    print("   HEALTH_QUICK_TITLE: str = 'Schnelle Systemprüfung'")
    print("   INGREDIENTS_SEARCH_TITLE: str = 'Zutaten suchen'")
    print()

    print("🔧 EXAMPLE 3: API Versioning")
    print("   HEALTH_PREFIX: str = '/api/v2/health'")
    print("   INGREDIENTS_PREFIX: str = '/api/v2/ingredients'")
    print("   OCR_PREFIX: str = '/api/v2/ocr'")
    print()

    print("🔧 EXAMPLE 4: Alternative Endpoint Paths")
    print("   INGREDIENTS_MASTER_ENDPOINT: str = '/catalog'  # Instead of '/master'")
    print("   INGREDIENTS_SEARCH_ENDPOINT: str = '/find'  # Instead of '/search'")
    print("   OCR_EXTRACT_TEXT_ENDPOINT: str = '/read'  # Instead of '/extract-text'")
    print()

    print("🔧 EXAMPLE 5: Kubernetes-Style Paths")
    print("   HEALTH_LIVENESS_ENDPOINT: str = '/livez'")
    print("   HEALTH_READINESS_ENDPOINT: str = '/readyz'")
    print("   HEALTH_METRICS_ENDPOINT: str = '/metricz'")
    print()


def show_environment_overrides():
    """Show how to override endpoint settings with environment variables."""

    print("=" * 80)
    print("ENVIRONMENT VARIABLE OVERRIDES")
    print("=" * 80)
    print()

    print("You can override any endpoint setting using environment variables:")
    print()

    print("🌍 EXAMPLES:")
    print("   export HEALTH_PREFIX='/api/status'")
    print("   export INGREDIENTS_TAG='Food Items'")
    print("   export OCR_EXTRACT_TEXT_TITLE='Scan Receipt Text'")
    print("   export AUTH_LOGIN_ENDPOINT='/signin'")
    print()

    print("🐳 DOCKER ENVIRONMENT:")
    print("   docker run -e HEALTH_PREFIX='/status' -e INGREDIENTS_PREFIX='/food' cookify-backend")
    print()

    print("📝 .ENV FILE:")
    print("   HEALTH_PREFIX=/monitoring")
    print("   HEALTH_TAG=System Monitoring")
    print("   INGREDIENTS_PREFIX=/api/v1/food")
    print()


def main():
    """Main demonstration function."""
    show_all_endpoint_configurations()
    show_customization_examples()
    show_environment_overrides()

    print("=" * 80)
    print("✅ ALL ENDPOINTS ARE NOW CENTRALLY CONFIGURABLE!")
    print("=" * 80)
    print()
    print("Benefits:")
    print("• 🔧 Easy customization without code changes")
    print("• 🌍 Environment-specific endpoint paths")
    print("• 🏷️  Consistent API documentation")
    print("• 🚀 Simplified deployment configurations")
    print("• 🔄 Easy A/B testing of API designs")
    print("• 🌐 Localization support for titles/descriptions")
    print()


if __name__ == "__main__":
    main()
