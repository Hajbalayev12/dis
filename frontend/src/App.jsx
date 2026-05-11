import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import AnalyzePage from './pages/Analyze.jsx'
import Results from './pages/Results.jsx'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/results" element={<Results />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App