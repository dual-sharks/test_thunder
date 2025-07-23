// Allow streaming responses up to 30 seconds
export const maxDuration = 30

export async function POST(req: Request) {
  const { messages } = await req.json()

  try {
    // Get the last user message
    const lastMessage = messages[messages.length - 1]
    const question = lastMessage?.content || ''

    if (!question) {
      return new Response(
        JSON.stringify({ error: 'No question provided' }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    // Call the Flask backend
    const flaskResponse = await fetch('http://localhost:5001/ask-with-tools', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    })

    if (!flaskResponse.ok) {
      throw new Error(`Flask backend responded with status: ${flaskResponse.status}`)
    }

    const data = await flaskResponse.json()

    if (!data.success) {
      throw new Error(data.error || 'Unknown error from backend')
    }

    // Create a streaming response from the backend result
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      start(controller) {
        // Stream the response content
        const content = data.llm_response || data.content || 'No response from backend'
        const chunks = content.split(' ')
        
        let i = 0
        const sendChunk = () => {
          if (i < chunks.length) {
            const chunk = (i === 0 ? chunks[i] : ' ' + chunks[i])
            controller.enqueue(encoder.encode(`data: {"content":"${chunk.replace(/"/g, '\\"')}"}\n\n`))
            i++
            setTimeout(sendChunk, 50) // Add small delay for streaming effect
          } else {
            controller.enqueue(encoder.encode('data: [DONE]\n\n'))
            controller.close()
          }
        }
        
        sendChunk()
      }
    })

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Transfer-Encoding': 'chunked',
      },
    })

  } catch (error) {
    console.error('Error calling Flask backend:', error)
    
    return new Response(
      JSON.stringify({ 
        error: 'Failed to process your question. Please make sure the DuckDB service is running.',
        details: error instanceof Error ? error.message : 'Unknown error'
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}
