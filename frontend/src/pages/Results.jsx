import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

function Results() {
  const location = useLocation()
  const navigate = useNavigate()
  const data = location.state?.data
  const [threshold, setThreshold] = useState(50)

  if (!data) {
    navigate('/')
    return null
  }

  const aboveThreshold = data.candidates.filter(c => c.final_score >= threshold)
  const belowThreshold = data.candidates.filter(c => c.final_score < threshold)

  const renderCandidate = (candidate, index, isAbove) => (
    <div key={index} style={{
      border: `1px solid ${isAbove ? '#28a745' : '#ccc'}`,
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '16px',
      opacity: isAbove ? 1 : 0.5,
      background: isAbove ? '#fff' : '#f8f8f8'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0 }}>
          {isAbove ? '✅' : '❌'} {candidate.name}
        </h3>
        <span style={{
          fontSize: '24px',
          fontWeight: 'bold',
          color: isAbove ? 'green' : 'red'
        }}>
          {candidate.final_score}%
        </span>
      </div>

      <div style={{ marginTop: '12px', display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '14px' }}>
        <span>Skills: {candidate.skill_score}%</span>
        <span>Experience: {candidate.experience_score}%</span>
        <span>Education: {candidate.education_score}%</span>
        <span>Semantic: {candidate.semantic_score}%</span>
      </div>

      <p style={{ marginTop: '12px', color: '#555', fontSize: '14px' }}>
        {candidate.explanation}
      </p>

      {candidate.matched_skills.length > 0 && (
        <div style={{ marginTop: '8px' }}>
          <strong>Matched: </strong>
          {candidate.matched_skills.map((skill, i) => (
            <span key={i} style={{
              background: '#d4edda',
              padding: '2px 8px',
              borderRadius: '4px',
              marginRight: '4px',
              fontSize: '13px'
            }}>{skill}</span>
          ))}
        </div>
      )}

      {candidate.missing_skills.length > 0 && (
        <div style={{ marginTop: '8px' }}>
          <strong>Missing: </strong>
          {candidate.missing_skills.map((skill, i) => (
            <span key={i} style={{
              background: '#f8d7da',
              padding: '2px 8px',
              borderRadius: '4px',
              marginRight: '4px',
              fontSize: '13px'
            }}>{skill}</span>
          ))}
        </div>
      )}
    </div>
  )

  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', padding: '20px' }}>

      <h2>Results for: {data.job.title}</h2>
      <p>{data.candidates.length} candidates analyzed</p>

      {/* Threshold Slider */}
      <div style={{
        background: '#f0f0f0',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <strong>Minimum match threshold</strong>
          <strong style={{ color: 'green' }}>{threshold}%</strong>
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={threshold}
          onChange={(e) => setThreshold(Number(e.target.value))}
          style={{ width: '100%' }}
        />
        <div style={{ marginTop: '8px', fontSize: '14px', color: '#555' }}>
          ✅ {aboveThreshold.length} candidates above threshold &nbsp;|&nbsp;
          ❌ {belowThreshold.length} candidates below threshold
        </div>
      </div>

      <button onClick={() => navigate('/analyze')} style={{ marginBottom: '24px', padding: '8px 20px' }}>
        New Analysis
      </button>

      {/* Above threshold */}
      {aboveThreshold.map((candidate, index) => renderCandidate(candidate, index, true))}

      {/* Divider */}
      {belowThreshold.length > 0 && (
        <div style={{
          textAlign: 'center',
          color: '#999',
          margin: '16px 0',
          borderTop: '1px dashed #ccc',
          paddingTop: '16px'
        }}>
          Below threshold ({threshold}%)
        </div>
      )}

      {/* Below threshold */}
      {belowThreshold.map((candidate, index) => renderCandidate(candidate, index, false))}

    </div>
  )
}

export default Results