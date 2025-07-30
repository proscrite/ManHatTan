import requests
API_URL = "https://api-inference.huggingface.co/models/distilgpt2"
HF_TOKEN = "here_your_huggingface_token"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}
def gen_en_sentence_api(word):
    prompt = f'Write one simple English sentence using the word "{word}".'
    resp = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return resp#.json()[0]["generated_text"][len(prompt):].strip()

if __name__ == "__main__":
    for w in ["father", "house", "family"]:
        print(f"{w} → {gen_en_sentence_api(w)}")