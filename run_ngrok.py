from pyngrok import ngrok
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_ngrok():
    try:
        # Start ngrok on port 8000
        public_url = ngrok.connect(8000)
        logger.info(f"Ngrok tunnel established at: {public_url}")
        logger.info("Copy this URL and update your WEBHOOK_URL in .env file")
        
        # Keep the tunnel open
        ngrok_process = ngrok.get_ngrok_process()
        try:
            # Block until CTRL-C or some other terminating event
            ngrok_process.proc.wait()
        except KeyboardInterrupt:
            logger.info("Shutting down ngrok tunnel...")
    except Exception as e:
        logger.error(f"Error starting ngrok: {e}")
        raise

if __name__ == "__main__":
    start_ngrok()