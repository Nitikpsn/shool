import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Compare from './pages/Compare'
import Reports from './pages/Reports'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/compare/:sessionId" element={<Compare />} />
        <Route path="/reports/:sessionId" element={<Reports />} />
      </Routes>
    </BrowserRouter>
  )
}