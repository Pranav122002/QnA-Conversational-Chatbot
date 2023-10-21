import React, { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [qaHistory, setQaHistory] = useState([]);

  const handleQuestionSubmit = async () => {
    try {
      const response = await axios.post("http://localhost:5000/answer", {
        question: question,
      });

      const newQa = { question, answer: response.data.answer };
      setQaHistory([...qaHistory, newQa]);

      setQuestion("");
      setAnswer(response.data.answer);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div>
      <input
        type="text"
        placeholder="Ask a question"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button onClick={handleQuestionSubmit}>Submit</button>
      {/* <p>Answer: {answer}</p> */}
      <div>
        <h2>Question-Answer History:</h2>
        <ul>
          {qaHistory.map((qa, index) => (
            <li key={index}>
              <strong>Q:</strong> {qa.question}
              <br />
              <strong>A:</strong> {qa.answer}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
