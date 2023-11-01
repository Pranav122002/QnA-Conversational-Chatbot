import React, { useState } from "react";
import Chatbot from "./Chatbot";
import "../css/Panel.css";

const Panel = () => {
  const [isOpen, setIsOpen] = useState(false);

  const togglePanel = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      <div className={`chatbot-panel ${isOpen ? "open" : ""}`}>
        <div
          className={`floating-icon ${isOpen ? "open" : ""}`}
          onClick={togglePanel}
        >
          {/* <i className="fas fa-comments"></i> Chat icon */}
        </div>

        <div className="chatbot-container">
          <div className="cross">
            <i className="fas fa-times cross-icon" onClick={togglePanel}></i>{" "}
            {/* Cross mark icon */}
          </div>
          <div>
            <Chatbot />
          </div>
        </div>
      </div>
    </>
  );
};

export default Panel;
