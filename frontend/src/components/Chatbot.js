import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "../css/Chatbot.css";

export default function Chatbot() {
  const [question, setQuestion] = useState("");
  const [qaHistory, setQAHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [voiceSpeaking, setVoiceSpeaking] = useState(false);
  const chatContainerRef = useRef(null);

  const [listening, setListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  const startListening = () => {
    const recognition = new (window.SpeechRecognition ||
      window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.onstart = () => {
      setListening(true);
    };
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;

      setQuestion(text);
    };
    recognition.onend = () => {
      setListening(false);
    };

    recognition.start();
    setRecognition(recognition);
  };

  const stopListening = () => {
    if (recognition) {
      recognition.stop();
      setRecognition(null);
    }
  };

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

  const speakAnswer = (answer) => {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(answer);

    synth.speak(utterance);

    utterance.onstart = () => {
      setVoiceSpeaking(true);
    };

    utterance.onend = () => {
      setVoiceSpeaking(false);
    };
  };

  const like = async (question, answer) => {
    try {
      const response = await axios.post("http://localhost:5000/like", {
        question: question,
        answer: answer,
      });
      console.log("Like response:", response.data);
    } catch (error) {
      console.error("Error sending like feedback:", error);
    }
  };

  const dislike = async (question, answer) => {
    try {
      const response = await axios.post("http://localhost:5000/dislike", {
        question: question,
        answer: answer,
      });
      console.log("Dislike response:", response.data);
    } catch (error) {
      console.error("Error sending dislike feedback:", error);
    }
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
      return {
        hindi_answer: response.data.hindi_answer,
        marathi_answer: response.data.marathi_answer,
        tamil_answer: response.data.tamil_answer,
      };
    } catch (error) {
      console.error(error);
      return {
        hindi_answer: "Translation Error",
        marathi_answer: "Translation Error",
        tamil_answer: "Translation Error",
      };
    }
  };

  const handleTranslateClick = async (index) => {
    const qa = qaHistory[index];
    const translatedAnswers = await translate(qa.answer);
    setQAHistory((prevHistory) => {
      const updatedHistory = [...prevHistory];
      updatedHistory[index].hindi_answer = translatedAnswers.hindi_answer;
      updatedHistory[index].marathi_answer = translatedAnswers.marathi_answer;
      updatedHistory[index].tamil_answer = translatedAnswers.tamil_answer;
      return updatedHistory;
    });
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

                <div className="icons">
                  <div
                    className="translate"
                    onClick={() => handleTranslateClick(index)}
                  >
                    <i className="fa-solid fa-globe"></i>
                  </div>

                  <div
                    className="voiceanswer"
                    onClick={() => speakAnswer(qa.answer)}
                  >
                    <i className="fa-solid fa-volume-high"></i>
                  </div>

                  <div
                    className="like"
                    onClick={() => like(qa.question, qa.answer)}
                  >
                    <i className="fa-solid fa-thumbs-up"></i>
                  </div>

                  <div
                    className="dislike"
                    onClick={() => dislike(qa.question, qa.answer)}
                  >
                    <i className="fa-solid fa-thumbs-down"></i>
                  </div>
                </div>

                {qa.hindi_answer && <div className="t">{qa.hindi_answer}</div>}
                {qa.marathi_answer && (
                  <div className="t">{qa.marathi_answer}</div>
                )}
                {qa.tamil_answer && <div className="t">{qa.tamil_answer}</div>}
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

          <div
            className="microphone"
            onClick={listening ? stopListening : startListening}
          >
            <i className="fa-solid fa-microphone"></i>
          </div>

          <div className="submitbtn" onClick={getAnswer}>
            {loading ? (
              <Spinner />
            ) : (
              <>
                <i className="fa-solid fa-arrow-right fa-xl"></i>{" "}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
