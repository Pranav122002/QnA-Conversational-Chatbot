import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Panel from "./components/Panel";
import Home from "./components/Home";
import AboutUs from "./components/AboutUs";

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Panel />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/aboutus" element={<AboutUs />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
