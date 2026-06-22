def generate_title(message: str, max_len: int = 30) -> str:
    """Generate a title from the first user message."""
    if not message:
        return "New Chat"
    title = message.strip().replace("\n", " ")
    return title[:max_len] + "..." if len(title) > max_len else title