import yt_dlp as yt
from pathlib import Path
import sys

class YTDownloader:
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def _progress_hook(self, d):
        if self.progress_callback:
            self.progress_callback(d)

    def downloadAudio(self, url, filePath, format):
        ffmpeg_path = Path(__file__).resolve().parent / "ffmpeg"
        ydl_opst = {
            'format' : 'bestaudio/best',
            'ignoreerrors': True,
            'no_cache_dir': True,  
            'outtmpl' : str(filePath / "%(title)s.%(ext)s"),
            'postprocessors' : [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec' : format,
            }],
            'progress_hooks' : [self._progress_hook],
            'quiet': True,
            'noplaylist': True,
            'color': 'never',
            'ffmpeg_location': ffmpeg_path
        }
        with yt.YoutubeDL(ydl_opst) as ydl:
            ydl.download([url])
    
    def downloadVideo(self, url, filePath, format):
        ffmpeg_path = getattr(sys, '_MEIPASS',Path(__file__).resolve().parent / "ffmpeg")
        ydl_opts = {
            'format' : 'bestvideo+bestaudio/best',
            'ignoreerrors': True,
            'merge_output_format' : format,
            'no_cache_dir': True,
            'outtmpl' : str(filePath / "%(title)s.%(ext)s"),
            'progress_hooks' : [self._progress_hook],
            'quiet': True,
            'noplaylist': True,
            'color': 'never',
            'ffmpeg_location': ffmpeg_path
        }
        with yt.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
