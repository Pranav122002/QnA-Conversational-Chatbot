from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import (
    BertTokenizer,
    BertForQuestionAnswering,
    MarianMTModel,
    MarianTokenizer,
)
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from pymongo import MongoClient
from flask import request

client = MongoClient("mongodb+srv://test:test@cluster0.5llacmy.mongodb.net/")
db = client["QnA"]
qnaCollection = db["QnA"]
feedbackCollection = db["QnA"]
print("MongoDB Connection Successfull...")

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

translator = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-hi")
translator_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-hi")

tokenizer = BertTokenizer.from_pretrained(
    "bert-large-uncased-whole-word-masking-finetuned-squad"
)
model = BertForQuestionAnswering.from_pretrained(
    "bert-large-uncased-whole-word-masking-finetuned-squad"
)

with open("./datasets/datasetnew.txt", "r") as f:
    full_text = f.read()

# Split the dataset into chunks based on newlines
chunks = [chunk.strip() for chunk in full_text.split("\n\n")]


def answer_question(question, chunks):
    best_context = identify_context(question, chunks)
    if best_context is not None:
        inputs = tokenizer(question, best_context, return_tensors="pt")
        start_positions, end_positions = (
            model(**inputs).start_logits.argmax(),
            model(**inputs).end_logits.argmax(),
        )
        answer = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(
                inputs["input_ids"][0][start_positions : end_positions + 1]
            )
        )
        return answer
    else:
        return "Unable to identify context for the question."


def identify_context(question, chunks):
    question_keywords = set(
        [
            word.lower()
            for word in word_tokenize(question)
            if word.isalnum() and word.lower() not in stop_words
        ]
    )

    best_context = None
    highest_overlap = 0

    for context in chunks:
        context_lower = context.lower()
        context_keywords = set(
            [
                word.lower()
                for word in word_tokenize(context)
                if word.isalnum() and word.lower() not in stop_words
            ]
        )

        # Calculate the overlap between question keywords and context keywords
        overlap = len(question_keywords.intersection(context_keywords))

        # Update the best context if the overlap is higher
        if overlap > highest_overlap:
            best_context = context
            highest_overlap = overlap

    return best_context


def translate_to_hindi(text):
    inputs = translator_tokenizer.encode(text, return_tensors="pt")
    translated = translator.generate(
        inputs, max_length=128, num_beams=4, early_stopping=True
    )
    translation = translator_tokenizer.decode(translated[0], skip_special_tokens=True)
    return translation


app = Flask(__name__)
CORS(app)


@app.route("/answer", methods=["POST"])
def answer_endpoint():
    data = request.get_json()
    question = data["question"]
    answer = answer_question(question, chunks)

    existing_question = qnaCollection.find_one({"question": question})

    if existing_question:
        pass
    else:
        result = qnaCollection.insert_one({"question": question, "answer": answer})

    return jsonify({"answer": answer})


@app.route("/translate", methods=["POST"])
def translate_endpoint():
    data = request.get_json()
    text = data["answer"]
    hindi_answer = translate_to_hindi(text)
    return jsonify({"hindi_answer": hindi_answer})


@app.route("/like", methods=["POST"])
def like_endpoint():
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")

    result = qnaCollection.find_one({"question": question, "answer": answer})

    if result:
        qnaCollection.update_one(
            {"question": question, "answer": answer}, {"$inc": {"likes": 1}}
        )
        return jsonify({"message": "Like added successfully"})
    else:
        return jsonify({"message": "Question-answer pair not found in the database"})


@app.route("/dislike", methods=["POST"])
def dislike_endpoint():
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")

    result = qnaCollection.find_one({"question": question, "answer": answer})

    if result:
        qnaCollection.update_one(
            {"question": question, "answer": answer}, {"$inc": {"dislikes": 1}}
        )
        return jsonify({"message": "Dislike added successfully"})
    else:
        return jsonify({"message": "Question-answer pair not found in the database"})


if __name__ == "__main__":
    app.run()
