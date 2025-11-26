import re
import openai
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


def generate_safe_response(prompt, api_model=config.API_MODEL):
    """Generate response using OpenAI-compatible API + universal safety layer."""

    try:
        # Initialize OpenAI client with custom base URL and API key
        client = openai.OpenAI(
            api_key=config.API_KEY,
            base_url=config.API_BASE_URL
        )

        # Call the API with chat completions
        response = client.chat.completions.create(
            model=api_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        llm_output = response.choices[0].message.content
        safe_output = apply_safety_layer(llm_output)
        return safe_output

    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while generating the response."
