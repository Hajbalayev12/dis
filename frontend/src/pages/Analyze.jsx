import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/index.js'

function Analyze() {
  const navigate = useNavigate()
  const [jobTitle, setJobTitle] = useState('')
  const [requiredSkills, setRequiredSkills] = useState('')
  const [experienceYears, setExperienceYears] = useState(0)
  const [education, setEducation] = useState('bachelors')
  const [description, setDescription] = useState('')
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (files.length === 0) {
      alert('Please upload at least one CV')
      return
    }

    const formData = new FormData()
    formData.append('job_title', jobTitle)
    formData.append('required_skills', requiredSkills)
    formData.append('experience_years', experienceYears)
    formData.append('education', education)
    formData.append('description', description)
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }

    try {
      setLoading(true)
      const response = await api.post('/api/candidates/analyze', formData)
      navigate('/results', { state: { data: response.data } })
    } catch (error) {
      alert('Something went wrong. Make sure backend is running.')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '40px auto', padding: '20px' }}>
      <h2>New Analysis</h2>
      <form onSubmit={handleSubmit}>

        <div style={{ marginBottom: '16px' }}>
          <label>Job Title</label><br />
          <input
            type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label>Required Skills (comma separated)</label><br />
          <input
            type="text"
            value={requiredSkills}
            onChange={(e) => setRequiredSkills(e.target.value)}
            placeholder="react, python, docker"
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label>Minimum Experience (years)</label><br />
          <input
            type="number"
            value={experienceYears}
            onChange={(e) => setExperienceYears(e.target.value)}
            min="0"
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label>Minimum Education</label><br />
          <select
            value={education}
            onChange={(e) => setEducation(e.target.value)}
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          >
            <option value="associate">Associate / Diploma</option>
            <option value="bachelors">Bachelor's</option>
            <option value="masters">Master's</option>
            <option value="phd">PhD</option>
          </select>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label>Job Description</label><br />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="4"
            required
            style={{ width: '100%', padding: '8px', marginTop: '4px' }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label>Upload CVs (PDF or DOCX)</label><br />
          <input
            type="file"
            multiple
            accept=".pdf,.docx"
            onChange={(e) => setFiles(e.target.files)}
            required
            style={{ marginTop: '4px' }}
          />
          {files.length > 0 && (
            <p>{files.length} file(s) selected</p>
          )}
        </div>

        <button type="submit" disabled={loading} style={{ padding: '10px 24px' }}>
          {loading ? 'Analyzing...' : 'Start Analysis'}
        </button>

      </form>
    </div>
  )
}

export default Analyze