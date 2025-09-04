"""
Platform definitions package

All platform definitions are automatically imported and registered here
"""

# Import all platform definitions to trigger registration
from . import twitch
from . import youtube  
from . import sooplive
from . import chzzk

# Make definitions available for import
__all__ = [
    "twitch",
    "youtube", 
    "sooplive",
    "chzzk"
]