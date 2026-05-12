import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import api from '../../api/index.js'
import styles from './Home.module.scss'

const FEATURES = [
  {
    icon: '🧠',
    title: 'AI-Powered Matching',
    desc: 'Uses semantic similarity and NLP to deeply understand CV content beyond simple keyword matching.',
  },
  {
    icon: '📊',
    title: 'Smart Scoring',
    desc: 'Ranks candidates by skills, experience, education and semantic relevance with detailed breakdowns.',
  },
  {
    icon: '🗂',
    title: 'ESCO Skills Database',
    desc: 'Backed by the official EU ESCO database with 500+ recognized skills and occupations.',
  },
  {
    icon: '📄',
    title: 'PDF Report Export',
    desc: 'Download a professional ranked candidate report to share with your hiring team instantly.',
  },
]

const STATS = [
  { number: '500+', label: 'ESCO Skills Recognized' },
  { number: 'AI',   label: 'Semantic Matching' },
  { number: '4',    label: 'Scoring Dimensions' },
  { number: 'PDF',  label: 'Export Ready' },
]

function Home() {
  const navigate = useNavigate()
  const [history, setHistory] = useState([])

  useEffect(() => {
    api.get('/api/candidates/history')
      .then(res => setHistory(res.data.slice(0, 5)))
      .catch(() => setHistory([]))
  }, [])

  const scrollToFeatures = () => {
    document.getElementById('features').scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <div className={styles.wrapper}>

      <nav className={styles.navbar}>
        <div className={styles.logo}>CV<span>Match</span></div>
        <button className={styles.navBtn} onClick={() => navigate('/analyze')}>
          Start Analysis
        </button>
      </nav>

      <section className={styles.hero}>
        <div className={styles.badge}>AI-Powered CV Screening</div>
        <h1>Find the <span>right candidate</span> faster</h1>
        <p>
          Upload multiple CVs, define your job requirements, and let our AI
          rank candidates by match percentage instantly.
        </p>
        <div className={styles.heroBtns}>
          <button className={styles.primaryBtn} onClick={() => navigate('/analyze')}>
            Start Analysis
          </button>
          <button className={styles.secondaryBtn} onClick={scrollToFeatures}>
            See Features
          </button>
        </div>
      </section>

      <div className={styles.stats}>
        {STATS.map((s, i) => (
          <div className={styles.statItem} key={i}>
            <div className={styles.statNumber}>{s.number}</div>
            <div className={styles.statLabel}>{s.label}</div>
          </div>
        ))}
      </div>

      <section className={styles.features} id="features">
        <h2>Everything you need to hire smarter</h2>
        <div className={styles.grid}>
          {FEATURES.map((f, i) => (
            <div className={styles.card} key={i}>
              <div className={styles.icon}>{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.history}>
        <h2>Recent Analyses</h2>
        {history.length === 0 ? (
          <div className={styles.empty}>
            No analyses yet. Start your first analysis above!
          </div>
        ) : (
          <div className={styles.historyList}>
            {history.map((job, i) => (
              <div
                className={styles.historyItem}
                key={i}
                onClick={() => navigate('/analyze')}
              >
                <div className={styles.historyLeft}>
                  <div className={styles.historyTitle}>{job.title}</div>
                  <div className={styles.historyMeta}>
                    {job.candidate_count} candidates · {new Date(job.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div className={styles.historyRight}>
                  <div className={styles.topScore}>
                    {job.top_score ? `${job.top_score}%` : '--'}
                  </div>
                  <button className={styles.viewBtn}>View</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <footer className={styles.footer}>
        CV Matching System · Built with FastAPI + React · Masters Dissertation Project
      </footer>

    </div>
  )
}

export default Home