from app.processing.exceptions import ConversionError

class MarkdownConverter:
    """
    Converts normalized HTML into clean, semantically correct Markdown.
    
    Future Implementation Notes:
    - Will likely use `markdownify` or `html2text`.
    - Must preserve code blocks and tables perfectly.
    """
    
    def convert(self, html: str) -> str:
        """
        Converts HTML to Markdown.
        
        Args:
            html: Normalized HTML string.
            
        Returns:
            Markdown formatted string.
            
        Raises:
            ConversionError: If the conversion process fails.
        """
        # TODO: Implement HTML to Markdown logic
        raise NotImplementedError("Markdown conversion is not yet implemented.")
