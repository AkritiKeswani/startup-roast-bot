import React, { useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

interface Company {
  name: string
  website: string
}

interface Result {
  company: Company
  roast: string
  screenshot_url?: string
  status: string
  reason?: string
}

interface RunRequest {
  source: 'yc' | 'custom'
  yc: {
    batch?: string
    limit: number
  }
  custom: {
    urls: string[]
  }
  style: 'spicy' | 'kind' | 'deadpan'
  max_steps: number
}

function App() {
  const [results, setResults] = useState<Result[]>([])
  const [logs, setLogs] = useState<string[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [runId, setRunId] = useState<string | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)
  
  const [formData, setFormData] = useState<RunRequest>({
    source: 'yc',
    yc: { batch: '', limit: 24 },
    custom: { urls: [''] },
    style: 'spicy',
    max_steps: 6
  })

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const startRun = async () => {
    try {
      setIsRunning(true)
      setResults([])
      setLogs([])
      addLog('Starting roast session...')

      const response = await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      setRunId(data.run_id)
      addLog(`Run started: ${data.run_id}`)

      // Connect to WebSocket
      const wsUrl = API_BASE.replace(/^http/, 'ws') + data.stream_url
      const newWs = new WebSocket(wsUrl)
      
      newWs.onopen = () => {
        addLog('Connected to stream')
      }
      
      newWs.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.status === 'finished') {
          addLog('Run completed!')
          setIsRunning(false)
          newWs.close()
          setWs(null)
        } else if (data.status === 'error') {
          addLog(`Error: ${data.error}`)
          setIsRunning(false)
          newWs.close()
          setWs(null)
        } else if (data.company) {
          setResults(prev => [...prev, data])
          addLog(`Processed: ${data.company.name}`)
        }
      }
      
      newWs.onerror = (error) => {
        addLog(`WebSocket error: ${error}`)
        setIsRunning(false)
      }
      
      setWs(newWs)
    } catch (error) {
      addLog(`Error: ${error}`)
      setIsRunning(false)
    }
  }

  const stopRun = () => {
    if (ws) {
      ws.close()
      setWs(null)
    }
    setIsRunning(false)
    addLog('Run stopped')
  }

  const updateFormData = (field: string, value: any) => {
    setFormData(prev => {
      const newData = { ...prev }
      const keys = field.split('.')
      let current = newData
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]]
      }
      
      current[keys[keys.length - 1]] = value
      return newData
    })
  }

  const addCustomUrl = () => {
    setFormData(prev => ({
      ...prev,
      custom: {
        ...prev.custom,
        urls: [...prev.custom.urls, '']
      }
    }))
  }

  const updateCustomUrl = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      custom: {
        ...prev.custom,
        urls: prev.custom.urls.map((url, i) => i === index ? value : url)
      }
    }))
  }

  const removeCustomUrl = (index: number) => {
    setFormData(prev => ({
      ...prev,
      custom: {
        ...prev.custom,
        urls: prev.custom.urls.filter((_, i) => i !== index)
      }
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          🍖 Startup Roast Bot
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Controls Panel */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Configuration</h2>
            
            <div className="space-y-4">
              {/* Source Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Source
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="yc"
                      checked={formData.source === 'yc'}
                      onChange={(e) => updateFormData('source', e.target.value)}
                      className="mr-2"
                    />
                    YC Companies
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="custom"
                      checked={formData.source === 'custom'}
                      onChange={(e) => updateFormData('source', e.target.value)}
                      className="mr-2"
                    />
                    Custom URLs
                  </label>
                </div>
              </div>

              {/* YC Configuration */}
              {formData.source === 'yc' && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Batch (optional)
                    </label>
                    <input
                      type="text"
                      value={formData.yc.batch || ''}
                      onChange={(e) => updateFormData('yc.batch', e.target.value)}
                      placeholder="e.g., F25, S25"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Limit
                    </label>
                    <input
                      type="number"
                      value={formData.yc.limit}
                      onChange={(e) => updateFormData('yc.limit', parseInt(e.target.value))}
                      min="1"
                      max="100"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              )}

              {/* Custom URLs */}
              {formData.source === 'custom' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URLs
                  </label>
                  <div className="space-y-2">
                    {formData.custom.urls.map((url, index) => (
                      <div key={index} className="flex space-x-2">
                        <input
                          type="url"
                          value={url}
                          onChange={(e) => updateCustomUrl(index, e.target.value)}
                          placeholder="https://example.com"
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                          onClick={() => removeCustomUrl(index)}
                          className="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={addCustomUrl}
                      className="w-full px-3 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                    >
                      Add URL
                    </button>
                  </div>
                </div>
              )}

              {/* Style Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Roast Style
                </label>
                <select
                  value={formData.style}
                  onChange={(e) => updateFormData('style', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="spicy">🌶️ Spicy</option>
                  <option value="kind">😊 Kind</option>
                  <option value="deadpan">😐 Deadpan</option>
                </select>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-4">
                <button
                  onClick={startRun}
                  disabled={isRunning}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {isRunning ? 'Running...' : '🍖 Roast Landing Pages'}
                </button>
                {isRunning && (
                  <button
                    onClick={stopRun}
                    className="px-6 py-3 bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    Stop
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Results Panel */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4">Results</h2>
            
            {results.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No results yet. Start a roast session to see companies here.
              </p>
            ) : (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {results.map((result, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-lg">{result.company.name}</h3>
                      <span className={`px-2 py-1 rounded text-xs ${
                        result.status === 'done' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {result.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{result.company.website}</p>
                    {result.roast && (
                      <p className="text-gray-800 italic">"{result.roast}"</p>
                    )}
                    {result.reason && (
                      <p className="text-sm text-red-600">Error: {result.reason}</p>
                    )}
                    {result.screenshot_url && (
                      <img 
                        src={result.screenshot_url} 
                        alt={`${result.company.name} screenshot`}
                        className="mt-2 max-w-full h-32 object-cover rounded"
                      />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Logs Panel */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Logs</h2>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-48 overflow-y-auto">
            {logs.length === 0 ? (
              <p className="text-gray-500">No logs yet...</p>
            ) : (
              logs.map((log, index) => (
                <div key={index}>{log}</div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App