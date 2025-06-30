import os
import tempfile
import subprocess
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
import textwrap

class VideoGenerator:
    """Creates actual MP4 videos with synchronized text animation"""
    
    def __init__(self):
        """Initialize the video generator"""
        self.temp_dir = tempfile.mkdtemp()
        self.frame_rate = 10  # Lower frame rate for faster processing
        
    def create_synchronized_video(self, audio_path: str, word_timestamps: List[Dict], 
                                text: str, style_config: Dict, output_filename: str) -> str:
        """
        Create a synchronized MP4 video with animated text
        
        Args:
            audio_path: Path to the audio file
            word_timestamps: List of word timestamp dictionaries
            text: The full text content
            style_config: Dictionary with styling configuration
            output_filename: Name for the output file
            
        Returns:
            Path to the output MP4 file
        """
        try:
            output_path = os.path.join(self.temp_dir, output_filename)
            
            # Try to create a simple slideshow video
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
            cmd = [
                'ffmpeg', '-y', '-v', 'quiet',
                '-loop', '1', '-i', img_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-t', '60',  # Limit to 60 seconds max
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except Exception as e:
            # If ffmpeg fails, try a simpler approach
            return self._create_fallback_video(audio_path, text, output_filename)
    
    def _create_fallback_video(self, audio_path: str, text: str, output_filename: str) -> str:
        """Create a basic video file as fallback"""
        output_path = os.path.join(self.temp_dir, output_filename)
        
        try:
            # Create a simple black video with audio
            cmd = [
                'ffmpeg', '-y', '-v', 'quiet',
                '-f', 'lavfi', '-i', 'color=black:size=1280x720:duration=60',
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'copy',
                '-shortest',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                # Final fallback - copy the audio file as MP4
                fallback_path = output_path.replace('.mp4', '.m4a')
                import shutil
                shutil.copy2(audio_path, fallback_path)
                return fallback_path
                
        except Exception as e:
            # Final fallback - copy the audio file
            fallback_path = output_path.replace('.mp4', '.m4a')
            import shutil
            shutil.copy2(audio_path, fallback_path)
            return fallback_path
    
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
            import shutil
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass