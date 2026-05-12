import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/index.js'
import styles from './Analyze.module.scss'

const EDUCATION_OPTIONS = [
  { value: 'associate', label: 'Associate / Diploma' },
  { value: 'bachelors', label: "Bachelor's Degree" },
  { value: 'masters',   label: "Master's Degree" },
  { value: 'phd',       label: 'PhD / Doctorate' },
]

function Analyze() {
  const navigate = useNavigate()
  const fileInputRef = useRef(null)

  const [jobTitle,       setJobTitle]       = useState('')
  const [skillInput,     setSkillInput]      = useState('')
  const [skillTags,      setSkillTags]       = useState([])
  const [experienceYears, setExperienceYears] = useState(0)
  const [education,      setEducation]       = useState('bachelors')
  const [description,    setDescription]     = useState('')
  const [files,          setFiles]           = useState([])
  const [dragOver,       setDragOver]        = useState(false)
  const [loading,        setLoading]         = useState(false)

  const addSkillTag = (e) => {
    if ((e.key === 'Enter' || e.key === ',') && skillInput.trim()) {
      e.preventDefault()
      const newSkill = skillInput.trim().toLowerCase().replace(',', '')
      if (!skillTags.includes(newSkill)) {
        setSkillTags([...skillTags, newSkill])
      }
      setSkillInput('')
    }
  }

  const removeSkillTag = (skill) => {
    setSkillTags(skillTags.filter(s => s !== skill))
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = Array.from(e.dataTransfer.files).filter(
      f => f.name.endsWith('.pdf') || f.name.endsWith('.docx')
    )
    setFiles(prev => [...prev, ...dropped])
  }

  const handleFileInput = (e) => {
    const selected = Array.from(e.target.files)
    setFiles(prev => [...prev, ...selected])
  }

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const handleSubmit = async () => {
    if (!jobTitle.trim()) return alert('Please enter a job title')
    if (skillTags.length === 0) return alert('Please add at least one required skill')
    if (files.length === 0) return alert('Please upload at least one CV')

    const formData = new FormData()
    formData.append('job_title', jobTitle)
    formData.append('required_skills', skillTags.join(','))
    formData.append('experience_years', experienceYears)
    formData.append('education', education)
    formData.append('description', description)
    files.forEach(f => formData.append('files', f))

    try {
      setLoading(true)
      const response = await api.post('/api/candidates/analyze', formData)
      navigate('/results', { state: { data: response.data } })
    } catch (err) {
      alert('Something went wrong. Make sure the backend is running.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className={styles.wrapper}>
        <div className={styles.container}>
          <div className={styles.loadingBox}>
            <div className={styles.spinner} />
            <p>Analyzing {files.length} CV{files.length > 1 ? 's' : ''}...</p>
            <p className={styles.loadingHint}>
              This may take a few seconds depending on file size
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.wrapper}>

      <nav className={styles.navbar}>
        <div className={styles.logo} onClick={() => navigate('/')}>
          CV<span>Match</span>
        </div>
        <button className={styles.navBtn} onClick={() => navigate('/')}>
          Back to Home
        </button>
      </nav>

      <div className={styles.container}>

        <div className={styles.header}>
          <h1>New Analysis</h1>
          <p>Fill in the job requirements and upload candidate CVs to get started</p>
        </div>

        {/* Job Info */}
        <div className={styles.card}>
          <div className={styles.cardTitle}>Job Information</div>

          <div className={styles.field}>
            <label>Job Title</label>
            <input
              type="text"
              placeholder="e.g. Senior Frontend Developer"
              value={jobTitle}
              onChange={e => setJobTitle(e.target.value)}
            />
          </div>

          <div className={styles.field}>
            <label>Job Description</label>
            <textarea
              placeholder="Describe the role, responsibilities and expectations..."
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
          </div>
        </div>

        {/* Requirements */}
        <div className={styles.card}>
          <div className={styles.cardTitle}>Requirements</div>

          <div className={styles.field}>
            <label>Required Skills</label>
            <input
              type="text"
              placeholder="Type a skill and press Enter or comma..."
              value={skillInput}
              onChange={e => setSkillInput(e.target.value)}
              onKeyDown={addSkillTag}
            />
            <div className={styles.hint}>Press Enter or comma to add each skill</div>
            {skillTags.length > 0 && (
              <div className={styles.skillTags}>
                {skillTags.map((skill, i) => (
                  <div className={styles.tag} key={i}>
                    {skill}
                    <span
                      className={styles.removeTag}
                      onClick={() => removeSkillTag(skill)}
                    >
                      x
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className={styles.row}>
            <div className={styles.field}>
              <label>Minimum Experience (years)</label>
              <input
                type="number"
                min="0"
                value={experienceYears}
                onChange={e => setExperienceYears(e.target.value)}
              />
            </div>
            <div className={styles.field}>
              <label>Minimum Education</label>
              <select
                value={education}
                onChange={e => setEducation(e.target.value)}
              >
                {EDUCATION_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Upload */}
        <div className={styles.card}>
          <div className={styles.cardTitle}>Upload CVs</div>

          <div
            className={`${styles.dropzone} ${dragOver ? styles.dragOver : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current.click()}
          >
            <div className={styles.dropIcon}>📂</div>
            <p><strong>Click to upload</strong> or drag and drop</p>
            <div className={styles.dropHint}>PDF or DOCX files only</div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.docx"
              style={{ display: 'none' }}
              onChange={handleFileInput}
            />
          </div>

          {files.length > 0 && (
            <div className={styles.fileList}>
              {files.map((file, i) => (
                <div className={styles.fileItem} key={i}>
                  <div>
                    <span className={styles.fileName}>{file.name}</span>
                    <span className={styles.fileSize}>{formatSize(file.size)}</span>
                  </div>
                  <button className={styles.removeFile} onClick={() => removeFile(i)}>
                    x
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <button
          className={styles.submitBtn}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'Analyzing...' : `Analyze ${files.length > 0 ? files.length + ' CV' + (files.length > 1 ? 's' : '') : 'CVs'}`}
        </button>

      </div>
    </div>
  )
}

export default Analyze