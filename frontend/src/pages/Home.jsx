import { useNavigate } from 'react-router-dom'

function HomePage() {
  const navigate = useNavigate()

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '100vh' 
    }}>
      <h1>CV Matching System</h1>
      <p>AI-powered candidate ranking for HR professionals</p>
      <button onClick={() => navigate('/analyze')}>
        Get Started
      </button>
    </div>
  )
}

export default HomePage