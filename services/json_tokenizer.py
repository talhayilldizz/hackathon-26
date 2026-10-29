import json
from pathlib import Path


class JsonTokenizer:
    def __init__(self, path):
        data = json.loads(
            Path(path).read_text(encoding="utf-8")
        )

        if data.get("format_version") != 1:
            raise ValueError("Unsupported tokenizer format")

        if data["char_level"] is not False:
            raise ValueError("Character tokenizer is not supported")

        self.num_words = data["num_words"]
        self.lower = data["lower"]
        self.split = data["split"]
        self.word_index = data["word_index"]
        self.oov_index = data["oov_index"]

        if not isinstance(self.num_words, int) or self.num_words <= 1:
            raise ValueError("Invalid vocabulary limit")

        if not isinstance(self.split, str) or not self.split:
            raise ValueError("Invalid split character")

        if not (0 < self.oov_index < self.num_words):
            raise ValueError("Invalid OOV index")

        self.translation = str.maketrans({
            char: self.split for char in data["filters"]
        })

    def texts_to_sequences(self, texts):
        results = []

        for text in texts:
            if not isinstance(text, str):
                raise TypeError("Tokenizer input must be a string")

            if self.lower:
                text = text.lower()

            words = [
                word
                for word in text.translate(self.translation).split(self.split)
                if word
            ]

            results.append([
                self.word_index.get(word, self.oov_index)
                for word in words
            ])

        return results
