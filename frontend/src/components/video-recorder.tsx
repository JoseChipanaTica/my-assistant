'use client'

import { MutableRefObject, useEffect, useRef, useState } from 'react'

export const VideoRecorder: React.FC = () => {
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null)
  const mediaRecorderRef: MutableRefObject<MediaRecorder | null> = useRef(null)
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const videoRef: MutableRefObject<HTMLVideoElement | null> = useRef(null)
  const chunks: MutableRefObject<Blob[]> = useRef([])
  const silenceTimeout: MutableRefObject<NodeJS.Timeout | null> = useRef(null)
  const audioContextRef: MutableRefObject<AudioContext | null> = useRef(null)
  const analyserRef: MutableRefObject<AnalyserNode | null> = useRef(null)
  const dataArrayRef: MutableRefObject<Uint8Array | null> = useRef(null)
  const [shouldRestart, setShouldRestart] = useState<boolean>(true) // New state variable
  const [serverResponse, setServerResponse] = useState<string>('')

  useEffect(() => {
    // Get access to the camera and microphone
    const getMedia = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        setMediaStream(stream)
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
      } catch (err) {
        console.error('Error accessing media devices.', err)
      }
    }

    // Initialize WebSocket connection
    const initWebSocket = () => {
      const ws = new WebSocket('ws://127.0.0.1:8000/ws')
      ws.onopen = () => {
        console.log('WebSocket connection established')
      }
      ws.onerror = error => {
        console.error('WebSocket error:', error)
      }
      ws.onmessage = async event => {
        if (typeof event.data === 'string') {
          console.log('Message received from server:', event.data)
          setServerResponse(event.data) // Set server response to state
        } else {
          console.log('Audio bytes received from server')
          const arrayBuffer = await event.data.arrayBuffer()
          playAudio(arrayBuffer)
        }
      }
      ws.onclose = () => {
        console.log('WebSocket connection closed')
      }
      setSocket(ws)
    }

    getMedia()
    initWebSocket()

    // Cleanup on component unmount
    return () => {
      if (socket) {
        socket.close()
      }
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  const startRecording = (stream: MediaStream) => {
    if (!stream) return

    const recorder = new MediaRecorder(stream)
    mediaRecorderRef.current = recorder

    recorder.ondataavailable = (event: BlobEvent) => {
      if (event.data.size > 0) {
        chunks.current.push(event.data)
      }
    }

    recorder.onstop = () => {
      const blob = new Blob(chunks.current, { type: 'video/webm' })
      chunks.current = []
      console.log('Sending data to server:', blob)
      sendToServer(blob)

      if (shouldRestart) {
        startRecording(stream) // Automatically restart recording
      }
    }

    recorder.start(1000) // Collect data in 1-second intervals

    // Set up Web Audio API to monitor audio levels
    const audioContext = new AudioContext()
    audioContextRef.current = audioContext
    const analyser = audioContext.createAnalyser()
    analyserRef.current = analyser
    const source = audioContext.createMediaStreamSource(stream)
    source.connect(analyser)

    analyser.fftSize = 256
    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    dataArrayRef.current = dataArray

    monitorAudioLevel()
    setIsRecording(true)
  }

  const monitorAudioLevel = () => {
    if (!analyserRef.current || !dataArrayRef.current) return

    analyserRef.current.getByteFrequencyData(dataArrayRef.current)
    // console.log('DataArrayRef Length: ', dataArrayRef.current.length)
    const sum = dataArrayRef.current.reduce((a, b) => a + b, 0)
    // console.log('DataArrayRef Sum: ', sum)

    const average = sum / dataArrayRef.current.length

    if (average > 1 && average < 10) {
      // Adjust this threshold as needed
      if (!silenceTimeout.current) {
        silenceTimeout.current = setTimeout(() => {
          console.log('average', average)
          handleSilenceDetected()
          silenceTimeout.current = null
        }, 2000) // 2 seconds of silence
      }
    } else {
      if (silenceTimeout.current) {
        clearTimeout(silenceTimeout.current)
        silenceTimeout.current = null
      }
    }

    requestAnimationFrame(monitorAudioLevel)
  }

  const handleSilenceDetected = () => {
    console.log('Silence detected, user finished talking.')
    stopRecording()
  }

  const sendToServer = (data: Blob) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(data)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
    }
    setIsRecording(false)
  }

  const dropRecording = () => {
    setShouldRestart(false) // Prevent automatic restart
    stopRecording()
  }

  const playAudio = async (arrayBuffer: ArrayBuffer) => {
    if (!audioContextRef.current) return

    try {
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer)
      const source = audioContextRef.current.createBufferSource()
      source.buffer = audioBuffer
      source.connect(audioContextRef.current.destination)
      source.start()
    } catch (error) {
      console.error('Error decoding audio data:', error)
    }
  }

  return (
    <div>
      <video ref={videoRef} autoPlay muted style={{ width: '100%' }} />
      <div>
        {isRecording ? (
          <button onClick={dropRecording}>Stop Recording</button>
        ) : (
          <button onClick={() => mediaStream && startRecording(mediaStream)}>Start Recording</button>
        )}
      </div>

      <div>
        <p>Server Response: {serverResponse}</p>
      </div>
    </div>
  )
}
