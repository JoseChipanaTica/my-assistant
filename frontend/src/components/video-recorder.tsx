'use client'

import { MutableRefObject, useEffect, useRef, useState } from 'react'

export const VideoRecorder: React.FC = () => {
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null)
  const videoRef: MutableRefObject<HTMLVideoElement | null> = useRef(null)
  const [audioSocket, setAudioSocket] = useState<WebSocket | null>(null)
  const [videoSocket, setVideoSocket] = useState<WebSocket | null>(null)
  const audioContextRef: MutableRefObject<AudioContext | null> = useRef(null)
  const videoCanvasRef: MutableRefObject<HTMLCanvasElement | null> = useRef(null)

  useEffect(() => {
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

    const initAudioWebSocket = () => {
      const ws = new WebSocket('ws://127.0.0.1:8000/ws/audio')
      ws.onopen = () => {
        console.log('WebSocket connection established')
      }

      ws.onmessage = async event => {
        const arrayBuffer = await event.data.arrayBuffer()
        playAudio(arrayBuffer)
      }

      ws.onerror = error => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket connection closed')
      }
      setAudioSocket(ws)
    }

    const initVideoWebSocket = () => {
      const ws = new WebSocket('ws://127.0.0.1:8000/ws/video')
      ws.onopen = () => {
        console.log('WebSocket connection established')
      }
      ws.onerror = error => {
        console.error('WebSocket error:', error)
      }
      ws.onclose = () => {
        console.log('WebSocket connection closed')
      }
      setVideoSocket(ws)
    }

    getMedia()
    initAudioWebSocket()
    initVideoWebSocket()

    return () => {
      if (audioSocket) {
        audioSocket.close()
      }

      if (videoSocket) {
        videoSocket.close()
      }

      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const startRecording = (stream: MediaStream) => {
    const audioStream = new MediaStream(stream.getAudioTracks())

    const recorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' })
    recorder.ondataavailable = (event: BlobEvent) => {
      if (event.data.size > 0) {
        if (audioSocket && audioSocket.readyState === WebSocket.OPEN) {
          audioSocket.send(event.data)
        }
      }
    }

    recorder.onstop = () => {}

    recorder.start(1000 * 2)
    setIsRecording(true)
  }

  const startVideoCapture = (stream: MediaStream) => {
    if (!videoCanvasRef.current) {
      const canvas = document.createElement('canvas')
      videoCanvasRef.current = canvas
    }

    const captureFrame = () => {
      if (videoRef.current && videoCanvasRef.current) {
        const context = videoCanvasRef.current.getContext('2d')
        if (context) {
          videoCanvasRef.current.width = videoRef.current.videoWidth
          videoCanvasRef.current.height = videoRef.current.videoHeight
          context.drawImage(videoRef.current, 0, 0, videoCanvasRef.current.width, videoCanvasRef.current.height)
          videoCanvasRef.current.toBlob(blob => {
            if (blob) {
              if (videoSocket && videoSocket.readyState === WebSocket.OPEN) {
                videoSocket.send(blob)
              }
            }
          }, 'image/jpeg')
        }
      }
      setTimeout(captureFrame, 1000 * 2)
    }

    captureFrame()
    setIsRecording(true)
  }

  const stopRecording = () => {
    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
    }
    setIsRecording(false)
  }

  const playAudio = async (audioBytes: ArrayBuffer) => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
    }

    const audioContext = audioContextRef.current

    try {
      const audioBuffer = await audioContext.decodeAudioData(audioBytes)
      const source = audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(audioContext.destination)
      source.start(0)
    } catch (error) {
      console.error('Error decoding audio data:', error)
    }
  }

  return (
    <div>
      <video ref={videoRef} autoPlay muted style={{ width: '100%' }} />
      <div>
        {isRecording ? (
          <button onClick={stopRecording}>Stop Recording</button>
        ) : (
          <button
            onClick={() => {
              if (mediaStream) {
                startRecording(mediaStream), startVideoCapture(mediaStream)
              }
            }}
          >
            Start Recording
          </button>
        )}
      </div>
    </div>
  )
}
