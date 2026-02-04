"""Claw City - Modular Pipeline for AI-Generated Comedy Show"""

import logging

__version__ = "2.0.0"
__author__ = "Claw City Team"

# Konfiguration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Nutzung
logger = logging.getLogger(__name__)
logger.debug("Debug-Information")
logger.info("Normale Operation")
logger.warning("Warnung")
logger.error("Fehler aufgetreten")
# logger.exception("Fehler mit Stack-Trace")  # Nur in except-Block
