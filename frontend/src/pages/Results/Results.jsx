import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import styles from './Results.module.scss'

function getScoreClass(score) {
  if (score >= 70) return 'high'
  if (score >= 50) return 'mid'
  return 'low'
}

function Modal({ candidate, onClose }) {
  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <button className={styles.modalClose} onClick={onClose}>x</button>

        <div className={styles.modalName}>{candidate.name}</div>
        <div className={styles.modalScore}>{candidate.final_score}%</div>

        {candidate.email && (
          <div className={styles.modalSection}>
            <h4>Contact</h4>
            <p>
              {candidate.email}
              {candidate.phone ? '  |  ' + candidate.phone : ''}
            </p>
          </div>
        )}

        <div className={styles.modalSection}>
          <h4>Score Breakdown</h4>
          <p>
            Skills: {candidate.skill_score}% |
            Experience: {candidate.experience_score}% |
            Education: {candidate.education_score}% |
            Semantic: {candidate.semantic_score}%
          </p>
        </div>

        <div className={styles.modalSection}>
          <h4>Matched Skills</h4>
          <div className={styles.modalTags}>
            {candidate.matched_skills.map((s, i) => (
              <span key={i} className={`${styles.modalTag} ${styles.matched}`}>{s}</span>
            ))}
          </div>
        </div>

        {candidate.missing_skills.length > 0 && (
          <div className={styles.modalSection}>
            <h4>Missing Skills</h4>
            <div className={styles.modalTags}>
              {candidate.missing_skills.map((s, i) => (
                <span key={i} className={`${styles.modalTag} ${styles.missing}`}>{s}</span>
              ))}
            </div>
          </div>
        )}

        {candidate.extra_skills && candidate.extra_skills.length > 0 && (
          <div className={styles.modalSection}>
            <h4>Additional Skills</h4>
            <div className={styles.modalTags}>
              {candidate.extra_skills.map((s, i) => (
                <span key={i} className={`${styles.modalTag} ${styles.extra}`}>{s}</span>
              ))}
            </div>
          </div>
        )}

        <div className={styles.modalSection}>
          <h4>Summary</h4>
          <p>{candidate.explanation}</p>
        </div>
      </div>
    </div>
  )
}

