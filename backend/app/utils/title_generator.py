"""
Session title generator utility.
Uses LLM to generate concise, descriptive titles from the first user message.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def generate_session_title(
    user_message: str,
    llm_service = None,
    max_length: int = 50
) -> str:
    """
    Generate a concise session title from the first user message using LLM.
    
    Args:
        user_message: The first user message
        llm_service: LLM service instance (optional)
        max_length: Maximum title length
        
    Returns:
        str: Generated title
    """
    # Fallback if no LLM service provided or message too short
    if not llm_service or len(user_message.strip()) < 5:
        return _generate_fallback_title(user_message, max_length)
    
    try:
        # Create a prompt for title generation
        title_prompt = f"""Generate a very short, concise title (3-6 words maximum) for a conversation that starts with this user message:

"{user_message[:200]}"

The title should:
- Be descriptive but brief (maximum 6 words)
- Capture the main topic or question
- Not include quotes or special characters
- Be suitable as a conversation title

Title:"""
        
        # Try to generate title using LLM
        try:
            # Check if we can use the LLM service
            if hasattr(llm_service, 'generate_answer'):
                # Synchronous call
                generated_title = llm_service.generate_answer(title_prompt, context_docs=[])
            elif hasattr(llm_service, 'chat'):
                # Alternative method
                response, _ = llm_service.chat_with_metadata(title_prompt)
                generated_title = response
            else:
                logger.warning("LLM service doesn't have expected methods, using fallback")
                return _generate_fallback_title(user_message, max_length)
            
            # Clean up the generated title
            title = generated_title.strip()
            
            # Remove quotes if present
            if title.startswith('"') and title.endswith('"'):
                title = title[1:-1]
            if title.startswith("'") and title.endswith("'"):
                title = title[1:-1]
            
            # Remove common prefixes
            prefixes_to_remove = [
                "Title:",
                "title:",
                "Session:",
                "session:",
                "Conversation:",
                "conversation:"
            ]
            for prefix in prefixes_to_remove:
                if title.startswith(prefix):
                    title = title[len(prefix):].strip()
            
            # Truncate if too long
            if len(title) > max_length:
                title = title[:max_length].rsplit(' ', 1)[0] + "..."
            
            # Validate title is not empty
            if not title or len(title) < 3:
                return _generate_fallback_title(user_message, max_length)
            
            logger.info(f"Generated title: {title}")
            return title
            
        except Exception as e:
            logger.warning(f"LLM title generation failed: {e}, using fallback")
            return _generate_fallback_title(user_message, max_length)
            
    except Exception as e:
        logger.error(f"Error in generate_session_title: {e}")
        return _generate_fallback_title(user_message, max_length)


def _generate_fallback_title(user_message: str, max_length: int = 50) -> str:
    """
    Generate a fallback title from the user message.
    
    Args:
        user_message: User message
        max_length: Maximum title length
        
    Returns:
        str: Fallback title
    """
    # Clean the message
    title = user_message.strip()
    
    # Remove line breaks
    title = ' '.join(title.split('\n'))
    
    # Truncate if too long
    if len(title) > max_length:
        # Try to truncate at a word boundary
        title = title[:max_length].rsplit(' ', 1)[0] + "..."
    
    # If still empty or too short, use default
    if not title or len(title) < 3:
        return "New Conversation"
    
    return title


def should_generate_title(session_message_count: int) -> bool:
    """
    Determine if a title should be generated for a session.
    Typically only generate on the first user message.
    
    Args:
        session_message_count: Current number of messages in the session
        
    Returns:
        bool: True if title should be generated
    """
    # Generate title only for the first message (count = 0 before adding)
    return session_message_count == 0
