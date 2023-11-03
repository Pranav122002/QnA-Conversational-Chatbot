import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "../css/Chatbot.css";

export default function Chatbot() {
  const [question, setQuestion] = useState("");
  const [qaHistory, setQAHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
  }, [qaHistory]);

  const Spinner = () => {
    return (
      <div className="loader">
        <div className="dot dot1"></div>
        <div className="dot dot2"></div>
        <div className="dot dot3"></div>
      </div>
    );
  };
  const getAnswer = async () => {
    try {
      setLoading(true);
      const response = await axios.post("http://localhost:5000/answer", {
        question: question,
      });

      const newQA = { question, answer: response.data.answer };
      setQAHistory([...qaHistory, newQA]);
      setQuestion("");
    } catch (error) {
      console.error(error);
      return "Error";
    } finally {
      setLoading(false);
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
        <div className="container" ref={chatContainerRef}>
          <div className="qatcontainer">
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
                >
                  <i class="fa-solid fa-globe"></i>
                </div>

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

          <div className="submitbtn" onClick={getAnswer}>
            {loading ? (
              <Spinner />
            ) : (
              <>
                <i class="fa-solid fa-arrow-right fa-xl"></i>{" "}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
