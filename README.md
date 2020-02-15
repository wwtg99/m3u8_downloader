M3U8 Downloader
===============

# Description

A simple script to download videos by m3u8 file for some video can not be downloaded by youtube-dl or you-get.

# Dependency

Install [ffmpe](http://ffmpeg.org/download.html) first.

Depends on Python 3.5+, Install python libs in `requirements.txt`.

# Usage

1. Download m3u8 file manually
2. Download video parts by m3u8 files and merged into mp4

```
python downloader.py <path-to-m3u8-file> <domain-prefix-for-video>
```

Tips: Open the m3u8 file, <domain-prefix-for-video> + <ts-part-in-m3u8> is the real url path of video part.

# Support

Any videos use m3u8 files.