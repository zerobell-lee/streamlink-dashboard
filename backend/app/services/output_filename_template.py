"""
Output filename template engine for generating safe, customizable file names
"""
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class OutputFileNameTemplate:
    """
    Template engine for generating output filenames with variable substitution
    and filesystem safety validation
    """
    
    # Template variable patterns
    TEMPLATE_VARIABLES = {
        # Streamer information
        "streamer_id": r"\{streamer_id\}",
        "streamer_name": r"\{streamer_name\}",
        "platform": r"\{platform\}",
        "title": r"\{title\}",
        "quality": r"\{quality\}",
        
        # Date/time variables
        "yyyy": r"\{yyyy\}",
        "yy": r"\{yy\}",
        "MM": r"\{MM\}",
        "dd": r"\{dd\}",
        "HH": r"\{HH\}",
        "mm": r"\{mm\}",
        "ss": r"\{ss\}",
        "yyyyMMdd": r"\{yyyyMMdd\}",
        "HHmmss": r"\{HHmmss\}",
        "yyyyMMdd_HHmmss": r"\{yyyyMMdd_HHmmss\}",
    }
    
    # Characters that are unsafe for filenames across different filesystems
    UNSAFE_CHARS = r'[<>:"/\\|?*\x00-\x1f]'
    
    # Reserved names on Windows (also good to avoid on other systems)
    RESERVED_NAMES = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
    }
    
    def __init__(self, template: str):
        """
        Initialize template engine with template string
        
        Args:
            template: Template string with variables like {streamer_id}_{yyyyMMdd}
        """
        self.template = template
        self.validate_template()
    
    def validate_template(self) -> None:
        """
        Validate template syntax and variables
        
        Raises:
            ValueError: If template contains invalid variables or syntax
        """
        if not self.template or not isinstance(self.template, str):
            raise ValueError("Template must be a non-empty string")
        
        # Find all template variables in the string
        template_vars = re.findall(r'\{([^}]+)\}', self.template)
        
        # Check if all variables are supported
        for var in template_vars:
            if var not in self.TEMPLATE_VARIABLES:
                raise ValueError(f"Unsupported template variable: {{{var}}}")
    
    def generate_filename(
        self,
        streamer_id: str,
        platform: str,
        quality: str = "best",
        streamer_name: Optional[str] = None,
        title: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        file_extension: str = "mp4"
    ) -> str:
        """
        Generate filename from template with provided data
        
        Args:
            streamer_id: Streamer username/ID
            platform: Platform name (twitch, youtube, etc.)
            quality: Recording quality
            streamer_name: Display name (defaults to streamer_id)
            title: Stream title
            timestamp: Recording timestamp (defaults to now)
            file_extension: File extension without dot
            
        Returns:
            Safe filename string
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if streamer_name is None:
            streamer_name = streamer_id
        
        if title is None:
            title = f"{streamer_name} Stream"
        
        # Create substitution dictionary
        substitutions = {
            "streamer_id": self._sanitize_component(streamer_id),
            "streamer_name": self._sanitize_component(streamer_name),
            "platform": self._sanitize_component(platform),
            "title": self._sanitize_component(title),
            "quality": self._sanitize_component(quality),
            "yyyy": timestamp.strftime("%Y"),
            "yy": timestamp.strftime("%y"),
            "MM": timestamp.strftime("%m"),
            "dd": timestamp.strftime("%d"),
            "HH": timestamp.strftime("%H"),
            "mm": timestamp.strftime("%M"),
            "ss": timestamp.strftime("%S"),
            "yyyyMMdd": timestamp.strftime("%Y%m%d"),
            "HHmmss": timestamp.strftime("%H%M%S"),
            "yyyyMMdd_HHmmss": timestamp.strftime("%Y%m%d_%H%M%S"),
        }
        
        # Perform variable substitution
        filename = self.template
        for var_name, pattern in self.TEMPLATE_VARIABLES.items():
            if var_name in substitutions:
                filename = re.sub(pattern, substitutions[var_name], filename)
        
        # Final sanitization and validation
        filename = self._sanitize_filename(filename)
        
        # Add file extension
        if file_extension and not file_extension.startswith('.'):
            file_extension = f".{file_extension}"
        
        return f"{filename}{file_extension}"
    
    def _sanitize_component(self, component: str) -> str:
        """
        Sanitize individual filename component
        
        Args:
            component: Raw component string
            
        Returns:
            Sanitized component safe for filenames
        """
        if not component:
            return "unknown"
        
        # Remove unsafe characters
        sanitized = re.sub(self.UNSAFE_CHARS, "_", component)
        
        # Trim whitespace and replace with underscores
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        
        # Remove consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Ensure not empty after sanitization
        if not sanitized:
            return "unknown"
        
        return sanitized
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Final filename sanitization and validation
        
        Args:
            filename: Generated filename before extension
            
        Returns:
            Safe filename
        """
        # Basic sanitization
        sanitized = self._sanitize_component(filename)
        
        # Check for reserved names
        name_upper = sanitized.upper()
        if name_upper in self.RESERVED_NAMES:
            sanitized = f"{sanitized}_file"
        
        # Limit length (255 chars is common filesystem limit, leave room for extension)
        if len(sanitized) > 200:
            sanitized = sanitized[:200]
            logger.warning(f"Filename truncated to 200 characters: {sanitized}")
        
        # Ensure not empty
        if not sanitized:
            sanitized = "recording"
        
        return sanitized
    
    def preview_filename(
        self,
        streamer_id: str = "example_streamer",
        platform: str = "twitch",
        quality: str = "1080p",
        streamer_name: Optional[str] = None,
        title: Optional[str] = None,
        file_extension: str = "mp4"
    ) -> str:
        """
        Generate preview filename for UI display
        
        Args:
            streamer_id: Example streamer ID
            platform: Example platform
            quality: Example quality
            streamer_name: Example display name
            title: Example title
            file_extension: Example extension
            
        Returns:
            Preview filename
        """
        return self.generate_filename(
            streamer_id=streamer_id,
            platform=platform,
            quality=quality,
            streamer_name=streamer_name,
            title=title,
            timestamp=datetime(2024, 12, 25, 14, 30, 0),  # Fixed date for consistent preview
            file_extension=file_extension
        )
    
    @classmethod
    def get_available_variables(cls) -> Dict[str, str]:
        """
        Get dictionary of available template variables with descriptions
        
        Returns:
            Dictionary mapping variable names to descriptions
        """
        return {
            "streamer_id": "Streamer username/ID",
            "streamer_name": "Streamer display name",
            "platform": "Platform name (twitch, youtube, etc.)",
            "title": "Stream title (sanitized for filename)",
            "quality": "Recording quality (1080p, 720p, etc.)",
            "yyyy": "4-digit year (2024)",
            "yy": "2-digit year (24)",
            "MM": "2-digit month (01-12)",
            "dd": "2-digit day (01-31)",
            "HH": "2-digit hour 24h format (00-23)",
            "mm": "2-digit minute (00-59)",
            "ss": "2-digit second (00-59)",
            "yyyyMMdd": "Date format YYYYMMDD (20241225)",
            "HHmmss": "Time format HHMMSS (143000)",
            "yyyyMMdd_HHmmss": "Combined datetime (20241225_143000)"
        }
    
    @classmethod
    def get_example_templates(cls) -> Dict[str, str]:
        """
        Get dictionary of example templates with descriptions
        
        Returns:
            Dictionary mapping template names to template strings
        """
        return {
            "Default": "{streamer_id}_{yyyyMMdd}_{HHmmss}",
            "Platform Organized": "{platform}_{streamer_id}_{yyyyMMdd}_{HHmmss}",
            "Detailed": "{streamer_name} - {title} [{quality}] {yyyyMMdd}",
            "Hierarchical": "recordings/{platform}/{streamer_id}/{yyyy}/{MM}/{dd}/stream_{HHmmss}",
            "Simple": "{streamer_id}_{yyyyMMdd_HHmmss}",
            "Quality Focused": "{streamer_id}_{quality}_{yyyyMMdd}_{HHmmss}"
        }


def create_template_engine(template: str) -> OutputFileNameTemplate:
    """
    Factory function to create template engine instance
    
    Args:
        template: Template string
        
    Returns:
        Template engine instance
        
    Raises:
        ValueError: If template is invalid
    """
    return OutputFileNameTemplate(template)