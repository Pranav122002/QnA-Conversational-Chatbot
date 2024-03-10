from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import BertTokenizer, BertForQuestionAnswering
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from pymongo import MongoClient
from flask import request
from googletrans import Translator
import pickle
from transformers import pipeline
import pandas as pd
import warnings
warnings.filterwarnings("ignore") 

translator = Translator()

client = MongoClient("mongodb+srv://test:test@cluster0.5llacmy.mongodb.net/")
db = client["QnA"]
qnaCollection = db["QnA"]
print("MongoDB Connection Successfull...")

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

tokenizer = BertTokenizer.from_pretrained(
    "bert-large-uncased-whole-word-masking-finetuned-squad"
)
model = BertForQuestionAnswering.from_pretrained(
    "bert-large-uncased-whole-word-masking-finetuned-squad"
)

tqa = pipeline(
    task="table-question-answering", model="google/tapas-large-finetuned-sqa"
)

with open("./models/classifier_model.pkl", "rb") as f:
    classifier, vectorizer = pickle.load(f)

with open("./datasets/dataset.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# Split the dataset into chunks based on newlines
chunks = [chunk.strip() for chunk in full_text.split("\n\n")]

table = pd.read_csv(r"./datasets/Placement1.csv")
table = table.astype(str)


def classify_question(question):
    question_vec = vectorizer.transform([question])
    question_type = classifier.predict(question_vec)[0]
    return question_type


def answer_table_question(question):
    answer = tqa(table=table, query=question)
    return answer["answer"]


def answer_para_question(question, chunks):
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
                for word in word_tokenize(context_lower)
                if word.isalnum() and word.lower() not in stop_words
            ]
        )

        overlap = len(question_keywords.intersection(context_keywords))

        if overlap > highest_overlap:
            best_context = context
            highest_overlap = overlap

    return best_context


def translate_to_hindi(text):
    translated = translator.translate(text, dest="hi")
    return translated.text


def translate_to_marathi(text):
    translated = translator.translate(text, dest="mr")
    return translated.text


def translate_to_tamil(text):
    translated = translator.translate(text, dest="ta")
    return translated.text


app = Flask(__name__)
CORS(app)


@app.route("/answer", methods=["POST"])
def answer_endpoint():

    data = request.get_json()
    question = data["question"]
    question_type = classify_question(question)

    if question_type == "Table":
        answer = answer_table_question(question)
    elif question_type == "Para":
        answer = answer_para_question(question, chunks)

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
    marathi_answer = translate_to_marathi(text)
    tamil_answer = translate_to_tamil(text)

    return jsonify(
        {
            "hindi_answer": hindi_answer,
            "marathi_answer": marathi_answer,
            "tamil_answer": tamil_answer,
        }
    )


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
