import streamlit as st
import os
import tempfile
import json
from pathlib import Path
import time
from audio_processor import AudioProcessor
from video_generator import VideoGenerator
from mp3_embedder import MP3Embedder
from utils import format_timestamp, validate_audio_file

# Page configuration
st.set_page_config(
    page_title="SyncMaster - AI Audio-Text Synchronization",
    page_icon="🎵",
    layout="wide"
)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'transcription_data' not in st.session_state:
    st.session_state.transcription_data = None
if 'edited_text' not in st.session_state:
    st.session_state.edited_text = ""
if 'video_style' not in st.session_state:
    st.session_state.video_style = {
        'animation_style': 'Karaoke Style',
        'text_color': '#FFFFFF',
        'highlight_color': '#FFD700',
        'background_color': '#000000',
        'font_family': 'Arial',
        'font_size': 48
    }

def main():
    # Header
    st.title("🎵 SyncMaster")
    st.markdown("### The Intelligent Audio-Text Synchronization Platform")
    st.markdown("Transform your audio files into mobile-compatible MP3s with synchronized lyrics and animated MP4 videos.")
    
    # Progress indicator
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.step >= 1:
            st.success("Step 1: Upload & Process")
        else:
            st.info("Step 1: Upload & Process")
    with col2:
        if st.session_state.step >= 2:
            st.success("Step 2: Review & Customize")
        elif st.session_state.step == 1:
            st.info("Step 2: Review & Customize")
        else:
            st.empty()
    with col3:
        if st.session_state.step >= 3:
            st.success("Step 3: Export")
        elif st.session_state.step >= 2:
            st.info("Step 3: Export")
        else:
            st.empty()
    
    st.divider()
    
    # Step routing
    if st.session_state.step == 1:
        step_1_upload_and_process()
    elif st.session_state.step == 2:
        step_2_review_and_customize()
    elif st.session_state.step == 3:
        step_3_export()

def step_1_upload_and_process():
    st.header("Step 1: Upload Your Audio File")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['mp3', 'wav', 'm4a'],
        help="Supported formats: MP3, WAV, M4A"
    )
    
    if uploaded_file is not None:
        st.session_state.audio_file = uploaded_file
        
        # Display file info
        st.success(f"File uploaded: {uploaded_file.name}")
        st.info(f"File size: {uploaded_file.size / 1024 / 1024:.2f} MB")
        
        # Audio preview
        st.audio(uploaded_file)
        
        # Process button
        if st.button("🚀 Start AI Processing", type="primary", use_container_width=True):
            process_audio()
    
    # Reset button
    if st.session_state.audio_file is not None:
        if st.button("🔄 Upload Different File"):
            reset_session()
            st.rerun()

