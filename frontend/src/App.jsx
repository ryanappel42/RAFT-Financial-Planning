import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "./pages/Landing";
import Consumer from "./pages/Consumer";
import Advisor from "./pages/Advisor";
import About from "./pages/About";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/consumer" element={<Consumer />} />
        <Route path="/advisor" element={<Advisor />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}