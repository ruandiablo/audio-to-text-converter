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

---

### Prerequisites

You will need [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed, as we will use it to manage FFmpeg and Python.

---

### Step 1: Install FFmpeg
FFmpeg is essential for audio processing. Open your terminal (**Anaconda Prompt** or **CMD**) and run:
```
conda install -c conda-forge ffmpeg -y
```
Wait for the installation to complete.

### Step 2: Install Python Dependencies
In the same terminal, install the Whisper AI library:
```
pip install openai-whisper
```
Note: If you have an NVIDIA GPU with CUDA support, Whisper will automatically use it for faster transcription. No extra configuration needed.

### Step 3: Prepare the Files
1. Download the source code or clone this repository
2. Make sure you have these files in the same folder (e.g., your Desktop):

📁 Your folder
├── mt.py              ← main program
├── INSTALAR.bat       ← automatic installer (run once)
└── CRIAR_EXE.bat      ← optional: generates standalone .exe

Tip: If creating mt.py manually in Notepad, change "Save as type" from Text Documents (*.txt) to All Files (*.*) to ensure the .py extension is saved correctly.

### Step 4: Run the Program
You have two options:

Option A: One-Click Setup (Recommended)
Double-click INSTALAR.bat
Wait for it to install dependencies and configure everything
A shortcut called "Audio to Text" will appear on your Desktop
Double-click the shortcut whenever you want to use the program

The installer automatically detects Anaconda/Miniconda, installs dependencies, creates a launcher, and places a desktop shortcut. You only need to run it once.

Option B: Manual Run via Terminal
Open your terminal (Anaconda Prompt or CMD) and run:
```
cd /d %USERPROFILE%\Desktop
python mt.py
```

Optional: Create Standalone Executable
If you want a .exe that doesn't require Python installed:
Double-click CRIAR_EXE.bat
Wait 10–30 minutes for the build process
The executable will be placed in a folder on your Desktop

Warning: The generated executable will be 2–5 GB in size because it bundles Python, PyTorch, and the Whisper library.

### 🌐 Language Support
The application interface supports Portuguese (BR) and English (US). Click the flag icons in the top-right corner to switch languages.
Whisper supports transcription in 10+ languages: Portuguese, English, Spanish, French, Italian, German, Japanese, Korean, Chinese, Russian, and Auto-detect.

### 🎯 Quick Reference

Action /	How
Open audio file /	Click the drop zone or press Ctrl+O
Start transcription /	Click one of the 5 model buttons (TINY → LARGE)
Copy result /	Click Copy or press Ctrl+C after selecting text
Save as TXT /	Click Save TXT or press Ctrl+S
Save as SRT /	Click Save SRT (subtitles with timestamps)
Change UI language /	Click 🇧🇷 or 🇺🇸 flag icons
Adjust font size /	Click A+ / A- buttons

Tip: Start with SMALL for a good balance. Use LARGE only when you need maximum precision and have a GPU.

### ⚠️ Troubleshooting
Problem /	Solution
whisper not found /	Run pip install openai-whisper
FFmpeg not found /	Run conda install -c conda-forge ffmpeg -y
Download stalls on MEDIUM/LARGE /	The app retries automatically up to 3 times. Check your internet connection
Program doesn't open via shortcut /	Run INSTALAR.bat again to recreate the launcher
No GPU detected /	Install CUDA Toolkit and pip install torch with CUDA support

This project is Open Source. Feel free to contribute!

# Ruan Almeida - @ruanalmeidar
