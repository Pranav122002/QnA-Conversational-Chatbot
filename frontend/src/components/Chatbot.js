import React, { useState } from "react";
import axios from "axios";
import "../css/Chatbot.css";

export default function Chatbot() {
  const [question, setQuestion] = useState("");
  const [qaHistory, setQAHistory] = useState([]);

  const getAnswer = async () => {
    try {
      const response = await axios.post("http://localhost:5000/answer", {
        question: question,
      });

      const newQA = { question, answer: response.data.answer };
      setQAHistory([...qaHistory, newQA]);

      setQuestion("");
    } catch (error) {
      console.error(error);
      return "Error";
    }
  };

  const translate = async (answer) => {
    try {
      const response = await axios.post("http://localhost:5000/translate", {
        answer: answer,
      });

      return response.data.hindi_answer;
    } catch (error) {
      console.error(error);
      return "Translation Error";
    }
  };

  return (
    <>
      <div>
        <div>
          <div>
            {qaHistory.map((qa, index) => (
              <div className="qat" key={index}>
                <div className="q">{qa.question}</div>

                <div className="a">{qa.answer}</div>
                <div
                  className="translate"
                  onClick={async () => {
                    const translatedAnswer = await translate(qa.answer);
                    setQAHistory((prevHistory) => {
                      const updatedHistory = [...prevHistory];
                      updatedHistory[index].hindi_answer = translatedAnswer;
                      return updatedHistory;
                    });
                  }}
                ></div>

                {qa.hindi_answer && <div className="t">{qa.hindi_answer}</div>}
              </div>
            ))}
          </div>
        </div>

        <div className="inputbar">
          <input
            className="bar"
            type="text"
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <div className="submitbtn" onClick={getAnswer}></div>
        </div>
      </div>
    </>
  );
}
