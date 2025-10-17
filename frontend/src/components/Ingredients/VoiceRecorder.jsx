import { useState, useRef } from 'react';
import { Mic, Square, Loader } from 'lucide-react';
import { ingredientService } from '../../services/ingredientService';
import { useToast } from '../../hooks/useToast';
import './Ingredients.css';

export default function VoiceRecorder({ onExtract }) {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const timerRef = useRef(null);
  const { addToast } = useToast();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = async () => {
        clearInterval(timerRef.current);
        const blob = new Blob(chunks, { type: 'audio/wav' });
        await processAudio(blob);
        stream.getTracks().forEach(track => track.stop());
        setRecordingTime(0);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
      setRecordingTime(0);
      
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      addToast('Recording started', 'info');
    } catch (error) {
      addToast('Microphone access denied', 'error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && recording) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  const processAudio = async (blob) => {
    setLoading(true);
    try {
      const file = new File([blob], 'recording.wav', { type: 'audio/wav' });
      const response = await ingredientService.extractFromAudio(file);
      
      if (response.ingredients && response.ingredients.length > 0) {
        onExtract(response.ingredients);
        addToast(`Found ${response.ingredients.length} ingredients`, 'success');
      } else {
        addToast('No ingredients detected', 'warning');
      }
    } catch (error) {
      const msg = error.response?.data?.detail || error.message;
      addToast(msg, 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="voice-recorder">
      <h3>Record Ingredients</h3>
      
      <button
        className={`record-btn ${recording ? 'active' : ''}`}
        onClick={recording ? stopRecording : startRecording}
        disabled={loading}
        type="button"
      >
        {loading ? (
          <>
            <Loader size={20} strokeWidth={2} className="spinner-small" />
            Processing...
          </>
        ) : recording ? (
          <>
            <Square size={20} strokeWidth={2} />
            Stop Recording
          </>
        ) : (
          <>
            <Mic size={20} strokeWidth={2} />
            Start Recording
          </>
        )}
      </button>
      
      {recording && <span className="timer">{recordingTime}s</span>}
      <p className="hint">Speak naturally: tomato, chicken, rice...</p>
    </div>
  );
}