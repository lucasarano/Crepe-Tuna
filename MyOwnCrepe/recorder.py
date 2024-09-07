import pyaudio
import wave
import threading
import librosa
import numpy as np
from testingPlayground import analyze_and_plot_audio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
FRAMES_PER_BUFFER = 1024


class AudioRecorder:
    def __init__(self, output_filename="recorded.wav", output_filename_reduced="recorded_reduced.wav"):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.output_filename = output_filename
        self.output_filename_reduced = output_filename_reduced
        self.lock = threading.Lock()

    def start_recording(self):
        try:
            self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                          rate=RATE, input=True,
                                          frames_per_buffer=FRAMES_PER_BUFFER)
            self.frames = []
            self.recording = True
            print("Recording...")
            self.record_thread = threading.Thread(target=self.record)
            self.record_thread.start()
        except Exception as e:
            print(f"Failed to start recording: {e}")

    def record(self):
        try:
            while self.recording:
                data = self.stream.read(FRAMES_PER_BUFFER, exception_on_overflow=False)
                with self.lock:
                    self.frames.append(data)
        except Exception as e:
            print(f"Error during recording: {e}")

    def stop_recording(self):
        try:
            self.recording = False
            self.record_thread.join()
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            with self.lock:
                # Save original recording
                waveFile = wave.open(self.output_filename, 'wb')
                waveFile.setnchannels(CHANNELS)
                waveFile.setsampwidth(self.audio.get_sample_size(FORMAT))
                waveFile.setframerate(RATE)
                waveFile.writeframes(b''.join(self.frames))
                waveFile.close()

                # Load original recording for noise reduction
                audio, sr = librosa.load(self.output_filename, sr=None)
                audio_reduced = librosa.effects.preemphasis(audio)

                # Save noise-reduced recording
                waveFileReduced = wave.open(self.output_filename_reduced, 'wb')
                waveFileReduced.setnchannels(CHANNELS)
                waveFileReduced.setsampwidth(self.audio.get_sample_size(FORMAT))
                waveFileReduced.setframerate(sr)
                waveFileReduced.writeframes(np.int16(audio_reduced * 32767).tobytes())
                waveFileReduced.close()

            print("Finished recording.")
        except Exception as e:
            print(f"Failed to stop recording: {e}")


def record(output_filename):
    recorder = AudioRecorder(output_filename, output_filename+"_reduced.wav")

    def start_recording_thread():
        try:
            recorder.start_recording()
        except Exception as e:
            print(f"Failed to start recording thread: {e}")

    def stop_recording_thread():
        try:
            recorder.stop_recording()
        except Exception as e:
            print(f"Failed to stop recording thread: {e}")

    print("Press ENTER to start recording.")
    input()
    recording_thread = threading.Thread(target=start_recording_thread)
    recording_thread.start()

    print("Recording... Press ENTER to stop recording.")
    input()
    stop_recording_thread()
    recording_thread.join()

    print("Recording process has completed.")


if __name__ == "__main__":
    filename = f"../audio/{input('Enter name of audio file: ')}.wav"
    record(filename)
    analyze_and_plot_audio(filename)
