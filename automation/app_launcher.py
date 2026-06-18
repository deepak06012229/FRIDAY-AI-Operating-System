import os
import subprocess
from utils import logger
import config

def resolve_path(path):
    """Replaces common user directory placeholders with active environment variables."""
    if not path:
        return ""
    
    # Resolve %USERPROFILE% or hardcoded 'Deepak' to support different target profiles dynamically
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Deepak")
    
    if "C:\\Users\\Deepak" in path:
        path = path.replace("C:\\Users\\Deepak", user_profile)
        
    return os.path.expandvars(path)

def launch_application(name):
    """
    Launches a Windows application by name, mapping it using APP_REGISTRY
    or attempting direct shell executions for standard commands.
    """
    app_key = name.lower().strip()
    
    logger.info(f"AppLauncher: Attempting to launch application: '{name}'")
    
    # 1. Lookup in registry
    if app_key in config.APP_REGISTRY:
        exec_path = resolve_path(config.APP_REGISTRY[app_key])
        if os.path.exists(exec_path):
            try:
                os.startfile(exec_path)
                logger.info(f"AppLauncher: Successfully started registered app '{name}' at {exec_path}")
                return True, f"Opened {name}."
            except Exception as e:
                logger.error(f"AppLauncher: Failed to open registered app {name}: {e}")
                return False, f"Error launching {name}: {e}"
        else:
            logger.warn(f"AppLauncher: Registered path for '{name}' does not exist: {exec_path}")
            
    # 2. Try common system executables directly via shell (fallback)
    try:
        # Check standard PATH command
        subprocess.Popen(app_key, shell=True)
        logger.info(f"AppLauncher: Started '{name}' via shell command.")
        return True, f"Triggered execution for {name}."
    except Exception as e:
        logger.error(f"AppLauncher: Shell launch failed for '{name}': {e}")
        
    return False, f"Could not locate or launch application '{name}'."
