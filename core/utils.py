EMERGENCY_KEYWORDS = ['urgent', 'immediately', 'danger', 'harassment', 'threat', 'emergency', 'violence', 'abuse']

def detect_emergency(text: str) -> bool:
    text_lower = text.lower()
    return any(word in text_lower for word in EMERGENCY_KEYWORDS)