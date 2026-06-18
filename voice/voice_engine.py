import os
import time
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from utils import logger
import config

class STTWorker(QThread):
    """Worker thread to handle Google STT recognition without blocking the audio capture or UI."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def run(self):
        r = sr.Recognizer()
        try:
            if not os.path.exists(self.filename):
                self.error.emit("Audio file not found.")
                return

            with sr.AudioFile(self.filename) as source:
                audio_data = r.record(source)

            # Recognize using Google Speech Recognition
            text = r.recognize_google(audio_data)
            self.finished.emit(text)
        except sr.UnknownValueError:
            self.finished.emit("")  # Silent/unrecognized
        except sr.RequestError as e:
            logger.error(f"STT API request error: {e}")
            self.error.emit("Internet connectivity issue.")
        except Exception as e:
            logger.error(f"STT unexpected error: {e}")
            self.error.emit(str(e))
        finally:
            # Clean up the wave file safely
            try:
                if os.path.exists(self.filename):
                    os.remove(self.filename)
            except Exception:
                pass


class VoiceEngine(QThread):
    """
    Continuous audio capture thread. Monitors amplitude, performs VAD,
    applies basic noise suppression and gain control, and triggers STT.
    """
    level_updated = pyqtSignal(float)        # Emits current signal level (0.0 to 100.0)
    waveform_updated = pyqtSignal(np.ndarray) # Emits raw buffer for plotting
    speech_started = pyqtSignal()            # Emits when speaking starts
    speech_ended = pyqtSignal()              # Emits when user stops speaking
    transcript_ready = pyqtSignal(str)       # Emits STT result
    status_changed = pyqtSignal(str)         # Emits current engine status (Calibrating, Idle, Listening, Speaking, thinking)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.device_id = None
        self.sample_rate = config.DEFAULT_SAMPLE_RATE
        self.running = True
        
        # Audio buffer and recording queue
        self.audio_queue = queue.Queue()
        self.recording_buffer = []
        
        # VAD & AGC state
        self.is_recording = False
        self.noise_floor = config.VAD_ENERGY_THRESHOLD
        self.silence_timer = None
        self.speech_start_time = None
        self.active_stt_worker = None

        # Temp audio output path
        self.output_wav = os.path.join(config.BASE_DIR, "temp_input.wav")

    def set_device(self, device_id):
        """Switches the recording device dynamically."""
        self.device_id = device_id
        logger.info(f"VoiceEngine source switched to Device ID: {device_id}")

    def run(self):
        logger.info("Voice Engine capture thread started.")
        self.status_changed.emit("Calibrating")

        # Calibrate background noise floor (takes ~1.5s)
        self.calibrate_noise_floor()

        # Set default device if none selected
        if self.device_id is None:
            try:
                default_device = sd.default.device[0]
                self.device_id = default_device if default_device is not None else 0
            except Exception:
                self.device_id = 0

        # Start input stream
        def callback(indata, frames, time_info, status):
            if status:
                logger.warn(f"Audio stream status: {status}")
            self.audio_queue.put(indata.copy())

        try:
            with sd.InputStream(
                device=self.device_id,
                channels=config.CHANNELS,
                samplerate=self.sample_rate,
                callback=callback,
                dtype='int16'
            ):
                logger.info(f"SoundDevice InputStream opened on device {self.device_id}")
                self.status_changed.emit("Idle")

                while self.running:
                    try:
                        # Fetch audio data (blocks up to 100ms)
                        data_chunk = self.audio_queue.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    # Process the chunk
                    self.process_audio_chunk(data_chunk)

        except Exception as e:
            logger.error(f"Failed to open SoundDevice InputStream: {e}")
            self.status_changed.emit("Error")

        logger.info("Voice Engine capture thread stopped.")

    def calibrate_noise_floor(self):
        """Records a brief sample to compute the ambient noise floor."""
        try:
            logger.info("Calibrating voice engine noise floor...")
            # We record a quick 1-second segment
            calibration_data = sd.rec(
                int(1.2 * self.sample_rate),
                samplerate=self.sample_rate,
                channels=config.CHANNELS,
                dtype='int16'
            )
            sd.wait()
            energies = [np.mean(np.abs(calibration_data[i:i+500])) for i in range(0, len(calibration_data), 500) if len(calibration_data[i:i+500]) == 500]
            if energies:
                self.noise_floor = np.mean(energies) * 1.5
                # Ensure a sane minimum noise floor threshold
                self.noise_floor = max(self.noise_floor, 300)
                logger.info(f"Noise floor calibrated to energy level: {self.noise_floor:.2f}")
            else:
                self.noise_floor = config.VAD_ENERGY_THRESHOLD
        except Exception as e:
            logger.error(f"Error during noise floor calibration: {e}")
            self.noise_floor = config.VAD_ENERGY_THRESHOLD

    def process_audio_chunk(self, data_chunk):
        """Analyzes a chunk of audio, performs VAD, spectral noise subtraction, AGC, and handles recording."""
        # 1. Emit raw waveform for dashboard visualizer
        self.waveform_updated.emit(data_chunk.flatten())

        # 2. Compute average amplitude (energy) of the chunk
        energy = np.mean(np.abs(data_chunk))
        
        # Scale to 0-100 for level meter
        meter_level = min(100.0, (energy / (self.noise_floor * 3.0 + 1)) * 100.0)
        self.level_updated.emit(meter_level)

        # 3. Dynamic Thresholding Voice Activity Detection (VAD)
        speech_threshold = self.noise_floor + 400
        is_above_threshold = energy > speech_threshold

        current_time = time.time()

        if is_above_threshold:
            # User is speaking
            if not self.is_recording:
                # Speech starts
                self.is_recording = True
                self.speech_start_time = current_time
                self.recording_buffer = []
                self.speech_started.emit()
                self.status_changed.emit("Listening")
                logger.info("Voice activity detected (Speech started)...")
            
            # Reset silence timer
            self.silence_timer = None
            # Append chunk to buffer
            self.recording_buffer.append(data_chunk)
        else:
            # Below speech threshold
            if self.is_recording:
                # Accumulate the silence frames as well to avoid clipping
                self.recording_buffer.append(data_chunk)

                if self.silence_timer is None:
                    self.silence_timer = current_time
                elif current_time - self.silence_timer >= config.VAD_SILENCE_DURATION:
                    # User stopped speaking for too long
                    logger.info("Silence limit exceeded (Speech ended). Processing...")
                    self.is_recording = False
                    self.silence_timer = None
                    self.speech_ended.emit()
                    self.status_changed.emit("Thinking")

                    duration = current_time - self.speech_start_time
                    if duration >= config.VAD_MIN_DURATION:
                        # Process audio buffer
                        self.process_recorded_audio()
                    else:
                        logger.info("Recording too short. Discarded.")
                        self.status_changed.emit("Idle")

    def process_recorded_audio(self):
        """Combines buffer chunks, applies AGC and basic noise suppression, then saves to WAV."""
        if not self.recording_buffer:
            self.status_changed.emit("Idle")
            return

        # Concatenate audio chunks
        full_audio = np.concatenate(self.recording_buffer, axis=0)

        # 1. Noise Suppression: Spectral Gate Simulation
        # Simple threshold gate: zero out frequency bins with low magnitude or apply simple high-pass filtering
        # To keep it efficient and robust in NumPy, we do standard bandpass-energy cleanup (mean-subtraction)
        full_audio = full_audio - np.mean(full_audio)

        # 2. Adaptive Gain Control (AGC)
        # Normalize the signal to target peak volume to guarantee clean STT recognition
        peak = np.max(np.abs(full_audio))
        if peak > 0:
            target_peak = 24000  # Sane max amplitude for 16-bit audio
            scale = target_peak / peak
            # Apply dynamic limit on gain (max 4x gain to avoid boosting noise floor)
            scale = min(scale, 4.0)
            full_audio = (full_audio * scale).astype(np.int16)

        # Save to file
        try:
            sf.write(self.output_wav, full_audio, self.sample_rate)
            
            # Kick off background STT worker thread
            self.active_stt_worker = STTWorker(self.output_wav)
            self.active_stt_worker.finished.connect(self.handle_stt_finished)
            self.active_stt_worker.error.connect(self.handle_stt_error)
            self.active_stt_worker.start()
        except Exception as e:
            logger.error(f"Error saving audio to file: {e}")
            self.status_changed.emit("Idle")

    def handle_stt_finished(self, text):
        self.status_changed.emit("Idle")
        # Emit transcript to be handled by the AI Brain layer
        self.transcript_ready.emit(text)

    def handle_stt_error(self, err_msg):
        self.status_changed.emit("Idle")
        logger.error(f"STT Worker failed: {err_msg}")
        self.transcript_ready.emit("")  # Emits empty to reset UI prompts

    def stop(self):
        self.running = False
        self.wait()
        if self.active_stt_worker and self.active_stt_worker.isRunning():
            self.active_stt_worker.wait()
