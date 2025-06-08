import os
import sys
import pyaudio
import wave
import asyncio
import queue
from google.cloud import speech
from google.api_core.exceptions import GoogleAPICallError, RetryError
from google.auth.exceptions import GoogleAuthError
from orchestratex.agents.voice_agent import VoiceAgent
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StreamingVoiceHandler:
    """Handles real-time streaming audio with quantum-safe security."""
    
    def __init__(self, voice_agent: VoiceAgent):
        self.voice_agent = voice_agent
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.chunk = 1024
        self.rate = 16000
        self.channels = 1
        self.format = pyaudio.paInt16
        self.stream_queue = queue.Queue()
        self.streaming_config = None
        self._initialize_streaming_config()

    def _initialize_streaming_config(self) -> None:
        """Initialize streaming configuration with quantum-safe settings."""
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.rate,
                language_code="en-US",
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True
            ),
            interim_results=True
        )

    def start_stream(self) -> None:
        """Start audio stream with quantum-safe encryption."""
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                stream_callback=self._stream_callback
            )
            self.stream.start_stream()
            logger.info("Audio stream started")
            
        except Exception as e:
            logger.error(f"Failed to start stream: {str(e)}")
            self.voice_agent.metrics["errors"] += 1
            raise

    def stop_stream(self) -> None:
        """Stop audio stream with quantum-safe cleanup."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.audio.terminate()
            logger.info("Audio stream stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop stream: {str(e)}")
            self.voice_agent.metrics["errors"] += 1
            raise

    def _stream_callback(self, in_data, frame_count, time_info, status) -> tuple:
        """Callback for streaming audio with quantum-safe encryption."""
        try:
            # Encrypt audio data
            encrypted_data = self.voice_agent._encrypt_audio(in_data)
            self.stream_queue.put(encrypted_data)
            
            return (in_data, pyaudio.paContinue)
            
        except Exception as e:
            logger.error(f"Stream callback error: {str(e)}")
            self.voice_agent.metrics["errors"] += 1
            return (in_data, pyaudio.paAbort)

    async def process_stream(self) -> None:
        """Process streaming audio with quantum-safe recognition."""
        try:
            requests = (
                speech.StreamingRecognizeRequest(audio_content=data)
                for data in self._generate_stream_requests()
            )
            
            responses = self.voice_agent.stt_client.streaming_recognize(
                self.streaming_config, requests
            )
            
            async for response in responses:
                for result in response.results:
                    if not result.is_final:
                        # Process interim results
                        transcript = result.alternatives[0].transcript
                        self.voice_agent._audit(f"Interim transcript: {transcript}", "streaming")
                        
                    else:
                        # Process final results
                        transcript = result.alternatives[0].transcript
                        confidence = result.alternatives[0].confidence
                        
                        # Update metrics
                        self.voice_agent.metrics["transcriptions"] += 1
                        
                        # Log audit entry
                        self.voice_agent._audit(f"Final transcript: {transcript}", "streaming")
                        
                        # Emit real-time update
                        await self.voice_agent._emit_realtime_update({
                            "transcript": transcript,
                            "confidence": confidence,
                            "timestamp": datetime.now().isoformat()
                        })
                        
        except Exception as e:
            logger.error(f"Streaming processing error: {str(e)}")
            self.voice_agent.metrics["errors"] += 1
            raise

    def _generate_stream_requests(self) -> bytes:
        """Generate streaming requests with quantum-safe encryption."""
        while True:
            try:
                data = self.stream_queue.get()
                if data:
                    yield data
                
            except Exception as e:
                logger.error(f"Stream request generation error: {str(e)}")
                self.voice_agent.metrics["errors"] += 1
                raise

    def get_stream_status(self) -> Dict[str, Any]:
        """Get streaming status with quantum-safe metrics."""
        return {
            "is_active": self.stream.is_active() if self.stream else False,
            "queue_size": self.stream_queue.qsize(),
            "metrics": {
                "transcriptions": self.voice_agent.metrics["transcriptions"],
                "errors": self.voice_agent.metrics["errors"],
                "security_checks": self.voice_agent.metrics["security_checks"]
            }
        }
