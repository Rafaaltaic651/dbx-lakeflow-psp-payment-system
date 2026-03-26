import logging
import sys

# Suppress noisy Azure/HTTP credential logs before any imports
logging.getLogger("azure").setLevel(logging.ERROR)
logging.getLogger("azure.identity").setLevel(logging.ERROR)
logging.getLogger("azure.core").setLevel(logging.ERROR)
logging.getLogger("msal").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

from cli.app import app

app()
