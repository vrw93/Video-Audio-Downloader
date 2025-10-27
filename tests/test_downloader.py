import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from modul.downloader import YTDownloader

@pytest.fixture
def downloader(tmp_path):
    d = Downloader()
    d._progress_hook = MagicMock()
    d.temp_dir = tmp_path
    return d

@patch("modul.downloader.yt.YoutubeDL")
def test_download_audio(mock_yt, downloader):
    mock_instance = mock_yt.return_value.__enter__.return_value
    mock_instance.download.return_value = 0

    url = "https://youtube.com/watch?v=dummy"
    format = "mp3"
    filePath = downloader.temp_dir

    downloader.downloadAudio(url, filePath, format)

    mock_yt.assert_called_once()
    mock_instance.download.assert_called_once_with([url])
