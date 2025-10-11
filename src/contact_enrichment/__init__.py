"""
Contact Enrichment Module
Module 010: Contact Enrichment

Main entry point for contact enrichment functionality.
"""

from .contact_enricher import ContactEnricher
from .models.contact_info import ContactInfo
from .models.enrichment_result import EnrichmentResult

__all__ = ["ContactEnricher", "ContactInfo", "EnrichmentResult"]
