'use client'

import React, { useState, useEffect, useRef } from 'react'

interface VoiceCommandResponse {
  success: boolean
  operation: string
  message: string
  action?: string
  parameters?: Record<string, any>
  api_endpoint?: string
  method?: string
  suggestions?: string[]
}

interface VoiceCommandInterfaceProps {
  onCommandProcessed?: (response: VoiceCommandResponse) => void
  onError?: (error: string) => void
}

export default function VoiceCommandInterface({ 
  onCommandProcessed, 
  onError 
}: VoiceCommandInterfaceProps) {
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [lastCommand, setLastCommand] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [availableCommands, setAvailableCommands] = useState<any[]>([])
  const [showHelp, setShowHelp] = useState(false)
  
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    // Check if speech recognition is supported
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      if (SpeechRecognition) {
        setIsSupported(true)
        recognitionRef.current = new SpeechRecognition()
        setupRecognition()
      }
    }

    // Load available commands
    loadAvailableCommands()

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  const setupRecognition = () => {
    if (!recognitionRef.current) return

    const recognition = recognitionRef.current
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
      setTranscript('')
    }

    recognition.onresult = (event) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript
        } else {
          interimTranscript += transcript
        }
      }

      setTranscript(finalTranscript || interimTranscript)
    }

    recognition.onend = () => {
      setIsListening(false)
      if (transcript.trim()) {
        processVoiceCommand(transcript.trim())
      }
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
      onError?.(`Speech recognition error: ${event.error}`)
    }
  }

  const loadAvailableCommands = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/voice/available-commands')
      const data = await response.json()
      if (data.ok) {
        setAvailableCommands(data.data.commands)
      }
    } catch (error) {
      console.error('Failed to load available commands:', error)
    }
  }

  const processVoiceCommand = async (command: string) => {
    if (!command.trim()) return

    setIsProcessing(true)
    setLastCommand(command)

    try {
      const response = await fetch('http://localhost:8000/api/voice/process-command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: command,
          user_id: 'frontend_user'
        })
      })

      const data = await response.json()
      
      if (data.ok) {
        const voiceResponse = data.data.voice_response as VoiceCommandResponse
        onCommandProcessed?.(voiceResponse)
        
        // If the command was successful and has an API endpoint, execute it
        if (voiceResponse.success && voiceResponse.api_endpoint) {
          await executeCommand(voiceResponse)
        }
      } else {
        onError?.(data.error?.message || 'Failed to process voice command')
      }
    } catch (error) {
      console.error('Error processing voice command:', error)
      onError?.(`Network error: ${error}`)
    } finally {
      setIsProcessing(false)
    }
  }

  const executeCommand = async (voiceResponse: VoiceCommandResponse) => {
    try {
      const { api_endpoint, method, parameters } = voiceResponse
      
      if (!api_endpoint) return

      let url = api_endpoint
      if (parameters?.artifact_id && url.includes('{artifact_id}')) {
        url = url.replace('{artifact_id}', parameters.artifact_id)
      }

      const options: RequestInit = {
        method: method || 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      }

      if (method === 'POST' && parameters) {
        options.body = JSON.stringify(parameters)
      }

      const response = await fetch(url, options)
      const data = await response.json()
      
      if (data.ok) {
        console.log('Command executed successfully:', data)
      } else {
        console.error('Command execution failed:', data)
        onError?.(`Command execution failed: ${data.error?.message || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error executing command:', error)
      onError?.(`Command execution error: ${error}`)
    }
  }

  const startListening = () => {
    if (!recognitionRef.current || isListening) return
    
    try {
      recognitionRef.current.start()
    } catch (error) {
      console.error('Error starting speech recognition:', error)
      onError?.('Failed to start voice recognition')
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }

  const handleManualCommand = () => {
    if (transcript.trim()) {
      processVoiceCommand(transcript.trim())
    }
  }

  if (!isSupported) {
    return (
      <div className="voice-interface">
        <div className="error-message">
          <h3>🎤 Voice Commands Not Supported</h3>
          <p>Your browser doesn't support speech recognition. Please use a modern browser like Chrome, Edge, or Safari.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="voice-interface">
      <div className="voice-header">
        <h3>🎤 Voice Commands</h3>
        <button 
          className="help-button"
          onClick={() => setShowHelp(!showHelp)}
        >
          {showHelp ? 'Hide Help' : 'Show Help'}
        </button>
      </div>

      {showHelp && (
        <div className="voice-help">
          <h4>Available Commands:</h4>
          <ul>
            {availableCommands.map((cmd, index) => (
              <li key={index}>
                <strong>{cmd.operation.replace('_', ' ')}:</strong> {cmd.description}
                <br />
                <em>Examples: {cmd.examples.join(', ')}</em>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="voice-controls">
        <div className="voice-button-container">
          <button
            className={`voice-button ${isListening ? 'listening' : ''}`}
            onClick={isListening ? stopListening : startListening}
            disabled={isProcessing}
          >
            {isListening ? '🛑 Stop Listening' : '🎤 Start Listening'}
          </button>
        </div>

        <div className="voice-status">
          {isListening && <span className="status listening">🎤 Listening...</span>}
          {isProcessing && <span className="status processing">⚙️ Processing...</span>}
          {!isListening && !isProcessing && <span className="status ready">✅ Ready</span>}
        </div>
      </div>

      <div className="voice-transcript">
        <label htmlFor="transcript">Transcript:</label>
        <textarea
          id="transcript"
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder="Speak or type your command here..."
          rows={3}
        />
        <button 
          className="process-button"
          onClick={handleManualCommand}
          disabled={!transcript.trim() || isProcessing}
        >
          Process Command
        </button>
      </div>

      {lastCommand && (
        <div className="last-command">
          <h4>Last Command:</h4>
          <p>"{lastCommand}"</p>
        </div>
      )}

      <style jsx>{`
        .voice-interface {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
          margin: 20px 0;
        }

        .voice-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }

        .voice-header h3 {
          margin: 0;
          color: #495057;
        }

        .help-button {
          background: #6c757d;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
        }

        .help-button:hover {
          background: #5a6268;
        }

        .voice-help {
          background: #e9ecef;
          border-radius: 4px;
          padding: 15px;
          margin-bottom: 15px;
        }

        .voice-help h4 {
          margin-top: 0;
          color: #495057;
        }

        .voice-help ul {
          margin: 10px 0;
          padding-left: 20px;
        }

        .voice-help li {
          margin-bottom: 10px;
          color: #6c757d;
        }

        .voice-controls {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 15px;
        }

        .voice-button {
          background: #007bff;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
          font-weight: 500;
          transition: all 0.2s;
        }

        .voice-button:hover:not(:disabled) {
          background: #0056b3;
        }

        .voice-button:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }

        .voice-button.listening {
          background: #dc3545;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.7; }
          100% { opacity: 1; }
        }

        .voice-status {
          display: flex;
          align-items: center;
        }

        .status {
          padding: 6px 12px;
          border-radius: 4px;
          font-size: 14px;
          font-weight: 500;
        }

        .status.listening {
          background: #fff3cd;
          color: #856404;
        }

        .status.processing {
          background: #d1ecf1;
          color: #0c5460;
        }

        .status.ready {
          background: #d4edda;
          color: #155724;
        }

        .voice-transcript {
          margin-bottom: 15px;
        }

        .voice-transcript label {
          display: block;
          margin-bottom: 5px;
          font-weight: 500;
          color: #495057;
        }

        .voice-transcript textarea {
          width: 100%;
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-family: inherit;
          font-size: 14px;
          resize: vertical;
        }

        .voice-transcript textarea:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .process-button {
          background: #28a745;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          margin-top: 10px;
        }

        .process-button:hover:not(:disabled) {
          background: #218838;
        }

        .process-button:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }

        .last-command {
          background: #e9ecef;
          border-radius: 4px;
          padding: 10px;
        }

        .last-command h4 {
          margin: 0 0 5px 0;
          color: #495057;
        }

        .last-command p {
          margin: 0;
          color: #6c757d;
          font-style: italic;
        }

        .error-message {
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
          border-radius: 4px;
          padding: 15px;
          text-align: center;
        }

        .error-message h3 {
          margin-top: 0;
        }
      `}</style>
    </div>
  )
}

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition
    webkitSpeechRecognition: typeof SpeechRecognition
  }
}
