class ContentExtractor:
    """
    Responsible for extracting the core content from raw HTML,
    stripping away navbars, footers, and sidebars.
    
    Future Implementation Notes:
    - Likely will use Readability.js ported to Python (e.g. readability-lxml).
    - Or specific heuristics for documentation sites (Sphinx, Docusaurus).
    """
    
    def extract(self, raw_html: str) -> str:
        """
        Extracts the main content block from the raw HTML.
        
        Args:
            raw_html: The complete downloaded HTML document.
            
        Returns:
            A string containing only the HTML of the main content area.
            
        Raises:
            ExtractionError: If the main content cannot be identified.
        """
        # TODO: Implement HTML extraction logic
        raise NotImplementedError("HTML extraction is not yet implemented.")
