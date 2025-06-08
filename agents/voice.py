from .base import AgentBase
import os

class VoiceAgent(AgentBase):
    def __init__(self, name="VoiceAgent"):
        super().__init__(name, "Conversational AI")
        self._check_google_credentials()
    
    def _check_google_credentials(self):
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            print("Warning: Google Cloud credentials not found. Voice features will be limited.")
    
    def transcribe(self, audio_file_path: str, language_code: str = "en-US") -> str:
        try:
            from google.cloud import speech
            client = speech.SpeechClient()
            
            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
            )
            
            response = client.recognize(config=config, audio=audio)
            transcripts = [result.alternatives[0].transcript 
                         for result in response.results]
            return " ".join(transcripts)
        except ImportError:
            return "Google Speech-to-Text client not available"
        except Exception as e:
            return f"Transcription error: {str(e)}"
    
    def synthesize(self, text: str, language_code: str = "en-US", 
                  speaking_rate: float = 1.0, voice_name: str = None) -> str:
        try:
            from google.cloud import texttospeech
            client = texttospeech.TextToSpeechClient()
            
            input_text = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
                name=voice_name
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=speaking_rate
            )
            
            response = client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )
            
            output_path = "output.mp3"
            with open(output_path, "wb") as out:
                out.write(response.audio_content)
            
            return output_path
        except ImportError:
            return "Google Text-to-Speech client not available"
        except Exception as e:
            return f"Synthesis error: {str(e)}
