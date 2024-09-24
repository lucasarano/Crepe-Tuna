# Crepe-Tuna

Crepe-Tuna is a Python-based tool for analyzing monophonic audio recordings and extracting musical notes. It uses CREPE (Convolutional Representation for Pitch Estimation) for pitch detection and implements a custom algorithm for note segmentation. The project features an interactive visualization tool that allows users to fine-tune note detection parameters in real-time.

## Features

- Convert WAV audio files containing monophonic audio (e.g., voice recordings) to musical notes
- Utilize CREPE for high-accuracy pitch detection
- Implement a custom note segmentation algorithm with adjustable parameters
- Provide an interactive matplotlib-based GUI for visualizing pitch data and detected notes
- Allow real-time parameter adjustment for optimal note detection

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/crepe-tuna.git
   cd crepe-tuna
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Prepare your WAV file containing the monophonic audio input.

2. Run the main script:
   ```
   python crepe_tuna.py
   ```

3. Use the interactive GUI to adjust parameters and visualize the results.

## How It Works

1. **Audio Input**: The system reads a WAV file.
2. **Pitch Detection**: CREPE analyzes the audio and estimates the pitch at each time frame.
3. **Note Segmentation**: A custom algorithm processes the pitch data to identify discrete notes.
4. **Visualization**: The pitch data and detected notes are displayed in an interactive plot.
5. **Parameter Tuning**: Users can adjust various parameters to optimize note detection in real-time.

## Dependencies

- CREPE (Convolutional Representation for Pitch Estimation)
- NumPy
- SciPy
- Matplotlib
- Librosa (Audio Analysis)

## Contributing

We welcome contributions to Crepe-Tuna! Please feel free to submit pull requests or open issues on our GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The CREPE team for their excellent pitch detection model
- All contributors and users of Crepe-Tuna
