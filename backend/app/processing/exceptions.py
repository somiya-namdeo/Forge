class ProcessingError(Exception):
    """Base exception for all processing-related errors."""
    pass

class ExtractionError(ProcessingError):
    """Raised when HTML extraction fails."""
    pass

class ConversionError(ProcessingError):
    """Raised when Markdown conversion fails."""
    pass
