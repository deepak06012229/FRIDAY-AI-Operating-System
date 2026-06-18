import webbrowser
from utils import logger
import config

def open_url(url_or_name):
    """
    Opens a URL in the user's default browser.
    Maps registered web terms (e.g. 'youtube' -> 'https://www.youtube.com').
    """
    key = url_or_name.lower().strip()
    target_url = url_or_name

    if key in config.WEB_REGISTRY:
        target_url = config.WEB_REGISTRY[key]
        logger.info(f"BrowserController: Resolved '{url_or_name}' to registered URL '{target_url}'")

    # Add standard prefix if it looks like a clean domain name
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        if "." in target_url:
            target_url = "https://" + target_url
        else:
            target_url = f"https://www.google.com/search?q={target_url}"

    try:
        logger.info(f"BrowserController: Launching browser for '{target_url}'")
        webbrowser.open(target_url)
        return True, f"Navigating to {target_url}"
    except Exception as e:
        logger.error(f"BrowserController: Failed to open browser: {e}")
        return False, f"Failed to navigate: {e}"
