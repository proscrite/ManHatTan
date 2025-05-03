import fasttext
import fasttext.util
import spacy
from pathlib import Path

# Load FastText Hebrew vectors
fasttext_model = fasttext.load_model("/Users/pabloherrero/Documents/autism/ML_course/NLP_spaCy/cc.he.300.head")

# Convert FastText model to a dictionary
vectors = {word: fasttext_model.get_word_vector(word) for word in fasttext_model.get_words()}

# Create a blank Hebrew spaCy model
nlp = spacy.blank("he")

# Save the vectors in a .txt format required by spaCy
output_dir = Path("/Users/pabloherrero/Documents/autism/ML_course/NLP_spaCy/he_vectors")
output_dir.mkdir(exist_ok=True)
with open(output_dir / "vectors.txt", "w", encoding="utf-8") as f:
    f.write(f"{len(vectors)} {len(next(iter(vectors.values())))}\n")  # Header: num_words, vector_dim
    for word, vector in vectors.items():
        f.write(f"{word} " + " ".join(map(str, vector)) + "\n")

# # Convert and save in spaCy's format
# spacy.cli.init_vectors("he", output_dir / "vectors.txt", output_dir)

# # Load the new model with vectors
# nlp = spacy.load(output_dir)
# print(f"Loaded model with {len(nlp.vocab.vectors)} word vectors")
