# 🎙️ Audio to Text Converter

<img width="991" height="878" alt="image" src="https://github.com/user-attachments/assets/e9537ae0-58cb-4a8f-aa88-668cbfb9d9a3" />

A simple yet powerful tool with a Graphical User Interface (GUI) to transcribe audio and video files locally using OpenAI Whisper technology.

Developed by **Ruan Almeida** (@ruanalmeidar).

## 🚀 Features

* **Offline:** All processing is done locally on your computer (100% privacy).
* **Various Models:** Support for Tiny, Base, Small, Medium, and Large models (higher accuracy).
* **Output Formats:** Exports transcriptions to Text (.txt) and Subtitles (.srt).
* **Multilingual:** Automatically detects languages or allows manual selection.
* **Timestamps:** Option to include timestamps in the transcription.

---
OBS 1.: The quality of tiny and base models are not good, so, you should use at least "Medium"
OBS 2.: For every "quality" that you choose one download of the model will be made in the first time that you use that quality, lowest (tiny) quality will download less mb, large model (quality) will download more mb.
OBS 3.: Some transcriptions will not be perfect (quality of audio source, many people talking, music in the background, etc.)

## 🛠️ Installation and Usage

Follow the steps below to run the project on your machine.

### Prerequisites

You will need [Anaconda](https://www.anaconda.com/) or Miniconda installed, as we will use it to manage FFmpeg.

### Step 1: Install FFmpeg
FFmpeg is essential for audio processing. Open your terminal (Anaconda Prompt or CMD) and run:

```bash
conda install -c conda-forge ffmpeg -y
```

(Wait for the installation to complete).

Step 2: Install Python Dependencies
To run the code, you need to install the GUI and AI libraries. In the same terminal, run:

```bash
pip install openai-whisper customtkinter
```

Step 3: Prepare the File
Create a folder on your Desktop to organize the files.

Download the source code or create a new text file.

Paste the project code.

Save the file with the exact name: mt.py

Important: When saving in Notepad, change "Save as type" from "Text Documents (.txt)" to "All Files (.)" to ensure the .py extension is accepted.

Step 4: Run the Program
```base
Now, let's run the application.
```

In your terminal, navigate to your Desktop:
```bash
cd /d %USERPROFILE%\Desktop
```

Execute the script:
```base
python mt.py
```

Done! The interface should open, and you can now select your audio files for transcription.

This project is Open Source. Feel free to contribute.

# Ruan Almeida - @ruanalmeidar
