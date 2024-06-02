'use client'

import { MutableRefObject, useEffect, useRef, useState } from 'react'

export const VideoRecorder: React.FC = () => {
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null)
  const videoRef: MutableRefObject<HTMLVideoElement | null> = useRef(null)
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const audioContextRef: MutableRefObject<AudioContext | null> = useRef(null)
  const videoCanvasRef: MutableRefObject<HTMLCanvasElement | null> = useRef(null)
  const [audioQueue, setAudioQueue] = useState<any[]>([])

  const enqueueAudio = (audioBytes: any) => {
    setAudioQueue(prevQueue => [...prevQueue, audioBytes])
  }

  function blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        if (reader.result) {
          const base64data = reader.result.toString().split(',')[1] // Extract Base64 part
          resolve(base64data)
        } else {
          reject('Error converting Blob to Base64')
        }
      }
      reader.onerror = () => reject(reader.error)
      reader.readAsDataURL(blob)
    })
  }

  const getMedia = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: true })

      setMediaStream(stream)

      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (err) {
      console.error('Error accessing media devices.', err)
    }
  }

  const recording = async () => {
    if (!mediaStream) {
      await getMedia()
    }
    setIsRecording(true)
    startRecording()
    startVideoCapture()
  }

  const startRecording = () => {
    if (!mediaStream) {
      return
    }
    const audioStream = new MediaStream(mediaStream.getAudioTracks())
    const recorder = new MediaRecorder(audioStream, { mimeType: 'audio/webm' })
    recorder.ondataavailable = async (event: BlobEvent) => {
      if (event.data.size > 0) {
        if (socket && socket.readyState === WebSocket.OPEN) {
          const audioBlob = new Blob([event.data], { type: 'audio/wav' })
          const audioString = await blobToBase64(audioBlob)
          const data = JSON.stringify({ type: 'audio', audio: audioString })
          socket.send(data)
        }
      }
    }

    recorder.onstop = () => {}

    recorder.start(1000 * 1)
  }

  const startVideoCapture = () => {
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
          videoCanvasRef.current.toBlob(async blob => {
            if (blob) {
              if (socket && socket.readyState === WebSocket.OPEN) {
                const frameString = await blobToBase64(blob)
                const data = JSON.stringify({ type: 'frame', frame: frameString })
                socket.send(data)
              }
            }
          }, 'image/jpeg')
        }
      }
      setTimeout(captureFrame, 1000 * 2)
    }

    captureFrame()
  }

  const stopRecording = () => {
    setIsRecording(false)

    if (mediaStream) {
      mediaStream.getTracks().forEach(track => track.stop())
      setMediaStream(null)
    }

    if (socket) {
      socket.close()
    }
  }

  const playNextAudio = async () => {
    if (audioQueue.length === 0) return

    const audioBytes = audioQueue[0]

    if (!audioContextRef.current) {
      // @ts-ignore
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)()
    }

    const audioContext = audioContextRef.current

    try {
      const audioBuffer = await audioContext.decodeAudioData(audioBytes)
      const source = audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(audioContext.destination)
      source.start(0)

      source.onended = () => {
        setAudioQueue(prevQueue => prevQueue.slice(1))
      }
    } catch (error) {
      console.error('Error decoding audio data:', error)
      setAudioQueue(prevQueue => prevQueue.slice(1))
    }
  }

  useEffect(() => {
    if (audioQueue.length > 0) {
      playNextAudio()
    }
  }, [audioQueue])

  useEffect(() => {
    const initSocket = () => {
      const ws = new WebSocket(`${process.env.NEXT_PUBLIC_WEBSOCKET_SERVICE}/ws/13`)
      ws.onopen = () => {
        console.log('WebSocket connection established')
      }

      ws.onmessage = async event => {
        const arrayBuffer = await event.data.arrayBuffer()
        enqueueAudio(arrayBuffer)
      }

      ws.onerror = error => {
        console.error('WebSocket error:', error)
      }

      ws.onclose = () => {
        console.log('WebSocket connection closed')
      }
      setSocket(ws)
    }

    getMedia()
    initSocket()

    return () => {
      if (socket) {
        socket.close()
      }
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  return (
    <div className="h-screen w-screen">
      <div className="h-full flex flex-col justify-center items-center">
        <video className="w-full h-full" ref={videoRef} autoPlay muted playsInline style={{ width: '50%' }} />
        <div className="flex p-2">
          {isRecording ? (
            <button className="bg-blue-600 rounded-3xl p-4" onClick={stopRecording}>
              Stop Recording
            </button>
          ) : (
            <button className="bg-blue-600 rounded-3xl p-4" onClick={recording}>
              Start Recording
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
