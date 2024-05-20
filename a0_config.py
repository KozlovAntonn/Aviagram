# Bot token can be obtained via https://t.me/BotFather 
# TOKEN = "6653218699:AAG4a1kHzvYire9AB2OkEPFe-pao-lWCmmY"  # SkyPulse_bot token
TOKEN = "6736500032:AAFlT2hpvXNz6ry00Xejl0jBZWZQm2Sznkk"  # Aviagram_bot token

# Aviasales 
AVIASALES_TOKEN = "0078593117e70b6ea9e36d79ddc0b354"


# Webserver settings
WEB_SERVER_HOST = "0.0.0.0" # bind localhost only to prevent any external access
WEB_SERVER_PORT = 5000 # Port for incoming request from reverse proxy. Should be any available port
WEBHOOK_PATH = "/webhook" # Path to webhook route, on which Telegram will send requests
WEBHOOK_SECRET = '' # Secret key to validate requests from Telegram (optional)
BASE_WEBHOOK_URL = "https://aviagram-finder.online"