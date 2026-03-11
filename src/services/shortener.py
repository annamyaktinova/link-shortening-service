import random
import string

def generate_short_code(length: int = 6) -> str:
    """Generate a short random alphanumeric code (used as short URL)."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for _ in range(length))