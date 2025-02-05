import { BrowserRouter, Routes, Route } from "react-router";
import Dashboard from "./Dashboard";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard state="pending" />} />
        <Route path="/pending" element={<Dashboard state="pending" />} />
        <Route path="/blocked" element={<Dashboard state="blocked" />} />
        <Route path="/allowed" element={<Dashboard state="allowed" />} />
        <Route path="/settings" element={<Dashboard state="settings" />} />
      </Routes>
    </BrowserRouter>
  );
}
