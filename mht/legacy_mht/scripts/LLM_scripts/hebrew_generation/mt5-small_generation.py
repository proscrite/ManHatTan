import requests

from bidi.algorithm import get_display
HUGGINGFACE_API_TOKEN = "here_your_huggingface_token"  # Replace with your actual token
API_URL = "https://api-inference.huggingface.co/models/google/mt5-small"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}


def generate_claw_sentence(hebrew_word):
    prompt = (
        f"Generate a Hebrew sentence using the word '{hebrew_word}' "
        "and replace that word with a blank (___)."
    )

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 50,
            "do_sample": True,
            "top_p": 0.9,
            "temperature": 0.7,
        }
    }

    print(f"Prompt sent to model: {prompt}")

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None

    result = response.json()

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    else:
        print("Unexpected response format:", result)
        return None


if __name__ == "__main__":
    word = input("Enter a Hebrew word (e.g., המלצה): ")
    word = get_display(word)  # Ensure the word is displayed correctly in Hebrew
    print(f"Generating sentence for the word: {word}")
    sentence = generate_claw_sentence(word)
    if sentence:
        print("\n Generated CLAW Sentence:")
        print(sentence)
