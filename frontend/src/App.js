import React, { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleQuestionSubmit = async () => {
    try {
      const response = await axios.post("http://localhost:5000/answer", {
        question: question,
      });

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
      <p>Answer: {answer}</p>
    </div>
  );
}

export default App;
