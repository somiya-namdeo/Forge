import logging
from app.processing.extractor import ContentExtractor
from app.processing.cleaner import ContentCleaner
from app.processing.normalizer import ContentNormalizer
from app.processing.markdown_converter import MarkdownConverter
from app.processing.metadata import MetadataGenerator
from app.processing.models import ProcessedDocument
from app.storage.base import BaseStorage
from app.processing.exceptions import ProcessingError

# TODO: Initialize processing logger here when implementing (e.g. logger = logging.getLogger("forge.processing"))

class DocumentPipeline:
    """
    Orchestrates the document processing workflow:
    Raw HTML -> Extract -> Clean -> Normalize -> Markdown -> Metadata -> Save Processed Files
    
    Storage integration is performed exclusively via the BaseStorage interface.
    """
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.extractor = ContentExtractor()
        self.cleaner = ContentCleaner()
        self.normalizer = ContentNormalizer()
        self.converter = MarkdownConverter()
        self.metadata_generator = MetadataGenerator()
        
    async def process_document(self, raw_html: str, original_url: str) -> ProcessedDocument:
        """
        Runs the full processing pipeline on a raw HTML document.
        
        Args:
            raw_html: The raw downloaded HTML.
            original_url: The URL the document was fetched from.
            
        Returns:
            ProcessedDocument containing the markdown and metadata.
            
        Raises:
            ProcessingError: If any stage of the pipeline fails.
        """
        # TODO: Add logging hooks before and after each processing stage.
        # e.g., logger.debug("Extracting content from HTML")
        
        raise NotImplementedError("Pipeline orchestration is not yet implemented.")
