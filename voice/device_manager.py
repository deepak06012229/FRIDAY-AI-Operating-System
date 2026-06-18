import sounddevice as sd
import numpy as np
from utils import logger
import config

def get_input_devices():
    """Returns a list of dictionaries detailing available input devices."""
    devices = []
    try:
        device_list = sd.query_devices()
        for idx, dev in enumerate(device_list):
            if dev['max_input_channels'] > 0:
                devices.append({
                    "id": idx,
                    "name": dev['name'],
                    "channels": dev['max_input_channels'],
                    "sample_rate": int(dev['default_samplerate']),
                    "is_default": idx == sd.default.device[0] if sd.default.device[0] is not None else False
                })
    except Exception as e:
        logger.error(f"Error querying audio input devices: {e}")
    return devices

def get_default_input_device():
    """Finds the system's default input audio device."""
    try:
        default_idx = sd.default.device[0]
        if default_idx is None or default_idx < 0:
            # Fallback to query
            devices = get_input_devices()
            for dev in devices:
                if dev["is_default"]:
                    return dev
            if devices:
                return devices[0]
            return None
        dev_info = sd.query_devices(default_idx)
        return {
            "id": default_idx,
            "name": dev_info['name'],
            "channels": dev_info['max_input_channels'],
            "sample_rate": int(dev_info['default_samplerate'])
        }
    except Exception as e:
        logger.error(f"Error finding default input device: {e}")
        return None

def test_microphone_quality(device_id, duration=3.0, sample_rate=16000):
    """Records a brief sample, measuring average, peak amplitude, and estimated SNR."""
    try:
        logger.info(f"Starting microphone quality diagnostic test on device {device_id}...")
        sd.default.device = (device_id, None)
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        
        # Calculate stats
        peak = np.max(np.abs(recording))
        mean_energy = np.mean(np.abs(recording))
        
        # Estimate background noise (assume lowest 10% energy frames)
        frame_size = int(0.1 * sample_rate)  # 100ms frames
        frames = [np.mean(np.abs(recording[i:i+frame_size])) for i in range(0, len(recording), frame_size) if len(recording[i:i+frame_size]) == frame_size]
        
        if frames:
            noise_floor = sorted(frames)[0]
            snr_db = 20 * np.log10(peak / (noise_floor + 1e-5)) if peak > 0 else 0
        else:
            noise_floor = 0
            snr_db = 0

        status = "EXCELLENT" if snr_db > 30 else ("GOOD" if snr_db > 15 else "POOR/NOISY")

        return {
            "peak_amplitude": float(peak),
            "average_energy": float(mean_energy),
            "estimated_noise_floor": float(noise_floor),
            "snr_db": round(float(snr_db), 2),
            "quality_status": status,
            "success": True
        }
    except Exception as e:
        logger.error(f"Diagnostics failed on device {device_id}: {e}")
        return {
            "success": False,
            "error_msg": str(e)
        }


def get_output_devices():
    """Returns a list of dictionaries for available output devices."""
    devices = []
    try:
        device_list = sd.query_devices()
        for idx, dev in enumerate(device_list):
            if dev['max_output_channels'] > 0:
                devices.append({
                    "id": idx,
                    "name": dev['name'],
                    "channels": dev['max_output_channels'],
                    "sample_rate": int(dev['default_samplerate']),
                    "is_default": idx == sd.default.device[1] if sd.default.device[1] is not None else False
                })
    except Exception as e:
        logger.error(f"Error querying audio output devices: {e}")
    return devices

def get_default_output_device():
    """Finds the system's default output audio device."""
    try:
        default_idx = sd.default.device[1]
        if default_idx is None or default_idx < 0:
            devices = get_output_devices()
            for dev in devices:
                if dev["is_default"]:
                    return dev
            if devices:
                return devices[0]
            return None
        dev_info = sd.query_devices(default_idx)
        return {
            "id": default_idx,
            "name": dev_info['name'],
            "channels": dev_info['max_output_channels'],
            "sample_rate": int(dev_info['default_samplerate'])
        }
    except Exception as e:
        logger.error(f"Error finding default output device: {e}")
        return None
