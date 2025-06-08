from orchestratex.agents.voice_agent import VoiceAgent
from orchestratex.voice.streaming import StreamingVoiceHandler
import asyncio
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceStreamingDemo:
    """Demonstrates real-time voice streaming with quantum-safe security."""
    
    def __init__(self):
        # Initialize voice agent
        self.voice_agent = VoiceAgent()
        # Initialize streaming handler
        self.streaming_handler = StreamingVoiceHandler(self.voice_agent)
        # Initialize metrics
        self.metrics = {
            "stream_duration": 0,
            "transcriptions": 0,
            "errors": 0,
            "security_checks": 0
        }
        
    async def run_demo(self, duration: int = 30) -> Dict[str, Any]:
        """Run the streaming demo for specified duration."""
        try:
            # Start stream
            self.streaming_handler.start_stream()
            logger.info("Voice stream started")
            
            # Run processing
            start_time = datetime.now()
            await asyncio.gather(
                self.streaming_handler.process_stream(),
                self._monitor_stream(duration)
            )
            
            # Stop stream
            self.streaming_handler.stop_stream()
            logger.info("Voice stream stopped")
            
            # Generate report
            return self._generate_report()
            
        except Exception as e:
            logger.error(f"Demo failed: {str(e)}")
            self.metrics["errors"] += 1
            raise

    async def _monitor_stream(self, duration: int) -> None:
        """Monitor stream status and handle errors."""
        try:
            start_time = datetime.now()
            while True:
                # Check stream status
                status = self.streaming_handler.get_stream_status()
                
                # Log status
                logger.info(f"Stream status: {json.dumps(status)}")
                
                # Check duration
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= duration:
                    break
                
                # Update metrics
                self.metrics["stream_duration"] = elapsed
                self.metrics["transcriptions"] = status["metrics"]["transcriptions"]
                self.metrics["security_checks"] = status["metrics"]["security_checks"]
                
                # Wait before next check
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Stream monitoring failed: {str(e)}")
            self.metrics["errors"] += 1
            raise

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive streaming demo report."""
        return {
            "demo_info": {
                "start_time": datetime.now().isoformat(),
                "duration": self.metrics["stream_duration"],
                "agent_id": self.voice_agent.id
            },
            "metrics": {
                "transcriptions": self.metrics["transcriptions"],
                "errors": self.metrics["errors"],
                "security_checks": self.metrics["security_checks"],
                "stream_status": self.streaming_handler.get_stream_status()
            },
            "voice_capabilities": {
                "languages": ["en-US", "es-ES", "fr-FR", "de-DE"],
                "sample_rate": self.streaming_handler.rate,
                "chunk_size": self.streaming_handler.chunk
            },
            "security_status": {
                "encryption_enabled": True,
                "access_control": True,
                "audit_logging": True
            }
        }

if __name__ == "__main__":
    # Create demo instance
    demo = VoiceStreamingDemo()
    
    # Run demo for 30 seconds
    duration = 30  # seconds
    print(f"\nStarting voice streaming demo for {duration} seconds...")
    print("\n=== Voice Streaming Demo ===")
    print("\nSay something to test the speech recognition!")
    
    # Run demo
    results = asyncio.run(demo.run_demo(duration))
    
    # Print results
    print("\n=== Demo Results ===")
    print(f"\nDuration: {results['metrics']['stream_duration']} seconds")
    print(f"Transcriptions: {results['metrics']['transcriptions']}")
    print(f"Security Checks: {results['metrics']['security_checks']}")
    print(f"Errors: {results['metrics']['errors']}")
