# SyncMaster - AI Audio-Text Synchronization Platform

## Overview

SyncMaster is an intelligent web application that transforms audio files into synchronized multimedia content. The platform uses AI to automatically transcribe audio, extract word-level timestamps, and generate both mobile-compatible MP3 files with embedded synchronized lyrics and animated MP4 videos. Built with Streamlit for rapid prototyping and user-friendly interface, the application follows a three-step wizard approach: upload & process, review & customize, and export.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application
- **Design Pattern**: Multi-step wizard interface with session state management
- **User Flow**: Three-step process (Upload → Customize → Export)
- **State Management**: Streamlit session state for maintaining user progress and data across steps

### Backend Architecture
- **Language**: Python-based modular architecture
- **Processing Pipeline**: Sequential audio processing with AI transcription and synchronization
- **Component-Based Design**: Separate modules for audio processing, video generation, and MP3 embedding
- **File Handling**: Temporary file management for processing and output generation

## Key Components

### 1. Audio Processor (`audio_processor.py`)
- **Purpose**: Handles audio transcription and word-level timestamp extraction
- **Technology**: OpenAI Whisper model (base variant)
- **Key Features**:
  - Automatic speech-to-text conversion
  - Word-level timestamp precision
  - Support for multiple audio formats
- **Architecture Decision**: Uses Whisper's built-in word-level timing capabilities, eliminating the need for separate alignment algorithms

### 2. Video Generator (`video_generator.py`)
- **Purpose**: Creates synchronized MP4 videos with animated text
- **Technology**: MoviePy for video processing and PIL for text rendering
- **Animation Styles**: 
  - Karaoke Style (word-by-word highlighting)
  - Pop-up Word effects
  - Line-by-line reveals
- **Output**: HD quality videos (1280x720) with customizable styling

### 3. MP3 Embedder (`mp3_embedder.py`)
- **Purpose**: Embeds SYLT synchronized lyrics into MP3 files
- **Technology**: Mutagen library for audio metadata manipulation
- **Key Features**:
  - SYLT frame creation with UTF-16 encoding
  - Mobile device compatibility
  - Preservation of existing metadata
- **Architecture Decision**: Uses SYLT format specifically for mobile player compatibility

### 4. Main Application (`app.py`)
- **Purpose**: Orchestrates the entire user workflow
- **Features**:
  - Multi-step wizard interface
  - Progress tracking
  - Session state management
  - File upload handling
- **User Experience**: Clean, intuitive interface with real-time feedback

### 5. Utilities (`utils.py`)
- **Purpose**: Common functionality and validation
- **Functions**:
  - Audio file validation
  - Timestamp formatting
  - File type checking
- **Technology**: Librosa for audio file validation

## Data Flow

1. **Audio Input**: User uploads audio file (MP3, WAV, M4A, FLAC, OGG)
2. **AI Processing**: Whisper model transcribes audio and extracts word timestamps
3. **User Customization**: Text editing and visual style configuration
4. **Dual Output Generation**:
   - MP3 with embedded SYLT lyrics for mobile compatibility
   - MP4 video with synchronized animated text

## External Dependencies

### Core AI Libraries
- **OpenAI Whisper**: Primary transcription and timestamp extraction
- **Librosa**: Audio file validation and processing
- **NumPy**: Numerical operations for audio processing

### Media Processing
- **MoviePy**: Video generation and manipulation
- **Mutagen**: Audio metadata and ID3 tag handling
- **PIL (Pillow)**: Image and text rendering for video frames

### Web Framework
- **Streamlit**: Complete web application framework
- **Tempfile**: Temporary file management for processing

### System Requirements
- **Python 3.7+**: Core runtime environment
- **FFmpeg**: Required by MoviePy for video processing (system dependency)

## Deployment Strategy

### Current Architecture
- **Single Application**: Monolithic Streamlit application
- **Local Processing**: All AI processing happens on the deployment server
- **File Management**: Temporary file system for processing artifacts
- **Session Storage**: In-memory session state management

### Scaling Considerations
- **Resource Intensive**: Whisper model requires significant CPU/memory
- **Processing Time**: Large audio files may require extended processing time
- **Storage**: Temporary files need cleanup mechanisms
- **Concurrent Users**: May require queue management for multiple simultaneous users

### Deployment Requirements
- **Memory**: Minimum 4GB RAM for Whisper model loading
- **Storage**: Adequate temporary storage for audio/video processing
- **Network**: Stable connection for file uploads/downloads
- **System Dependencies**: FFmpeg installation required

## Changelog

```
Changelog:
- June 30, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```