import os
from midiutil import MIDIFile
import matplotlib.pyplot as plt
import crepe
from scipy.io import wavfile
import math
import numpy as np
import warnings


def frequency_to_note(freq):
    A4 = 440.0
    C0 = A4 * pow(2, -4.75)
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    h = round(12 * np.log2(freq / C0))
    octave = h // 12
    n = h % 12
    return note_names[n] + str(octave)


def plot_detected_notes(weighted_averages):
    # Extract note names, start times, and durations
    note_names = [note["name"] for note in weighted_averages]
    start_times = [note["startTime"] for note in weighted_averages]
    durations = [note["duration"] for note in weighted_averages]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.barh(note_names, durations, left=start_times, align='center', edgecolor='black')

    # Add labels and title
    plt.xlabel("Time (s)")
    plt.ylabel("Notes")
    plt.title("Detected Notes Over Time")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()

    # Show the plot
    plt.show()


def analyze_audio_old(file_path):
    # Load the file file
    sr, file = wavfile.read(file_path)

    # Predict the pitch
    time, frequency, confidence, activation = crepe.predict(file, sr, viterbi=True, model_capacity='large')

    # Create an array of tuples and filter by confidence
    data = [(t, f, c) for t, f, c in zip(time, frequency, confidence) if c > 0.82]

    # Extract the filtered values
    filtered_time = [d[0] for d in data]
    filtered_frequency = [d[1] for d in data]
    filtered_confidence = [d[2] for d in data]

    # Group frequencies into notes
    notes = []
    current_note = []
    prev_f = None
    prev_t = None
    note_diff = None

    for i in range(len(filtered_time)):
        if i != 0:
            note_diff = abs((filtered_frequency[i] - prev_f) / (filtered_time[i] - prev_t))
        if not current_note:
            current_note.append((filtered_time[i], filtered_frequency[i], filtered_confidence[i]))
        else:
            time_diff = filtered_time[i] - current_note[-1][0]
            if time_diff <= 0.1 and note_diff is not None and note_diff < 180:
                current_note.append((filtered_time[i], filtered_frequency[i], filtered_confidence[i]))
            else:
                notes.append(current_note)
                current_note = [(filtered_time[i], filtered_frequency[i], filtered_confidence[i])]
        prev_t = filtered_time[i]
        prev_f = filtered_frequency[i]

    if current_note:
        notes.append(current_note)

    long_notes = []
    for note_array in notes:
        time_last, freq_last, conf_last = note_array[-1]
        time_first, freq_first, conf_first = note_array[0]
        if (time_last - time_first) > 0.05:
            long_notes.append(note_array)

    notes = long_notes

    # Calculate weighted average of frequencies for each note and match with initial and ending time
    weighted_averages = []
    for note in notes:
        times, freqs, confs = zip(*note)
        weighted_avg_freq = np.average(freqs, weights=confs)
        start_time = times[0]
        end_time = times[-1]
        duration = end_time - start_time
        musical_note = frequency_to_note(weighted_avg_freq)
        weighted_averages.append({
            "name": musical_note,
            "duration": duration,
            "frequency": weighted_avg_freq,
            "startTime": start_time
        })

    return weighted_averages


def export_to_midi(notes, output_file="output.mid", tempo=120):
    """
    Convert the analyzed notes to MIDI format

    Args:
        notes: List of dictionaries containing note information (from analyze_audio)
        output_file: Path to save the MIDI file
        tempo: Tempo in BPM (default 120)
    """
    # Create MIDI file with 1 track
    midi = MIDIFile(1)
    track = 0
    time = 0
    channel = 0
    volume = 100  # 0-127

    # Set tempo
    midi.addTempo(track, time, tempo)

    # Helper function to convert frequency to MIDI note number
    def freq_to_midi_note(freq):
        # A4 = 69, 440Hz
        if freq <= 0: return 0
        return int(round(69 + 12 * math.log2(freq / 440.0)))

    # Add notes to the MIDI file
    for note in notes:
        freq = note["frequency"]
        start_time = note["startTime"]
        duration = note["duration"]

        # Convert frequency to MIDI note number
        midi_note = freq_to_midi_note(freq)

        # Convert time to beats (assuming 120 BPM)
        midi_time = start_time * (tempo / 60.0)
        midi_duration = duration * (tempo / 60.0)

        # Add note to MIDI file
        midi.addNote(track, channel, midi_note, midi_time, midi_duration, volume)

    # Save the MIDI file
    with open(output_file, "wb") as f:
        midi.writeFile(f)
