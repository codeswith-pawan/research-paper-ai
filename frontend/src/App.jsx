import { useEffect, useState } from 'react'
import {
  chatWithPapers,
  deletePaper,
  getPapers,
  searchPapers,
  uploadPaper,
} from './services/api'
import './App.css'

function formatFileSize(bytes) {
  if (!bytes) return '0 Bytes'

  const units = ['Bytes', 'KB', 'MB', 'GB']
  const index = Math.floor(Math.log(bytes) / Math.log(1024))
  const size = bytes / Math.pow(1024, index)

  return `${size.toFixed(index === 0 ? 0 : 2)} ${units[index]}`
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleString()
}

function App() {
  const [papers, setPapers] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)

  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState('')
  const [searched, setSearched] = useState(false)

  const [chatQuestion, setChatQuestion] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [chatting, setChatting] = useState(false)
  const [chatError, setChatError] = useState('')

 async function loadPapers(showLoading = true) {
  try {
    if (showLoading) {
      setLoading(true)
    }

    setError('')

    const data = await getPapers()
    setPapers(data.papers || [])
  } catch (err) {
    setError(err.message || 'Failed to load papers')
  } finally {
    if (showLoading) {
      setLoading(false)
    }
  }
}

  useEffect(() => {
  let cancelled = false

  async function initializePapers() {
    try {
      const data = await getPapers()

      if (!cancelled) {
        setPapers(data.papers || [])
        setError('')
        setLoading(false)
      }
    } catch (err) {
      if (!cancelled) {
        setError(err.message || 'Failed to load papers')
        setLoading(false)
      }
    }
  }

  initializePapers()

  return () => {
    cancelled = true
  }
}, [])

  function handleFileChange(event) {
    const file = event.target.files?.[0]

    setSelectedFile(file || null)
    setError('')
    setMessage('')
  }

  async function handleUpload(event) {
    event.preventDefault()

    if (!selectedFile) {
      setError('Please select a PDF file first.')
      return
    }

    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are allowed.')
      return
    }

    try {
      setUploading(true)
      setError('')
      setMessage('')

      const data = await uploadPaper(selectedFile)

      if (data.duplicate) {
        setMessage('This PDF already exists in the library.')
      } else {
        setMessage('PDF uploaded and indexed successfully.')
      }

      setSelectedFile(null)
      event.target.reset()

      await loadPapers()
    } catch (err) {
      setError(err.message || 'Failed to upload PDF')
    } finally {
      setUploading(false)
    }
  }

  async function handleDelete(paper) {
    const confirmed = window.confirm(
      `Delete "${paper.original_filename}"?`,
    )

    if (!confirmed) return

    try {
      setDeletingId(paper.paper_id)
      setError('')
      setMessage('')

      await deletePaper(paper.paper_id)

      setMessage('Paper deleted successfully.')
      await loadPapers()
    } catch (err) {
      setError(err.message || 'Failed to delete paper')
    } finally {
      setDeletingId(null)
    }
  }

  async function handleSearch(event) {
    event.preventDefault()

    if (!searchQuery.trim()) {
      setSearchError('Please enter a search query.')
      return
    }

    try {
      setSearching(true)
      setSearchError('')
      setSearched(true)

      const data = await searchPapers(searchQuery.trim(), 5)

      setSearchResults(data.results || [])
    } catch (err) {
      setSearchError(err.message || 'Search failed')
      setSearchResults([])
    } finally {
      setSearching(false)
    }
  }

  async function handleChat(event) {
    event.preventDefault()

    const question = chatQuestion.trim()

    if (!question) {
      setChatError('Please enter a question.')
      return
    }

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: question,
    }

    try {
      setChatting(true)
      setChatError('')
      setChatMessages((currentMessages) => [
        ...currentMessages,
        userMessage,
      ])
      setChatQuestion('')

      const data = await chatWithPapers(question, 5)

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        sources: data.sources || [],
      }

      setChatMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ])
    } catch (err) {
      setChatError(
        err.message || 'Failed to generate an answer',
      )
    } finally {
      setChatting(false)
    }
  }

  return (
    <main className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="brand">
            <div className="brand-mark">RP</div>

            <div>
              <h1>Research Paper AI</h1>
              <p>
                Search, analyze, and ask questions across your research papers.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="refresh-btn"
            onClick={loadPapers}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh Library'}
          </button>
        </div>
      </header>

      <div className="container">
        <section className="hero-section">
          <div>
            <span className="eyebrow">AI-POWERED RESEARCH WORKSPACE</span>

            <h2>
              Your research papers,
              <br />
              one intelligent workspace.
            </h2>

            <p>
              Upload PDFs, search their contents, and get grounded answers
              from your documents using local AI.
            </p>
          </div>

          <div className="stats-card">
            <span className="stats-label">PAPER LIBRARY</span>
            <strong>{papers.length}</strong>
            <span>
              {papers.length === 1 ? 'research paper' : 'research papers'}
            </span>
          </div>
        </section>

        <section className="card upload-card">
          <div className="card-heading">
            <div>
              <span className="card-kicker">01 · DOCUMENTS</span>
              <h2>Upload a research paper</h2>
              <p>
                Add a PDF to extract text, generate chunks, and make it
                searchable.
              </p>
            </div>
          </div>

          <form onSubmit={handleUpload}>
            <label className="upload-area">
              <div className="upload-icon">↑</div>

              <strong>
                {selectedFile
                  ? selectedFile.name
                  : 'Choose a PDF research paper'}
              </strong>

              <span>
                {selectedFile
                  ? `${formatFileSize(selectedFile.size)} selected`
                  : 'PDF files only · OCR supported for scanned documents'}
              </span>

              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                disabled={uploading}
              />

              <span className="upload-browse">
                {selectedFile ? 'Choose another file' : 'Browse files'}
              </span>
            </label>

            <button
              type="submit"
              className="primary-btn upload-btn"
              disabled={uploading}
            >
              {uploading
                ? 'Uploading and indexing...'
                : 'Upload & Index PDF'}
            </button>
          </form>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {message && (
            <div className="status-message">
              {message}
            </div>
          )}
        </section>

        <div className="workspace-grid">
          <section className="card">
            <div className="card-heading">
              <div>
                <span className="card-kicker">02 · LIBRARY</span>
                <h2>Your papers</h2>
                <p>Manage the documents currently available to the AI.</p>
              </div>

              <span className="count-badge">
                {papers.length}
              </span>
            </div>

            {loading && (
              <p className="loading">Loading your papers...</p>
            )}

            {!loading && papers.length === 0 && (
              <div className="empty-state">
                <strong>No papers yet</strong>
                <span>
                  Upload your first research paper to get started.
                </span>
              </div>
            )}

            {!loading && papers.length > 0 && (
              <div className="paper-grid">
                {papers.map((paper) => (
                  <article
                    key={paper.paper_id}
                    className="paper-item"
                  >
                    <div className="paper-icon">PDF</div>

                    <div className="paper-content">
                      <h3>{paper.original_filename}</h3>

                      <div className="paper-meta">
                        <span>{paper.chunks} chunks</span>
                        <span>
                          {formatFileSize(paper.file_size)}
                        </span>
                      </div>

                      <span className="paper-date">
                        Added {formatDate(paper.uploaded_at)}
                      </span>
                    </div>

                    <button
                      type="button"
                      className="delete-btn"
                      onClick={() => handleDelete(paper)}
                      disabled={
                        deletingId === paper.paper_id
                      }
                    >
                      {deletingId === paper.paper_id
                        ? 'Deleting...'
                        : 'Delete'}
                    </button>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="card">
            <div className="card-heading">
              <div>
                <span className="card-kicker">03 · SEARCH</span>
                <h2>Find relevant passages</h2>
                <p>
                  Search across your indexed papers using semantic retrieval.
                </p>
              </div>
            </div>

            <form
              className="search-form"
              onSubmit={handleSearch}
            >
              <input
                type="text"
                value={searchQuery}
                onChange={(event) => {
                  setSearchQuery(event.target.value)
                  setSearchError('')
                }}
                placeholder="e.g. Explain blockchain architecture"
                disabled={searching}
              />

              <button
                type="submit"
                className="primary-btn"
                disabled={searching}
              >
                {searching ? 'Searching...' : 'Search'}
              </button>
            </form>

            {searchError && (
              <div className="error-message">
                {searchError}
              </div>
            )}

            {searched &&
              !searching &&
              !searchError &&
              searchResults.length === 0 && (
                <div className="empty-state">
                  <strong>No relevant results</strong>
                  <span>
                    Try a broader question or different keywords.
                  </span>
                </div>
              )}

            {searchResults.length > 0 && (
              <div className="results-list">
                <div className="results-summary">
                  Found {searchResults.length} relevant passages
                </div>

                {searchResults.map((result) => (
                  <article
                    key={`${result.paper_id}-${result.chunk_id}`}
                    className="result-item"
                  >
                    <div className="result-top">
                      <div>
                        <span className="result-paper">
                          {result.paper_name}
                        </span>

                        <h3>
                          Page {result.page_number}
                        </h3>
                      </div>

                      <span className="score-badge">
                        {result.score.toFixed(3)}
                      </span>
                    </div>

                    <div className="result-meta">
                      <span>Chunk {result.chunk_id}</span>
                      <span>
                        Score {result.score.toFixed(4)}
                      </span>
                    </div>

                    <p className="result-text">
                      {result.text}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>

        <section className="card chat-card">
          <div className="card-heading">
            <div>
              <span className="card-kicker">04 · AI ASSISTANT</span>
              <h2>Chat with your papers</h2>
              <p>
                Ask questions and get answers grounded in the indexed
                documents.
              </p>
            </div>

            <span className="ai-badge">OLLAMA · LOCAL AI</span>
          </div>

          <div className="chat-container">
            {chatMessages.length === 0 && (
              <div className="chat-empty">
                <div className="assistant-avatar">AI</div>

                <div>
                  <strong>Ask your research assistant</strong>
                  <span>
                    Try “What is blockchain?” or “Explain the methodology.”
                  </span>
                </div>
              </div>
            )}

            {chatMessages.map((message) => (
              <article
                key={message.id}
                className={`chat-message ${message.role}`}
              >
                <div className="message-avatar">
                  {message.role === 'user' ? 'You' : 'AI'}
                </div>

                <div className="message-body">
                  <span className="message-role">
                    {message.role === 'user'
                      ? 'You'
                      : 'Research Assistant'}
                  </span>

                  <p>{message.content}</p>

                  {message.role === 'assistant' &&
                    message.sources?.length > 0 && (
                      <div className="chat-sources">
                        <strong>Sources</strong>

                        {message.sources.map(
                          (source, index) => (
                            <div
                              key={`${source.paper_name}-${source.page_number}-${index}`}
                              className="chat-source"
                            >
                              <span>
                                {source.paper_name}
                              </span>

                              <span>
                                Page {source.page_number}
                              </span>

                              <span>
                                Score {source.score.toFixed(3)}
                              </span>
                            </div>
                          ),
                        )}
                      </div>
                    )}
                </div>
              </article>
            ))}

            {chatting && (
              <div className="chat-message assistant">
                <div className="message-avatar">AI</div>

                <div className="message-body">
                  <span className="message-role">
                    Research Assistant
                  </span>

                  <p className="thinking">
                    Thinking<span>.</span><span>.</span><span>.</span>
                  </p>
                </div>
              </div>
            )}
          </div>

          <form
            className="chat-form"
            onSubmit={handleChat}
          >
            <input
              type="text"
              value={chatQuestion}
              onChange={(event) => {
                setChatQuestion(event.target.value)
                setChatError('')
              }}
              placeholder="Ask anything about your uploaded papers..."
              disabled={chatting}
            />

            <button
              type="submit"
              className="primary-btn"
              disabled={chatting}
            >
              {chatting ? 'Thinking...' : 'Ask AI'}
            </button>
          </form>

          {chatError && (
            <div className="error-message">
              {chatError}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}

export default App