def process_audio():
    """Process the uploaded audio file with AI transcription"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(st.session_state.audio_file.name).suffix) as tmp_file:
            tmp_file.write(st.session_state.audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Validate audio file
        if not validate_audio_file(tmp_file_path):
            st.error("Invalid audio file format. Please upload a valid MP3, WAV, or M4A file.")
            os.unlink(tmp_file_path)
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize audio processor
        processor = AudioProcessor()
        
        # Step 1: Transcription
        status_text.text("🎤 Transcribing audio with AI...")
        progress_bar.progress(20)
        
        transcription_result = processor.transcribe_audio(tmp_file_path)
        
        if not transcription_result:
            st.error("Failed to transcribe audio. Please try again with a different file.")
            os.unlink(tmp_file_path)
            return
        
        progress_bar.progress(60)
        status_text.text("⏱️ Extracting word-level timestamps...")
        
        # Step 2: Get word-level timestamps
        word_timestamps = processor.get_word_timestamps(tmp_file_path)
        
        if not word_timestamps:
            st.error("Failed to extract word timestamps. Please try again.")
            os.unlink(tmp_file_path)
            return
        
        progress_bar.progress(90)
        status_text.text("✅ Processing complete!")
        
        # Store results
        st.session_state.transcription_data = {
            'text': transcription_result,
            'word_timestamps': word_timestamps,
            'audio_path': tmp_file_path
        }
        st.session_state.edited_text = transcription_result
        
        progress_bar.progress(100)
        time.sleep(1)
        
        # Move to next step
        st.session_state.step = 2
        st.success("🎉 Audio processing complete! Moving to customization...")
        time.sleep(2)
        st.rerun()
        
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)

def step_2_review_and_customize():
    st.header("Step 2: Review & Customize")
    
    if st.session_state.transcription_data is None:
        st.error("No transcription data found. Please go back to Step 1.")
        if st.button("← Back to Step 1"):
            st.session_state.step = 1
            st.rerun()
        return
    
    # Two columns for editor and customization
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("📝 Text Editor")
        st.markdown("Review and edit the transcribed text:")
        
        # Text editor
        edited_text = st.text_area(
            "Transcribed Text",
            value=st.session_state.edited_text,
            height=300,
            help="Edit any mistakes in the transcription"
        )
        st.session_state.edited_text = edited_text
        
        # Word count
        word_count = len(edited_text.split())
        st.caption(f"Word count: {word_count}")
        
        # Preview synchronized text
        if st.button("🔍 Preview Synchronization"):
            show_sync_preview()
    
    with col2:
        st.subheader("🎨 Video Style Customization")
        
        # Animation style
        animation_style = st.selectbox(
            "Animation Style",
            ["Karaoke Style", "Pop-up Word", "Line-by-Line", "Fade In/Out"],
            index=0
        )
        st.session_state.video_style['animation_style'] = animation_style
        
        # Colors
        st.markdown("**Colors**")
        text_color = st.color_picker("Text Color", st.session_state.video_style['text_color'])
        highlight_color = st.color_picker("Highlight Color", st.session_state.video_style['highlight_color'])
        background_color = st.color_picker("Background Color", st.session_state.video_style['background_color'])
        
        st.session_state.video_style.update({
            'text_color': text_color,
            'highlight_color': highlight_color,
            'background_color': background_color
        })
        
        # Typography
        st.markdown("**Typography**")
        font_family = st.selectbox(
            "Font Family",
            ["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana"],
            index=0
        )
        font_size = st.slider("Font Size", 24, 72, st.session_state.video_style['font_size'])
        
        st.session_state.video_style.update({
            'font_family': font_family,
            'font_size': font_size
        })
        
        # Style preview
        st.markdown("**Style Preview**")
        preview_html = f"""
        <div style="
            background-color: {background_color};
            color: {text_color};
            font-family: {font_family};
            font-size: {font_size//2}px;
            padding: 20px;
            text-align: center;
            border-radius: 10px;
            margin: 10px 0;
        ">
            Sample lyrics text<br>
            <span style="color: {highlight_color}; font-weight: bold;">highlighted word</span>
        </div>
        """
        st.markdown(preview_html, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Upload"):
            st.session_state.step = 1
            st.rerun()
    
    with col3:
        if st.button("Continue to Export →", type="primary"):
            st.session_state.step = 3
            st.rerun()

def show_sync_preview():
    """Show a preview of synchronized text"""
    st.subheader("🎵 Synchronization Preview")
    
    if st.session_state.transcription_data and st.session_state.transcription_data.get('word_timestamps'):
        words_data = st.session_state.transcription_data['word_timestamps']
        
        # Show first 10 words with timestamps
        st.markdown("**Sample word timings:**")
        preview_data = []
        for i, word_data in enumerate(words_data[:10]):
            start_time = format_timestamp(word_data.get('start', 0))
            end_time = format_timestamp(word_data.get('end', 0))
            word = word_data.get('word', 'N/A')
            preview_data.append(f"{start_time} - {end_time}: '{word}'")
        
        for item in preview_data:
            st.code(item)
        
        if len(words_data) > 10:
            st.caption(f"... and {len(words_data) - 10} more words")
    else:
        st.warning("No timing data available for preview.")

def step_3_export():
    st.header("Step 3: Export Your Synchronized Media")
    
    if st.session_state.transcription_data is None:
        st.error("No transcription data found. Please go back to Step 1.")
        if st.button("← Back to Step 1"):
            st.session_state.step = 1
            st.rerun()
        return
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎵 MP3 Export")
        st.markdown("Export MP3 with embedded synchronized lyrics (SYLT) for mobile compatibility")
        
        if st.button("📱 Export MP3 with Lyrics", type="primary", use_container_width=True):
            export_mp3()
    
    with col2:
        st.subheader("🎬 MP4 Video Export")
        st.markdown("Create an animated video with synchronized text")
        
        if st.button("🎥 Generate MP4 Video", type="primary", use_container_width=True):
            export_mp4()
    
    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Back to Customize"):
            st.session_state.step = 2
            st.rerun()
    
    with col3:
        if st.button("🔄 Start Over"):
            reset_session()
            st.rerun()

def export_mp3():
    """Export MP3 file with embedded SYLT lyrics"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎵 Preparing MP3 with synchronized lyrics...")
        progress_bar.progress(20)
        
        # Initialize MP3 embedder
        embedder = MP3Embedder()
        
        # Prepare lyrics data
        word_timestamps = st.session_state.transcription_data['word_timestamps']
        audio_path = st.session_state.transcription_data['audio_path']
        
        progress_bar.progress(50)
        status_text.text("📱 Embedding SYLT frame for mobile compatibility...")
        
        # Create output file
        output_filename = f"synced_{st.session_state.audio_file.name}"
        output_path = embedder.embed_sylt_lyrics(
            audio_path, 
            word_timestamps, 
            st.session_state.edited_text,
            output_filename
        )
        
        progress_bar.progress(90)
        status_text.text("✅ MP3 export complete!")
        
        # Provide download
        if os.path.exists(output_path):
            with open(output_path, 'rb') as file:
                st.download_button(
                    label="📥 Download Synchronized MP3",
                    data=file.read(),
                    file_name=output_filename,
                    mime="audio/mpeg",
                    use_container_width=True
                )
            
            progress_bar.progress(100)
            st.success("🎉 MP3 export successful! The file includes embedded synchronized lyrics compatible with mobile players.")
        else:
            st.error("Failed to create MP3 file.")
            
    except Exception as e:
        st.error(f"Error exporting MP3: {str(e)}")