function Results() {
  const location  = useLocation()
  const navigate  = useNavigate()
  const data      = location.state?.data

  const [threshold,  setThreshold]  = useState(50)
  const [sortBy,     setSortBy]     = useState('final_score')
  const [selected,   setSelected]   = useState(null)

  if (!data) {
    navigate('/')
    return null
  }

  const sorted = [...data.candidates].sort((a, b) => b[sortBy] - a[sortBy])
  const above  = sorted.filter(c => c.final_score >= threshold)
  const below  = sorted.filter(c => c.final_score < threshold)

  const avgScore  = Math.round(
    data.candidates.reduce((s, c) => s + c.final_score, 0) / data.candidates.length
  )
  const topScore  = data.candidates[0]?.final_score ?? 0
  const strongCount = data.candidates.filter(c => c.final_score >= 70).length

  const exportCSV = () => {
    const headers = ['Name', 'Email', 'Phone', 'Final Score', 'Skills', 'Experience', 'Education', 'Semantic', 'Recommendation']
    const rows    = data.candidates.map(c => [
      c.name, c.email, c.phone,
      c.final_score, c.skill_score,
      c.experience_score, c.education_score,
      c.semantic_score, c.recommendation
    ])
    const csv     = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob    = new Blob([csv], { type: 'text/csv' })
    const url     = URL.createObjectURL(blob)
    const a       = document.createElement('a')
    a.href        = url
    a.download    = `${data.job.title}_results.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const downloadPDF = () => {
    if (data.job_id) {
      window.open(`http://localhost:8000/api/candidates/${data.job_id}/report`, '_blank')
    }
  }

  const renderCandidate = (candidate, isAbove) => {
    const sc = getScoreClass(candidate.final_score)
    return (
      <div
        key={candidate.filename}
        className={`${styles.candidateCard} ${isAbove ? styles.above : styles.below}`}
        onClick={() => setSelected(candidate)}
      >
        <div className={styles.cardTop}>
          <div className={styles.candidateInfo}>
            <div className={styles.candidateName}>{candidate.name}</div>
            <div className={styles.candidateMeta}>
              {candidate.email && <span>{candidate.email}</span>}
              {candidate.experience_years > 0 && (
                <span>{candidate.experience_years} yrs exp</span>
              )}
              <span>{candidate.education_level}</span>
              <span>{candidate.filename}</span>
            </div>
          </div>
          <div className={styles.scoreBox}>
            <div className={`${styles.score} ${styles[sc]}`}>
              {candidate.final_score}%
            </div>
            <div className={`${styles.recommendation} ${styles[sc]}`}>
              {candidate.recommendation}
            </div>
          </div>
        </div>

        {[
          { label: 'Skills',      value: candidate.skill_score,      cls: 'skills' },
          { label: 'Experience',  value: candidate.experience_score,  cls: 'experience' },
          { label: 'Education',   value: candidate.education_score,   cls: 'education' },
          { label: 'Semantic',    value: candidate.semantic_score,    cls: 'semantic' },
        ].map(bar => (
          <div className={styles.scoreBar} key={bar.label}>
            <div className={styles.scoreBarLabel}>
              <span>{bar.label}</span>
              <span>{bar.value}%</span>
            </div>
            <div className={styles.barTrack}>
              <div
                className={`${styles.barFill} ${styles[bar.cls]}`}
                style={{ width: `${bar.value}%` }}
              />
            </div>
          </div>
        ))}

        <div className={styles.skillsRow}>
          {candidate.matched_skills.map((s, i) => (
            <span key={i} className={`${styles.skillTag} ${styles.matched}`}>{s}</span>
          ))}
          {candidate.missing_skills.map((s, i) => (
            <span key={i} className={`${styles.skillTag} ${styles.missing}`}>{s}</span>
          ))}
          {(candidate.extra_skills || []).slice(0, 4).map((s, i) => (
            <span key={i} className={`${styles.skillTag} ${styles.extra}`}>{s}</span>
          ))}
        </div>

        <div className={styles.explanation}>{candidate.explanation}</div>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>

      {selected && (
        <Modal candidate={selected} onClose={() => setSelected(null)} />
      )}

      <nav className={styles.navbar}>
        <div className={styles.logo} onClick={() => navigate('/')}>
          CV<span>Match</span>
        </div>
        <div className={styles.navBtns}>
          <button className={styles.outlineBtn} onClick={exportCSV}>
            Export CSV
          </button>
          <button className={styles.outlineBtn} onClick={downloadPDF}>
            Download PDF
          </button>
          <button className={styles.primaryBtn} onClick={() => navigate('/analyze')}>
            New Analysis
          </button>
        </div>
      </nav>

      <div className={styles.container}>

        <div className={styles.header}>
          <h1>{data.job.title}</h1>
          <p>{data.candidates.length} candidates analyzed</p>
        </div>

        <div className={styles.summaryCards}>
          {[
            { number: data.candidates.length, label: 'Total Candidates' },
            { number: `${topScore}%`,         label: 'Top Score' },
            { number: `${avgScore}%`,          label: 'Average Score' },
            { number: strongCount,             label: 'Strong Matches' },
          ].map((s, i) => (
            <div className={styles.summaryCard} key={i}>
              <div className={styles.summaryNumber}>{s.number}</div>
              <div className={styles.summaryLabel}>{s.label}</div>
            </div>
          ))}
        </div>

        <div className={styles.controls}>
          <div className={styles.thresholdBox}>
            <div className={styles.thresholdLabel}>
              Minimum threshold <span>{threshold}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={threshold}
              onChange={e => setThreshold(Number(e.target.value))}
            />
          </div>
          <div className={styles.sortBox}>
            <label>Sort by</label>
            <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
              <option value="final_score">Final Score</option>
              <option value="skill_score">Skills</option>
              <option value="experience_score">Experience</option>
              <option value="education_score">Education</option>
              <option value="semantic_score">Semantic</option>
            </select>
          </div>
        </div>

        {above.map(c => renderCandidate(c, true))}

        {below.length > 0 && (
          <div className={styles.divider}>
            Below threshold ({threshold}%) -- {below.length} candidate{below.length > 1 ? 's' : ''}
          </div>
        )}

        {below.map(c => renderCandidate(c, false))}

      </div>
    </div>
  )
}

export default Results