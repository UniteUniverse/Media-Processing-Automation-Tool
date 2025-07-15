# Media-Processing-Automation-Tool
The Media Processing Automation Tool is a sophisticated Flask-based web application that transforms audio and video files into structured, searchable content through AI-powered analysis. This system combines multiple cutting-edge technologies to provide automated transcription, speaker identification, scene detection, and intelligent summarization.
## Features

- **Audio/Video Processing**: Supports multiple audio and video formats
- **Transcription**: OpenAI Whisper-based speech-to-text conversion
- **Speaker Diarization**: Automatic speaker identification and separation using pyannote.audio
- **Scene Detection**: Automatic scene change detection and keyframe extraction for videos
- **AI Summarization**: GPT-4 powered meeting summaries with action items
- **Duplicate Detection**: Built-in file registry to prevent reprocessing
- **Real-time Progress**: Live updates on processing status
- **Web Interface**: User-friendly dashboard for monitoring and control
- **File Upload**: Manual file upload with drag-and-drop support
- **Folder Monitoring**: Automatic processing of files dropped in watched folders

## Architecture

```
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Dependencies
├── lib/
│   ├── __init__.py
│   ├── folder_monitor.py     # File system monitoring
│   ├── audio_processor.py    # Audio extraction and normalization
│   ├── diarization.py        # Speaker diarization
│   ├── transcription.py      # Speech-to-text
│   ├── scene_detection.py    # Video scene detection
│   ├── summary_generator.py  # AI-powered summarization
│   └── file_registry.py      # Duplicate detection and tracking
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── results.html
```

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher (3.11 recommended)
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Memory**: At least 8GB RAM (16GB recommended for video processing)
- **Storage**: Minimum 10GB free space for processing files
- **Network**: Internet connection for API calls to OpenAI and Hugging Face

### Required Software

#### 1. FFmpeg
FFmpeg is required for audio/video processing.

