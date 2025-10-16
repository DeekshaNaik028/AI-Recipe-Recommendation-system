
// components/Ingredients/VoiceRecorder.jsx
import { useState } from 'react';
import { ingredientService } from '../../services/ingredientService';
import { useToast } from '../../hooks/useToast';
import './Ingredients.css';

export default function VoiceRecorder({ onExtract }) {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        await processAudio(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setRecording(true);
      addToast('Recording started...', 'info');
    } catch (error) {
      addToast('Microphone access denied', 'error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  const processAudio = async (blob) => {
    setLoading(true);
    try {
      const file = new File([blob], 'recording.wav', { type: 'audio/wav' });
      const response = await ingredientService.extractFromAudio(file);
      onExtract(response.ingredients);
      addToast(`Extracted ${response.ingredients.length} ingredients!`, 'success');
    } catch (error) {
      addToast(error.response?.data?.detail || 'Failed to process audio', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="voice-recorder">
      <h3>🎤 Voice Input</h3>
      <button
        className={`record-button ${recording ? 'active' : ''}`}
        onClick={recording ? stopRecording : startRecording}
        disabled={loading}
      >
        {loading ? '⏳ Processing...' : recording ? '⏹️ Stop Recording' : '🎤 Start Recording'}
      </button>
      <p className="recorder-hint">Speak your ingredients naturally</p>
    </div>
  );
}
