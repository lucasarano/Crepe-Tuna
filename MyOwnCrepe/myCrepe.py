import crepe
from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button

def plot_pitch_and_notes(t, f, c, notes, ax1, ax2):
    ax1.clear()
    ax2.clear()
    scatter = ax1.scatter(t, f, c=c, cmap='viridis', vmin=0.8, vmax=1.0)
    midi_min, midi_max = int(min(f)), int(max(f)) + 1
    midi_lines = range(midi_min, midi_max + 1)
    ax1.hlines(midi_lines, min(t), max(t), colors='gray', alpha=0.3, linestyles='dashed')
    midi_labels = [f"{midi}" for midi in midi_lines[::2]]
    ax1.set_yticks(midi_lines[::2])
    ax1.set_yticklabels(midi_labels)
    ax1.set_title('Pitch Data Points with Confidence (≥ 0.8)')
    ax1.set_ylabel('MIDI Note')
    
    ax2.scatter(t, f, c=c, cmap='viridis', vmin=0.8, vmax=1.0, alpha=0.5)
    for note in notes:
        ax2.plot([note['start_time'], note['end_time']], [note['midi'], note['midi']], linewidth=2, color='red', alpha=0.7)
    ax2.hlines(midi_lines, min(t), max(t), colors='gray', alpha=0.3, linestyles='dashed')
    ax2.set_yticks(midi_lines[::2])
    ax2.set_yticklabels(midi_labels)
    ax2.set_title('Identified Notes')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('MIDI Note')

def linearize(freq):
    if freq <= 0:
        return None
    midi_note = 69 + 12 * np.log2(freq / 440.0)
    return midi_note

def filter_data(t, f, c, threshold):
    return [(t[i], f[i], c[i]) for i in range(len(t)) if c[i] >= threshold]

def add_point(note, t, f, c, dt, df, time_th, ext_time_th, pitch_th, max_slope):
    if dt > time_th:
        if abs(df) <= pitch_th and dt <= ext_time_th:
            note.append((t, f, c))
            return note, True
    elif abs(df / dt) <= max_slope:
        note.append((t, f, c))
        return note, True
    return note, False

def finalize(note, notes, min_points):
    if len(note) >= min_points:
        notes.append(note)
    return notes, []

def process_notes(notes):
    processed = []
    for note in notes:
        midi_vals = np.array([point[1] for point in note])
        confidences = np.array([point[2] for point in note])
        weighted_log = np.sum(np.log(midi_vals) * confidences) / np.sum(confidences)
        weighted_mean_midi = np.exp(weighted_log)
        start = note[0][0]
        end = note[-1][0]
        avg_conf = np.mean(confidences)
        processed.append({
            'midi': weighted_mean_midi,
            'start_time': start,
            'end_time': end,
            'confidence': avg_conf
        })
    return processed

def detect_notes(t, f, c, max_slope=5, min_points=4, time_th=0.05, ext_time_th=0.08, pitch_th=1.0, conf_th=0.8):
    notes = []
    note = []
    for i in range(len(t)):
        if c[i] < conf_th:
            continue
        if not note:
            note.append((t[i], f[i], c[i]))
        else:
            dt = t[i] - note[-1][0]
            df = f[i] - note[-1][1]
            note, added = add_point(note, t[i], f[i], c[i], dt, df, time_th, ext_time_th, pitch_th, max_slope)
            if not added:
                notes, note = finalize(note, notes, min_points)
                note.append((t[i], f[i], c[i]))
    notes, _ = finalize(note, notes, min_points)
    return process_notes(notes)

def main():
    sr, audio = wavfile.read('voice_recording.wav')
    time, freq, conf, activation = crepe.predict(audio, sr, viterbi=True, model_capacity='full')
    data = filter_data(time, freq, conf, threshold=0.8)
    t = [d[0] for d in data]
    f = [linearize(d[1]) for d in data]
    c = [d[2] for d in data]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))
    plt.subplots_adjust(left=0.1, bottom=0.35)

    initial_notes = detect_notes(t, f, c, time_th=0.05, ext_time_th=0.1, pitch_th=4.0)
    plot_pitch_and_notes(t, f, c, initial_notes, ax1, ax2)

    # Create sliders
    ax_time_th = plt.axes([0.1, 0.2, 0.65, 0.03])
    ax_ext_time_th = plt.axes([0.1, 0.15, 0.65, 0.03])
    ax_pitch_th = plt.axes([0.1, 0.1, 0.65, 0.03])
    ax_max_slope = plt.axes([0.1, 0.05, 0.65, 0.03])

    s_time_th = Slider(ax_time_th, 'Time Threshold', 0.01, 0.2, valinit=0.05)
    s_ext_time_th = Slider(ax_ext_time_th, 'Extended Time Threshold', 0.05, 0.3, valinit=0.1)
    s_pitch_th = Slider(ax_pitch_th, 'Pitch Threshold', 0.5, 10.0, valinit=4.0)
    s_max_slope = Slider(ax_max_slope, 'Max Slope', 1, 20, valinit=5)

    def update(val):
        time_th = s_time_th.val
        ext_time_th = s_ext_time_th.val
        pitch_th = s_pitch_th.val
        max_slope = s_max_slope.val
        notes = detect_notes(t, f, c, time_th=time_th, ext_time_th=ext_time_th, pitch_th=pitch_th, max_slope=max_slope)
        plot_pitch_and_notes(t, f, c, notes, ax1, ax2)
        fig.canvas.draw_idle()

    s_time_th.on_changed(update)
    s_ext_time_th.on_changed(update)
    s_pitch_th.on_changed(update)
    s_max_slope.on_changed(update)

    plt.show()

if __name__ == '__main__':
    main()