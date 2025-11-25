import re
import ollama
import config

def apply_safety_layer(text):
    """
    Generic safety layer for *any* uploaded book.
    Prevents harmful, hateful, or defamatory outputs.
    """

    # List of harmful content categories (generic, not book-specific)
    blocked_patterns = [
        r"\bhate\b",
        r"\bkill\b",
        r"\bviolence\b",
        r"\bgenocide\b",
        r"\bracial superiority\b",
        r"\betnic cleansing\b"
    ]

    # Remove/soften harmful phrases
    for pattern in blocked_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, "[redacted]", text, flags=re.IGNORECASE)

    # Add a **neutral**, universal ethical footer
    text += "\n\nNote: Interpret all book content responsibly. Context matters, and ideas should be evaluated with respect, accuracy, and fairness."

    return text


def generate_safe_response(prompt, ollama_model=config.OLLAMA_MODEL):
    """Generate response using Ollama + universal safety layer."""

    try:
        response = ollama.generate(
            model=ollama_model,
            prompt=prompt,
            stream=False
        )

        llm_output = response['response']
        safe_output = apply_safety_layer(llm_output)
        return safe_output

    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while generating the response."