**Windows:**
1. Download from [FFmpeg official site](https://ffmpeg.org/download.html)
2. Extract to `C:\\ffmpeg`
3. Add `C:\\ffmpeg\\bin` to your system PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### 2. Python Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### API Keys Required

#### 1. OpenAI API Key
- Visit [OpenAI Platform](https://platform.openai.com/)
- Create an account and generate an API key
- Ensure you have credits available for Whisper and GPT-4 usage

#### 2. Hugging Face Token
- Visit [Hugging Face](https://huggingface.co/)
- Create an account and generate an access token
- Accept the terms for:
  - `pyannote/segmentation-3.0`
  - `pyannote/speaker-diarization-3.1`

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd media-processing-automation
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install PyTorch (if not automatically installed)
```bash
# For CPU-only (lighter):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# For CUDA (GPU acceleration):
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 5. Environment Configuration
Create a `.env` file in the project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here

# Processing Settings
LANGUAGE=auto  # or 'en', 'ta', 'hi'
NUM_SPEAKERS=0  # 0 for auto-detection, or specify number

# Directory Paths (optional - defaults will be created)
WATCH_FOLDER=./input
UPLOAD_FOLDER=./uploads
```

### 6. Create Required Directories
```bash
mkdir -p input uploads processed/audio processed/images processed/summaries
```

## Usage

### 1. Start the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### 2. Processing Methods

#### Manual File Upload
1. Navigate to the web interface
2. Use the "Manual Upload" section
3. Select audio or video files
4. Monitor progress in real-time

#### Folder Monitoring
1. Configure the folder path in the web interface
2. Click "Start Monitoring"
3. Drop files into the watched folder
4. Files will be processed automatically

### 3. Supported File Formats

**Audio:**
- MP3, WAV, FLAC, M4A, AAC, OGG, WMA

**Video:**
- MP4, MOV, MKV, AVI, WebM, FLV, WMV

### 4. Output Files
- **Audio**: Processed audio files in `processed/audio/`
- **Transcripts**: JSON files with detailed transcription data
- **Diarization**: RTTM files with speaker timestamps
- **Summaries**: Text files with AI-generated summaries
- **Scene Images**: Keyframes from video scenes in `processed/images/`

## API Endpoints

### Core Endpoints
- `GET /` - Main dashboard
- `POST /api/upload` - File upload
- `POST /api/start` - Start folder monitoring
- `POST /api/stop` - Stop folder monitoring
- `GET /api/status` - Get processing status
- `GET /api/status/<job_id>` - Get specific job status
- `GET /api/results/<item_id>` - Get processing results

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `HUGGINGFACE_TOKEN`: Your Hugging Face access token
- `LANGUAGE`: Transcription language (auto, en, ta, hi)
- `NUM_SPEAKERS`: Number of speakers for diarization (0 for auto)
- `WATCH_FOLDER`: Directory to monitor for new files
- `UPLOAD_FOLDER`: Directory for uploaded files

### Audio Processing Settings
- `AUDIO_SAMPLE_RATE`: 16000 Hz (optimized for speech recognition)
- `AUDIO_CHANNELS`: 1 (mono audio for better processing)

## Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found
```bash
# Verify FFmpeg installation
ffmpeg -version

# If not found, ensure it's in your PATH
which ffmpeg  # macOS/Linux
where ffmpeg  # Windows
```

#### 2. CUDA/GPU Issues
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# For CPU-only installation
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 3. Permission Errors
```bash
# Ensure proper permissions for directories
chmod 755 input uploads processed
```

#### 4. API Rate Limits
- Monitor your OpenAI API usage
- Implement delays between requests if needed
- Consider using smaller models for development

### Performance Optimization

#### 1. GPU Acceleration
- Install CUDA-enabled PyTorch for faster processing
- Ensure sufficient GPU memory (8GB+ recommended)

#### 2. Memory Management
- Process files sequentially for large files
- Monitor system memory usage
- Consider cloud deployment for heavy workloads

#### 3. Storage Optimization
- Regularly clean processed files
- Use compression for archived results
- Monitor disk space usage

## Development

### Running in Development Mode
```bash
# Set Flask environment
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows

# Run with debug mode
python app.py
```

### Testing
```bash
# Test with sample files
python -c "from lib.audio_processor import AudioProcessor; print('Audio processor working')"
python -c "from lib.transcription import TranscriptionService; print('Transcription service working')"
```

### Code Structure
- `app.py`: Main Flask application and routing
- `config.py`: Configuration management
- `lib/`: Core processing modules
- `static/`: Web assets (CSS, JavaScript)
- `templates/`: HTML templates

## Deployment

### Production Deployment
1. **Environment Setup**:
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Environment Variables**:
   ```bash
   export FLASK_ENV=production
   ```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Cloud Deployment Options
- **Heroku**: Use the provided Procfile
- **AWS Elastic Beanstalk**: Follow Flask deployment guide
- **Google Cloud Run**: Container-based deployment
- **Azure App Service**: Python web app deployment

## Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables or secure key management
- Rotate keys regularly
- Monitor API usage for anomalies

### File Handling
- Validate file types and sizes
- Implement virus scanning for uploaded files
- Use secure file storage
- Regular cleanup of temporary files

### Network Security
- Use HTTPS in production
- Implement rate limiting
- Add authentication for sensitive operations
- Monitor for unusual activity

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Include error handling

### Testing
- Write unit tests for new features
- Test with various file formats
- Verify API endpoints
- Performance testing for large files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper and GPT models
- Hugging Face for pyannote.audio
- PySceneDetect for video scene detection
- Flask community for the web framework
- FFmpeg for multimedia processing

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Include system information and error logs

## Changelog

### Version 1.0.0
- Initial release
- Basic audio/video processing
- Web interface
- API endpoints
- File monitoring
- Duplicate detection

---

**Note**: This tool processes audio and video files using cloud-based AI services. Ensure you comply with your organization's data privacy policies and terms of service for all integrated APIs.
"""
