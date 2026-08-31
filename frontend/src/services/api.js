const API_BASE_URL = 'http://127.0.0.1:8000'

async function handleResponse(response) {
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Something went wrong')
  }

  return data
}

export async function getPapers() {
  const response = await fetch(`${API_BASE_URL}/papers`)
  return handleResponse(response)
}

export async function uploadPaper(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/papers/upload`, {
    method: 'POST',
    body: formData,
  })

  return handleResponse(response)
}

export async function deletePaper(paperId) {
  const response = await fetch(
    `${API_BASE_URL}/papers/${paperId}`,
    {
      method: 'DELETE',
    },
  )

  return handleResponse(response)
}

export async function searchPapers(query, topK = 5) {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      top_k: topK,
    }),
  })

  return handleResponse(response)
}

export async function chatWithPapers(question, topK = 5) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question,
      top_k: topK,
    }),
  })

  return handleResponse(response)
}