def export_mp4():
    """Export MP4 video with synchronized text animation"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎬 Generating synchronized video...")
        progress_bar.progress(20)
        
        # Initialize video generator
        generator = VideoGenerator()
        
        # Prepare video data
        word_timestamps = st.session_state.transcription_data['word_timestamps']
        audio_path = st.session_state.transcription_data['audio_path']
        video_style = st.session_state.video_style
        
        progress_bar.progress(40)
        status_text.text("🎨 Applying custom styling...")
        
        # Generate video
        output_filename = f"synced_video_{Path(st.session_state.audio_file.name).stem}.mp4"
        output_path = generator.create_synchronized_video(
            audio_path,
            word_timestamps,
            st.session_state.edited_text,
            video_style,
            output_filename
        )
        
        progress_bar.progress(80)
        status_text.text("🎞️ Rendering final video...")
        
        # Provide download
        if os.path.exists(output_path):
            progress_bar.progress(100)
            status_text.text("✅ Video export complete!")
            
            with open(output_path, 'rb') as file:
                st.download_button(
                    label="📥 Download Synchronized Video",
                    data=file.read(),
                    file_name=output_filename,
                    mime="video/mp4",
                    use_container_width=True
                )
            
            st.success("🎉 MP4 video export successful! Your synchronized lyrics video is ready for sharing.")
        else:
            st.error("Failed to create video file.")
            
    except Exception as e:
        st.error(f"Error exporting video: {str(e)}")

def reset_session():
    """Reset all session state variables"""
    for key in list(st.session_state.keys()):
        if key not in ['step']:
            del st.session_state[key]
    st.session_state.step = 1
    st.session_state.audio_file = None
    st.session_state.transcription_data = None
    st.session_state.edited_text = ""
    st.session_state.video_style = {
        'animation_style': 'Karaoke Style',
        'text_color': '#FFFFFF',
        'highlight_color': '#FFD700',
        'background_color': '#000000',
        'font_family': 'Arial',
        'font_size': 48
    }

if __name__ == "__main__":
    main()
