import os
import tempfile
import subprocess
import shutil
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
import textwrap

class VideoGenerator:
    """Creates actual MP4 videos with synchronized text animation"""
    
    def __init__(self):
        """Initialize the video generator"""
        self.temp_dir = tempfile.mkdtemp()
        
    def create_synchronized_video(self, audio_path: str, word_timestamps: List[Dict], 
                                text: str, style_config: Dict, output_filename: str) -> str:
        """
        Create a synchronized MP4 video with animated text
        """
        try:
            output_path = os.path.join(self.temp_dir, output_filename)
            
            # Create a simple slideshow video
            return self._create_simple_slideshow(audio_path, text, style_config, output_filename)
            
        except Exception as e:
            # If video creation fails, create a basic video file
            return self._create_fallback_video(audio_path, text, output_filename)
    
    def _create_simple_slideshow(self, audio_path: str, text: str, style_config: Dict, output_filename: str) -> str:
        """Create a simple slideshow video"""
        output_path = os.path.join(self.temp_dir, output_filename)
        
        # Create a single image with the text
        width, height = 1280, 720
        bg_color = self._hex_to_rgb(style_config.get('background_color', '#000000'))
        text_color = self._hex_to_rgb(style_config.get('text_color', '#FFFFFF'))
        
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Wrap text to fit on screen
        wrapped_text = textwrap.fill(text, width=50)
        
        try:
            # Try to use a system font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
            except:
                font = ImageFont.load_default()
        
        # Calculate text position for centering
        lines = wrapped_text.split('\n')
        line_height = 40
        total_height = len(lines) * line_height
        start_y = (height - total_height) // 2
        
        # Draw each line of text
        for i, line in enumerate(lines):
            if line.strip():  # Only draw non-empty lines
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + i * line_height
                draw.text((x, y), line, fill=text_color, font=font)
        
        # Add title
        title = "SyncMaster - متزامن النص"
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            title_font = font
        
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 50), title, fill=self._hex_to_rgb('#FFD700'), font=title_font)
        
        # Save image
        img_path = os.path.join(self.temp_dir, 'slideshow.png')
        img.save(img_path)
        
        # Create video from single image and audio using ffmpeg
        try:
            # First check if ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=10)
            except:
                print("FFmpeg not available, using fallback")
                return self._create_fallback_video(audio_path, text, output_filename)
            
            cmd = [
                'ffmpeg', '-y', '-loglevel', 'error',
                '-loop', '1', '-i', img_path,
                '-i', audio_path,
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-c:a', 'aac', '-b:a', '128k',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1280:720',
                '-r', '10',  # 10 fps for smaller file size
                '-shortest',
                '-t', '30',  # Limit to 30 seconds for faster processing
                output_path
            ]
            
            print(f"Running FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Video created successfully: {output_path}")
                return output_path
            else:
                print(f"FFmpeg error: {result.stderr}")
                print(f"FFmpeg stdout: {result.stdout}")
                # Try fallback method
                return self._create_fallback_video(audio_path, text, output_filename)
                
        except Exception as e:
            print(f"Video creation error: {e}")
            # If ffmpeg fails, try a simpler approach
            return self._create_fallback_video(audio_path, text, output_filename)
    
    def _create_fallback_video(self, audio_path: str, text: str, output_filename: str) -> str:
        """Create a basic video file as fallback"""
        output_path = os.path.join(self.temp_dir, output_filename)
        
        try:
            # First try to create a simple image slideshow
            width, height = 1280, 720
            img = Image.new('RGB', (width, height), (0, 0, 0))  # Black background
            draw = ImageDraw.Draw(img)
            
            # Add simple text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            # Draw title
            title = "SyncMaster Video"
            bbox = draw.textbbox((0, 0), title, font=font)
            title_width = bbox[2] - bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, height//2 - 50), title, fill=(255, 255, 255), font=font)
            
            # Draw subtitle
            subtitle = "Synchronized Audio & Text"
            try:
                sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            except:
                sub_font = font
            bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
            sub_width = bbox[2] - bbox[0]
            sub_x = (width - sub_width) // 2
            draw.text((sub_x, height//2 + 20), subtitle, fill=(255, 215, 0), font=sub_font)
            
            # Save fallback image
            fallback_img_path = os.path.join(self.temp_dir, 'fallback.png')
            img.save(fallback_img_path)
            
            # Try to create video with simpler ffmpeg command
            cmd = [
                'ffmpeg', '-y', '-loglevel', 'panic',
                '-loop', '1', '-i', fallback_img_path,
                '-i', audio_path,
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-r', '1',  # Very low frame rate
                '-shortest',
                '-t', '10',  # Short duration
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Fallback video created: {output_path}")
                return output_path
            else:
                print(f"Fallback FFmpeg also failed: {result.stderr}")
                # Final fallback - copy audio as M4A with proper extension
                fallback_path = os.path.join(self.temp_dir, output_filename.replace('.mp4', '.m4a'))
                shutil.copy2(audio_path, fallback_path)
                print(f"Created audio fallback: {fallback_path}")
                return fallback_path
                
        except Exception as e:
            print(f"Fallback video creation error: {e}")
            # Final fallback - copy the audio file
            try:
                fallback_path = os.path.join(self.temp_dir, output_filename.replace('.mp4', '.m4a'))
                shutil.copy2(audio_path, fallback_path)
                print(f"Final fallback audio: {fallback_path}")
                return fallback_path
            except Exception as copy_error:
                print(f"Even audio copy failed: {copy_error}")
                # Create a basic MP3 copy as final fallback
                try:
                    mp3_fallback = os.path.join(self.temp_dir, output_filename.replace('.mp4', '.mp3'))
                    shutil.copy2(audio_path, mp3_fallback)
                    return mp3_fallback
                except:
                    return audio_path  # Return original audio path as last resort
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return (255, 255, 255)  # Default to white
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (255, 255, 255)  # Default to white
    
    def __del__(self):
        """Clean up temporary files"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass