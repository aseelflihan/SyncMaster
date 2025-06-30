from mutagen.mp3 import MP3
from mutagen.id3 import ID3, SYLT, Encoding
import os
import tempfile
import shutil
from typing import List, Dict

class MP3Embedder:
    """Handles embedding SYLT synchronized lyrics into MP3 files"""
    
    def __init__(self):
        """Initialize the MP3 embedder"""
        self.temp_dir = tempfile.mkdtemp()
    
    def embed_sylt_lyrics(self, audio_path: str, word_timestamps: List[Dict], 
                         text: str, output_filename: str) -> str:
        """
        Embed SYLT synchronized lyrics into an MP3 file
        
        Args:
            audio_path: Path to the original audio file
            word_timestamps: List of word timestamp dictionaries
            text: The full text content
            output_filename: Name for the output file
            
        Returns:
            Path to the output MP3 file with embedded lyrics
        """
        try:
            # Create output path
            output_path = os.path.join(self.temp_dir, output_filename)
            
            # Copy original file to output path
            shutil.copy2(audio_path, output_path)
            
            # Load the MP3 file
            audio_file = MP3(output_path, ID3=ID3)
            
            # Add ID3 tag if it doesn't exist
            try:
                audio_file.add_tags()
            except:
                pass  # Tags already exist
            
            # Create SYLT frame data
            sylt_data = self._create_sylt_data(word_timestamps)
            
            if sylt_data:
                # Create SYLT frame
                sylt_frame = SYLT(
                    encoding=Encoding.UTF16,  # UTF-16 encoding for mobile compatibility
                    lang='eng',  # Language code
                    format=2,  # Absolute time in milliseconds
                    type=1,  # Content type: lyrics
                    text=sylt_data
                )
                
                # Add SYLT frame to the file
                audio_file.tags.add(sylt_frame)
                
                # Also add unsynchronized lyrics as fallback
                from mutagen.id3 import USLT
                uslt_frame = USLT(
                    encoding=Encoding.UTF16,
                    lang='eng',
                    desc='',
                    text=text
                )
                audio_file.tags.add(uslt_frame)
                
                # Save the file
                audio_file.save()
                
                return output_path
            else:
                raise Exception("Failed to create SYLT data")
                
        except Exception as e:
            raise Exception(f"Error embedding SYLT lyrics: {str(e)}")
    
    def _create_sylt_data(self, word_timestamps: List[Dict]) -> List[tuple]:
        """
        Create SYLT data format from word timestamps
        
        Args:
            word_timestamps: List of word timestamp dictionaries
            
        Returns:
            List of tuples (text, timestamp_in_milliseconds)
        """
        try:
            sylt_data = []
            
            for word_data in word_timestamps:
                word = word_data.get('word', '').strip()
                start_time = word_data.get('start', 0)
                
                if word:
                    # Convert seconds to milliseconds
                    timestamp_ms = int(start_time * 1000)
                    sylt_data.append((word, timestamp_ms))
            
            return sylt_data
            
        except Exception as e:
            print(f"Error creating SYLT data: {str(e)}")
            return []
    
    def _create_line_based_sylt_data(self, word_timestamps: List[Dict], max_words_per_line: int = 6) -> List[tuple]:
        """
        Create line-based SYLT data (alternative approach)
        
        Args:
            word_timestamps: List of word timestamp dictionaries
            max_words_per_line: Maximum words per line
            
        Returns:
            List of tuples (line_text, timestamp_in_milliseconds)
        """
        try:
            sylt_data = []
            current_line = []
            
            for word_data in word_timestamps:
                current_line.append(word_data)
                
                # Check if we should end this line
                if len(current_line) >= max_words_per_line:
                    if current_line:
                        line_text = ' '.join([w.get('word', '') for w in current_line]).strip()
                        start_time = current_line[0].get('start', 0)
                        timestamp_ms = int(start_time * 1000)
                        
                        if line_text:
                            sylt_data.append((line_text, timestamp_ms))
                        
                        current_line = []
            
            # Add remaining words as final line
            if current_line:
                line_text = ' '.join([w.get('word', '') for w in current_line]).strip()
                start_time = current_line[0].get('start', 0)
                timestamp_ms = int(start_time * 1000)
                
                if line_text:
                    sylt_data.append((line_text, timestamp_ms))
            
            return sylt_data
            
        except Exception as e:
            print(f"Error creating line-based SYLT data: {str(e)}")
            return []
    
    def verify_sylt_embedding(self, mp3_path: str) -> Dict:
        """
        Verify that SYLT lyrics are properly embedded
        
        Args:
            mp3_path: Path to the MP3 file
            
        Returns:
            Dictionary with verification results
        """
        try:
            audio_file = MP3(mp3_path)
            
            result = {
                'has_sylt': False,
                'has_uslt': False,
                'sylt_entries': 0,
                'error': None
            }
            
            if audio_file.tags:
                # Check for SYLT
                sylt_frames = audio_file.tags.getall('SYLT')
                if sylt_frames:
                    result['has_sylt'] = True
                    result['sylt_entries'] = len(sylt_frames[0].text) if sylt_frames[0].text else 0
                
                # Check for USLT (fallback)
                uslt_frames = audio_file.tags.getall('USLT')
                if uslt_frames:
                    result['has_uslt'] = True
            
            return result
            
        except Exception as e:
            return {
                'has_sylt': False,
                'has_uslt': False,
                'sylt_entries': 0,
                'error': str(e)
            }
    
    def extract_sylt_lyrics(self, mp3_path: str) -> List[Dict]:
        """
        Extract SYLT lyrics from an MP3 file (for debugging)
        
        Args:
            mp3_path: Path to the MP3 file
            
        Returns:
            List of dictionaries with text and timestamp
        """
        try:
            audio_file = MP3(mp3_path)
            lyrics_data = []
            
            if audio_file.tags:
                sylt_frames = audio_file.tags.getall('SYLT')
                
                for frame in sylt_frames:
                    if frame.text:
                        for text, timestamp_ms in frame.text:
                            lyrics_data.append({
                                'text': text,
                                'timestamp': timestamp_ms / 1000.0  # Convert to seconds
                            })
            
            return lyrics_data
            
        except Exception as e:
            print(f"Error extracting SYLT lyrics: {str(e)}")
            return []
    
    def create_lrc_file(self, word_timestamps: List[Dict], output_path: str) -> str:
        """
        Create an LRC (lyrics) file as an additional export option
        
        Args:
            word_timestamps: List of word timestamp dictionaries
            output_path: Path for the output LRC file
            
        Returns:
            Path to the created LRC file
        """
        try:
            lrc_lines = []
            
            # Group words into lines
            current_line = []
            for word_data in word_timestamps:
                current_line.append(word_data)
                
                if len(current_line) >= 8:  # 8 words per line
                    if current_line:
                        line_text = ' '.join([w.get('word', '') for w in current_line])
                        start_time = current_line[0].get('start', 0)
                        
                        # Format timestamp as [mm:ss.xx]
                        minutes = int(start_time // 60)
                        seconds = start_time % 60
                        timestamp_str = f"[{minutes:02d}:{seconds:05.2f}]"
                        
                        lrc_lines.append(f"{timestamp_str}{line_text}")
                        current_line = []
            
            # Add remaining words
            if current_line:
                line_text = ' '.join([w.get('word', '') for w in current_line])
                start_time = current_line[0].get('start', 0)
                
                minutes = int(start_time // 60)
                seconds = start_time % 60
                timestamp_str = f"[{minutes:02d}:{seconds:05.2f}]"
                
                lrc_lines.append(f"{timestamp_str}{line_text}")
            
            # Write LRC file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lrc_lines))
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Error creating LRC file: {str(e)}")
    
    def __del__(self):
        """Clean up temporary files"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
