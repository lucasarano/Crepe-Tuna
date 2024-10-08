import argparse
import os
import sys
from tabulate import tabulate
from pprint import pprint
from model import analyze_and_plot_audio
"""
CLI tool to analyze audio, simplifies testing without a server.
To run this tool, run the following command:
    python plato.py wavfilename.wav
Use recorder.py to record a wav audio file.
"""


def main():
    """
    parser = argparse.ArgumentParser(description="Analyze an audio file.")
    parser.add_argument("audio_file", nargs="?", help="The audio file to analyze (should be a .wav file)")
    args = parser.parse_args()

    audio_file = args.audio_file

    if not audio_file:
        audio_file = input("Please enter the name of the audio file to analyze: ")

    # Check if the file exists
    if not os.path.exists(audio_file):
        print(f"Error: The file '{audio_file}' does not exist.")
        sys.exit(1)

    # Check if the file has a .wav extension, add it if necessary
    if not audio_file.lower().endswith('.wav'):
        audio_file += '.wav'
        if not os.path.exists(audio_file):
            print(f"Error: The file '{audio_file}' does not exist.")
            sys.exit(1)
"""
    try:
        print("Analyzing audio...")
        file_path = os.path.join('./', "audio.wav")
        #result = analyze_audio_dos(file_path)

    except Exception as e:
        print(f"An error occurred while analyzing the file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
