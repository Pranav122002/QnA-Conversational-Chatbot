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

with open("C:/Users/prana/Desktop/QnA-Conversational-Chatbot/backend/models/classifier_model.pkl", "rb") as f:
    classifier, vectorizer = pickle.load(f)

with open("C:/Users/prana/Desktop/QnA-Conversational-Chatbot/backend/datasets/dataset.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# Split the dataset into chunks based on newlines
chunks = [chunk.strip() for chunk in full_text.split("\n\n")]

table = pd.read_csv(r"C:/Users/prana/Desktop/QnA-Conversational-Chatbot/backend/datasets/Placement1.csv")
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

questions = [
    "What is the history of the college?",
    "What is the history of the college?",
    "What is the history of  FCRIT?",
    " history of the college?",
    "What is Vision of your college?",
    "vision of college",
    "What is the vision of  FCRIT?",
    "Descibe the vision of college",
    "What is Mission of your college?",
    "What is the mission of FCRIT?",
    "What is mission of college?",
    "describe the mission of college",
    "Who is Managing Director of your college?",
    "Who is MD of college?",
    "Who is MD of FCRIT?",
    "Who is Managing Director of FCRIT?",
    "Who is the chairman of your college?",
    "Who is chairman of college?",
    "Who is chairman of FCRIT?",
    "Who is vice-chairman of your college?",
    "Who is vice chairman of college?",
    "Who is vice chairman of FCRIT?",
    "Who is the treasurer of your college?",
    "Who is treasurer of college?",
    "Who is treasurer of FCRIT?",
    "Who is the Secretary of your college?",
    "Who is secretary of college?",
    "Who is secretary of FCRIT?",
    "Who is the Member of your college?",
    "Who is the Principal of your college?",
    "Who is principal of college?",
    "Who is principal of FCRIT?",
    "Tell me about Principal?",
    "What is qualification of principal?",
    "What is email ID of principal?",
    "How many departments are there ?",
    "What is number of departments in FCRIT?",
    "no. of departments in college",
    "What are department present in college?",
    "which departments exist?",
    "What are the departments in FCRIT?",
    "Tell me about College?",
    "describe the college",
    "describe FCRIT",
    "elaborate about college",
    "What is the intake capacity of computer department ?",
    "What is annual intake for computer?",
    "What is number of seats in computer department?",
    "What is availability in computer department?",
    "What is annual intake for IT?",
    "What is the number of seats in IT department?",
    "What is availability in IT?",
    "What is the intake capacity of I.T department ?",
    "What is the intake capacity of E.X.T.C. department ?",
    "What is annual intake for EXTC?",
    "What is number of seats in EXTC department?",
    "What is availability in EXTC?",
    "What is the intake capacity of Mechanical department ?",
    "What is annual intake for mechanical?",
    "What is the number of seats in mechanical department?",
    "What is availability in mechanical ?",
    "What is the intake capacity of Electrical department ?",
    "What is annual intake for electrical?",
    "What is the number of seats in electrical department?",
    "What is availability in electrical?",
    "Tell me about computer department?",
    "describe computer department",
    "elaborate on computer department",
    "What is vision of computer department?",
    "describe vision of computer department",
    "elaborate on vision for computer department ",
    "What is the vision of computer department?",
    "What is mission of computer department?",
    "describe mission of computer department",
    "elaborate on mission for computer department ",
    "What is the mission of computer department?",
    "What is address of college?",
    "where is FCRIT located?",
    "Where is college located at?",
    "What is location of FCRIT?",
    "How many minority seats are there?",
    "What is minority quota in college?",
    "How many minority seats in FCRIT?",
    "minority status",
    "placement ?",
    "placement cell website",
    "placement information",
    "placements in FCRIT",
    "placement in college",
    "phone ?",
    "What is admission enquiry number?",
    "mobile no.",
    "What is enquiry number?",
    "What is the placement cell?",
    "Is there placement group in college?",
    "Is there placement facility in college?",
    "placement cell in FCRIT",
    "Who is placement officer?",
    "who is placement officer of college?",
    "placement officer of FCRIT",
    "Where is the library?",
    "Is there library facility?",
    "Where is library in college?",
    "Where is library in FCRIT?",
    "Is there honors / minors in computer department?",
    "Is there honors / minors in computer ?",
    "Is there honors / minors in computer department  in college?",
    "Is there honors / minors in computer department? in FCRIT",
    "Is there honors / minors in IT department?",
    "Is there honors / minors in IT ?",
    "Is there honors / minors in IT department in college?",
    "Is there honors / minors in IT departmentin FCRIT?",
    "Is there honors / minors in mechanical department?",
    "Is there honors / minors in mechanical ?",
    "Is there honors / minors in mechanical department in college?",
    "Is there honors / minors in mechanical department in FCRIT?",
    "Is there honors / minors in electrical department?",
    "Is there honors / minors in electrical ?",
    "Is there honors / minors in electrical department in college?",
    "Is there honors / minors in electrical department in FCRIT?",
    "Is there honors / minors in EXTC department?",
    "Is there honors / minors in EXTC ?",
    "Is there honors / minors in EXTC department in college?",
    "Is there honors / minors in EXTC department in FCRIT?",
    "Who is Dean academics?",
    "Who isDean academics in college?",
    "Who is Dean academics for FCRIT?",
    "Who is Dean Student Affairs?",
    "Who is Dean Student Affairs in college?",
    "Who is Dean Student Affairs in FCRIT?",
    "Who is Dean R & D?",
    "Who is Dean R & D in college?",
    "Who is Dean R & D in FCRIT?",
    "Who is Dean PG Studies?",
    "Who is Dean PG Studies in college?",
    "Who is Dean PG Studies in FCRIT?",
    "Who is Dean Faculties? ",
    "Who is Dean Faculties in college?",
    "Who is Dean Faculties in FCRIT?",
    "What is Student Council?",
    "Is there student council in college?",
    "Is there student council of FCRIT?",
    "describe the student council",
    "What is FACES?",
    "What is intra collegiate fest?",
    "What is sports fest?",
    "What is techno fest?",
    "What is technical fest?",
    "What is inter collegiate techno fest?",
    "What is Eta Max?",
    "What are Student Clubs?",
    "Is there student clubs in college?",
    "Is there Student Clubs in FCRIT?",
    "What is the Infrastructure?",
    "What is infrastructure in college?",
    "What is infrastructure in FCRIT?",
    "What about ragging / anti-ragging?",
    "Is there anti ragging committee?",
    "Is there ragging in college?",
    "Is there ragging in FCRIT?",
    "Is there library website?",
    "what is the institute roadmap?",
    "Who are Trustees of the college?",
    "Who is HOD of Computer department?",
    "who is the Head of the computer department? ",
    "Who is Assistant HOD of computer department?",
    "Who is the assistant head of the computer department? ",
    "Who is HOD of Mechanical department?",
    "who is the Head of the Mechanical department? ",
    "Who is Assistant HOD of Mechanical department?",
    "Who is the assistant head of the Mechanical department? ",
    "Who is HOD of EXTC department?",
    "who is the Head of the EXTC department? ",
    "Who is Assistant HOD of EXTC department?",
    "Who is the assistant head of the EXTC department? ",
    "Who is HOD of Electrical department?",
    "who is the Head of the electrical department? ",
    "Who is Assistant HOD of electrical department?",
    "Who is the assistant head of the electrical department? ",
    "Who is HOD of IT department?",
    "who is the Head of the IT department? ",
    "Who is Assistant HOD of IT department?",
    "Who is the assistant head of the IT department? ",
    "Who is HOD of Humanities department?",
    "who is the Head of the Humanities department? ",
    "Who is Assistant HOD of Humanities department?",
    "Who is the assistant head of the Humanities department? ",
    "Who is Dean students and alumni? ",
    "Who is Dean students and alumni in college",
    "Who is Dean students and alumni in FCRIT?",
    "Who is Associate Dean academics? ",
    "Who is Associate Dean academics in college?",
    "Who is Associate Dean academics in FCRIT?",
    "Who is Associate Dean R & D and industry Liasoning? ",
    "Who is Associate Dean R & D and industry Liasoning in college?",
    "Who is Associate Dean R & D and industry Liasoning in FCRIT?",
    "Who is Associate Dean Admin and Faculty ? ",
    "Who is Associate Dean Admin and Faculty in college?",
    "Who is Associate Dean Admin and Faculty in FCRIT?",
    "Who is Associate Dean Students and alumni? ",
    "Who is Associate Dean Admin and Faculty in college?",
    "Who is Associate Dean Admin and Faculty in FCRIT?",
    "What are the different student clubs in college?",
    "What are different student clubs?",
    "What are the different professional bodies present in the college?",
    "Which Professional bodies are there in FCRIT?",
    "Is there NSS unit in college?",
    "What is last year report for the NSS unit?",
    "Is there direct second year admissions in the college?",
    "Who is Assistant Placement Officer?",
    "Who are the Assistant Placement Officer in FCRIT?",
    "What is the fee payment link for FCRIT?",
    "What is Fee payment link?",
    "FCRIT",
    "What is FCRIT?",
    "What is Recognition for FCRIT?",
    "What is accreditation of FCRIT?",
    "What is admission process of FCRIT?",
    "How to get admission in FCRIT?",
    "What is MHCET?",
    "What is entrance test for FCRIT?",
    "Is there alternative test for FCRIT?",
    "What are placement activities in FCRIT?",
    "Is there placement activities in college?",
]


for question in questions:
    question_type = classify_question(question)

    if question_type == "Table":
        answer = answer_table_question(question)
    elif question_type == "Para":
        answer = answer_para_question(question, chunks)

    print("Q : ", question)
    print("A : ", answer)
    print(" ")



