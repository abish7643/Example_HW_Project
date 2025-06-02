import requests
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)


def main():
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    print("Hello World")
    print(requests.get("http://google.com").status_code)

if __name__ == "__main__":
    main()
