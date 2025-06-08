import os
import logging
from typing import List, Dict, Optional, Tuple
from google.cloud import speech, texttospeech
from google.api_core import retry
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result
)
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Enum,
    Info
)
import time
import datetime
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OrchestrateXVoiceAgent')

class VoiceAgentError(Exception):
    """Base exception for VoiceAgent errors"""
    pass

class InvalidLanguageError(VoiceAgentError):
    """Raised when an unsupported language is requested"""
    pass

class CredentialsError(VoiceAgentError):
    """Raised when credentials are missing or invalid"""
    pass

class AudioProcessingError(VoiceAgentError):
    """Raised when audio processing fails"""
    pass

class NetworkError(VoiceAgentError):
    """Raised when network communication fails"""
    pass

class VoiceAgentConfig:
    SUPPORTED_LANGUAGES = [
        "en-US", "zh-CN", "hi-IN", "es-ES", "fr-FR", "ar-SA",
        "bn-BD", "pt-BR", "ru-RU", "ja-JP", "de-DE", "ur-PK"
    ]
    
    def __init__(self):
        self._validate_credentials()
        self._validate_environment()
        self._initialize_metrics()
        
    def _validate_credentials(self):
        """Verify Google Cloud credentials are properly configured"""
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path or not os.path.exists(creds_path):
            logger.critical("Google Cloud credentials not found")
            raise CredentialsError(
                "Google Cloud credentials file not found at specified path. "
                "Set GOOGLE_APPLICATION_CREDENTIALS environment variable."
            )

    def _validate_environment(self):
        """Validate required environment variables"""
        required_vars = [
            "GOOGLE_APPLICATION_CREDENTIALS",
            "VOICE_AGENT_MAX_RETRIES",
            "VOICE_AGENT_RETRY_DELAY",
            "VOICE_AGENT_TIMEOUT",
            "VOICE_AGENT_MAX_QUEUE_SIZE"
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

    def _initialize_metrics(self):
        """Initialize Prometheus metrics"""
        # Latency metrics
        self.voice_latency = Histogram(
            'orchestratex_voiceagent_latency_seconds',
            'Voice processing latency in seconds',
            ['operation', 'language', 'status']
        )

        # Error metrics
        self.voice_errors = Counter(
            'orchestratex_voiceagent_errors_total',
            'Number of voice processing errors',
            ['operation', 'language', 'error_type', 'cause']
        )

        # Success metrics
        self.voice_success = Counter(
            'orchestratex_voiceagent_success_total',
            'Number of successful voice operations',
            ['operation', 'language']
        )

        # Queue metrics
        self.voice_queue_size = Gauge(
            'orchestratex_voiceagent_queue_size',
            'Current size of voice processing queue',
            ['operation']
        )

        # Agent status
        self.agent_status = Enum(
            'orchestratex_voiceagent_status',
            'Voice agent status',
            states=['running', 'error', 'stopped', 'overloaded']
        )

        # Audio quality metrics
        self.audio_quality = Gauge(
            'orchestratex_voiceagent_audio_quality',
            'Audio quality metrics',
            ['metric', 'language']
        )

        # Emotion metrics
        self.emotion_confidence = Gauge(
            'orchestratex_voiceagent_emotion_confidence',
            'Emotion detection confidence scores',
            ['emotion', 'language']
        )

class VoiceAgent:
    def __init__(self):
        self.config = VoiceAgentConfig()
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.current_language = "en-US"
        self._queue = []
        self._initialize_error_handlers()
        
    def _initialize_error_handlers(self):
        """Initialize error handlers for different scenarios"""
        self.error_handlers = {
            'network': self._handle_network_error,
            'audio_processing': self._handle_audio_processing_error,
            'language': self._handle_language_error,
            'authentication': self._handle_auth_error
        }

    def _handle_network_error(self, error):
        """Handle network-related errors"""
        self.config.voice_errors.labels(
            operation='network',
            language=self.current_language,
            error_type=type(error).__name__,
            cause='network_failure'
        ).inc()
        logger.error(f"Network error: {str(error)}")
        self.config.agent_status.state('error')
        raise NetworkError(f"Network error: {str(error)}")

    def _handle_audio_processing_error(self, error):
        """Handle audio processing errors"""
        self.config.voice_errors.labels(
            operation='audio_processing',
            language=self.current_language,
            error_type=type(error).__name__,
            cause='audio_failure'
        ).inc()
        logger.error(f"Audio processing error: {str(error)}")
        self.config.agent_status.state('error')
        raise AudioProcessingError(f"Audio processing error: {str(error)}")

    def _handle_language_error(self, error):
        """Handle language-related errors"""
        self.config.voice_errors.labels(
            operation='language',
            language=self.current_language,
            error_type=type(error).__name__,
            cause='language_unsupported'
        ).inc()
        logger.error(f"Language error: {str(error)}")
        self.config.agent_status.state('error')
        raise InvalidLanguageError(f"Language error: {str(error)}")

    def _handle_auth_error(self, error):
        """Handle authentication errors"""
        self.config.voice_errors.labels(
            operation='authentication',
            language=self.current_language,
            error_type=type(error).__name__,
            cause='auth_failure'
        ).inc()
        logger.error(f"Authentication error: {str(error)}")
        self.config.agent_status.state('error')
        raise CredentialsError(f"Authentication error: {str(error)}")

    def set_language(self, language_code: str) -> bool:
        """Set the current language for the agent"""
        if language_code not in self.config.SUPPORTED_LANGUAGES:
            self._handle_language_error(
                InvalidLanguageError(f"Unsupported language: {language_code}")
            )
        
        self.current_language = language_code
        logger.info(f"Language set to {language_code}")
        self.config.voice_success.labels(
            operation='language_change',
            language=language_code
        ).inc()
        return True

    @retry(
        stop=stop_after_attempt(int(os.environ.get("VOICE_AGENT_MAX_RETRIES", "3"))),
        wait=wait_exponential(
            multiplier=float(os.environ.get("VOICE_AGENT_RETRY_DELAY", "1")),
            min=2,
            max=10
        ),
        retry=(
            retry_if_exception_type(Exception)  # Retry on general exceptions
            & retry_if_result(lambda result: result is None)
        ),
        reraise=True
    )
    def transcribe_audio(
        self,
        audio_uri: str,
        language_code: str = "en-US",
        alternative_languages: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Transcribe audio with automatic language detection and retry logic
        Args:
            audio_uri: GCS URI of audio file
            language_code: Primary language code
            alternative_languages: List of alternative language codes
        Returns:
            List of transcription results
        Raises:
            InvalidLanguageError: If language is not supported
            Exception: If transcription fails after retries
        """
        try:
            with self.config.voice_latency.labels(
                operation="transcribe",
                language=language_code,
                status="success"
            ).time():
                config = speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=16000,
                    language_code=language_code,
                    alternative_language_codes=alternative_languages or [],
                    enable_automatic_punctuation=True,
                    enable_word_time_offsets=True
                )

                audio = speech.RecognitionAudio(uri=audio_uri)
                response = self.speech_client.recognize(
                    config=config,
                    audio=audio,
                    retry=retry.Retry(
                        deadline=float(os.environ.get("VOICE_AGENT_TIMEOUT", "60")),
                        initial=1.0,
                        maximum=10.0,
                        multiplier=2.0
                    )
                )

                results = []
                for result in response.results:
                    transcript = result.alternatives[0].transcript
                    confidence = result.alternatives[0].confidence
                    results.append({
                        "transcript": transcript,
                        "confidence": confidence,
                        "language": language_code,
                        "timestamp": datetime.now().isoformat()
                    })

                self.config.voice_success.labels(
                    operation="transcribe",
                    language=language_code
                ).inc()
                
                # Update audio quality metrics
                self.config.audio_quality.labels(
                    metric="confidence",
                    language=language_code
                ).set(confidence)

                return results

        except Exception as e:
            self.config.voice_errors.labels(
                operation="transcribe",
                language=language_code,
                error_type=type(e).__name__,
                cause=getattr(e, 'cause', 'unknown')
            ).inc()
            logger.error(f"Transcription error for {language_code}: {str(e)}")
            self._queue.append({
                "operation": "transcribe",
                "uri": audio_uri,
                "language": language_code
            })
            self.config.voice_queue_size.labels(operation="transcribe").inc()
            self._handle_error(e)
            raise

    def _handle_error(self, error):
        """Handle errors with appropriate handler"""
        error_type = type(error).__name__
        handler = self.error_handlers.get(error_type.lower(), self._handle_generic_error)
        handler(error)

    def _handle_generic_error(self, error):
        """Handle generic errors"""
        self.config.voice_errors.labels(
            operation="generic",
            language=self.current_language,
            error_type=type(error).__name__,
            cause="unknown"
        ).inc()
        logger.error(f"Generic error: {str(error)}")
        self.config.agent_status.state('error')
        raise VoiceAgentError(f"Error: {str(error)}")

    def detect_emotion(self, text: str) -> Dict[str, float]:
        """Detect emotions in text using HumeAI/emotion-mesh"""
        try:
            # Simulate emotion detection
            emotions = {
                'happiness': 0.8,
                'sadness': 0.2,
                'anger': 0.1,
                'surprise': 0.3,
                'fear': 0.1,
                'disgust': 0.05,
                'neutral': 0.4
            }
            
            # Update emotion metrics
            for emotion, value in emotions.items():
                self.config.emotion_confidence.labels(
                    emotion=emotion,
                    language=self.current_language
                ).set(value)
            
            return emotions

        except Exception as e:
            self.config.voice_errors.labels(
                operation="emotion_detection",
                language=self.current_language,
                error_type=type(e).__name__,
                cause="emotion_detection_failure"
            ).inc()
            logger.error(f"Emotion detection error: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(int(os.environ.get("VOICE_AGENT_MAX_RETRIES", "3"))),
        wait=wait_exponential(
            multiplier=float(os.environ.get("VOICE_AGENT_RETRY_DELAY", "1")),
            min=2,
            max=10
        ),
        retry=(
            retry_if_exception_type(Exception)  # Retry on general exceptions
            & retry_if_result(lambda result: result is None)
            )
        ),
        reraise=True
    )
    def synthesize_speech(
        self,
        text: str,
        language_code: str = "en-US",
        voice_personality: str = "default",
        speaking_rate: float = 1.0
    ) -> bytes:
        """
        Synthesize speech with personality adaptation
        Args:
            text: Text to synthesize
            language_code: Target language code
            voice_personality: Voice personality (default, friendly, formal)
            speaking_rate: Speech rate (0.25 to 4.0)
        Returns:
            MP3 audio bytes
        Raises:
            InvalidLanguageError: If language is not supported
            Exception: If synthesis fails after retries
        """
        try:
            with VOICE_LATENCY.labels(operation="synthesize", language=language_code).time():
                if language_code not in self.config.SUPPORTED_LANGUAGES:
                    raise InvalidLanguageError(f"Unsupported language: {language_code}")

                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=self._get_voice_name(language_code, voice_personality)
                )

                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speaking_rate,
                    pitch=0.0,
                    volume_gain_db=0.0
                )

                synthesis_input = texttospeech.SynthesisInput(text=text)
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config,
                    retry=retry.Retry(
                        deadline=60,
                        initial=1.0,
                        maximum=10.0,
                        multiplier=2.0
                    )
                )

                return response.audio_content

        except Exception as e:
            VOICE_ERRORS.labels(
                operation="synthesize",
                language=language_code,
                error_type=type(e).__name__
            ).inc()
            logger.error(f"Synthesis error for {language_code}: {str(e)}")
            raise

    def _get_voice_name(self, language_code: str, personality: str) -> str:
        """Get appropriate voice name based on language and personality"""
        # Implementation will depend on available voices for each language
        return f"{language_code}-{personality.capitalize()}"

    async def process_audio_stream(self, audio_stream: bytes) -> Dict[str, Any]:
        """Process audio stream with real-time language detection"""
        try:
            # Split stream into chunks
            chunks = self._split_audio_stream(audio_stream)
            
            # Process each chunk
            results = []
            for chunk in chunks:
                result = await self.transcribe_audio(chunk)
                results.extend(result)
                
                # Emit real-time updates
                await self._emit_realtime_update(result)
            
            return results

        except Exception as e:
            logger.error(f"Stream processing error: {str(e)}")
            raise

    def _split_audio_stream(self, audio_stream: bytes) -> List[bytes]:
        """Split audio stream into chunks"""
        # Implementation will depend on audio format and requirements
        pass

    async def _emit_realtime_update(self, result: Dict[str, Any]) -> None:
        """Emit real-time updates to connected clients"""
        # Implementation will use WebSocket or similar real-time protocol
        pass

    def detect_emotion(self, text: str) -> Dict[str, float]:
        """Detect emotions in text using HumeAI/emotion-mesh"""
        try:
            # Implementation will use HumeAI/emotion-mesh API
            pass
        except Exception as e:
            logger.error(f"Emotion detection error: {str(e)}")
            raise
