from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import BertTokenizer, BertForQuestionAnswering, MarianMTModel, MarianTokenizer

translator = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-hi")
translator_tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-hi")

tokenizer = BertTokenizer.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

with open("dataset.txt", "r") as f:
    context = f.read()

def answer_question(question, context):
    inputs = tokenizer(question, context, return_tensors="pt")
    start_positions, end_positions = model(**inputs).start_logits.argmax(), model(**inputs).end_logits.argmax()
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][start_positions:end_positions+1]))
    return answer

def translate_to_hindi(text):
    inputs = translator_tokenizer.encode(text, return_tensors="pt")
    translated = translator.generate(inputs, max_length=128, num_beams=4, early_stopping=True)
    translation = translator_tokenizer.decode(translated[0], skip_special_tokens=True)
    return translation

app = Flask(__name__)
CORS(app)

@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    question = data['question']
    answer = answer_question(question, context)
    return jsonify({"answer": answer})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data['answer']
    hindi_answer = translate_to_hindi(text)
    return jsonify({"hindi_answer": hindi_answer})

if __name__ == '__main__':
    app.run()
