import streamlit as st
import torch
from transformers import BertTokenizer, BertForQuestionAnswering

tokenizer = BertTokenizer.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")
model = BertForQuestionAnswering.from_pretrained("bert-large-uncased-whole-word-masking-finetuned-squad")

def answer_question(question, context):
    inputs = tokenizer(question, context, return_tensors="pt")
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


st.title("QnA Conversational AI ")

uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

if uploaded_file is not None:
    context = uploaded_file.read().decode("utf-8")

    count = 0

    while True:
        count += 1
        user_input = st.text_input("You: ", key=count)
        if user_input.lower() == "exit":
            st.write("Chatbot: Goodbye!")
            break
        else:
            answer = answer_question(user_input, context)
            st.write("Chatbot: ", answer)
