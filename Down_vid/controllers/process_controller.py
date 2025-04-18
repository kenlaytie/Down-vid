from flask import jsonify
import requests
import yt_dlp  # ✅ Corrected this
import traceback  # ✅ Added this
from io import BytesIO
from PIL import Image
from collections import Counter

class process_controller:

    # Get Image Color

    @staticmethod
    def get_color(image_url, resize=100):
        # Download image from URL
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert('RGB')
    
        # Resize to reduce processing
        img = img.resize((resize, resize))
    
        # Get pixels and find most common color
        pixels = list(img.getdata())
        most_common_color = Counter(pixels).most_common(1)[0][0]
        return tuple(int(c * 0.5) for c in most_common_color)

    # Get Size

    @staticmethod
    def sizeof_fmt(num, suffix="B"):
        try:
            num = int(num)
        except:
            return "Unknown"
        for unit in ["", "K", "M", "G"]:
            if abs(num) < 1024.0:
                return f"{num:.1f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f} T{suffix}"

    # Analyze Video

    def analyze_video(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'forcejson': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            formats = []

            # Filter: only MP4 video formats (exclude audio-only)
            mp4_videos = [
                f for f in info.get('formats', [])
                if f.get('ext') == 'mp4' and f.get('vcodec') != 'none' and f.get('height') and (f.get('filesize') or f.get('filesize_approx'))
            ]

            # Sort by resolution (height) descending
            mp4_videos.sort(key=lambda x: x.get('height', 0), reverse=True)

            # Pick top 4
            top4 = mp4_videos[:4]

            for f in top4:
                formats.append({
                    "format_id": f.get("format_id"),
                    "type": "video",
                    "ext": f.get("ext"),
                    "resolution": f.get("resolution") or f.get("height"),
                    "fps": f.get("fps"),
                    "url": f.get("url"),
                    "filesize": self.sizeof_fmt(f.get("filesize") or f.get("filesize_approx")),
                })

            thumbnail = info.get("thumbnail");

            return jsonify({
                "exists": True,
                "title": info.get("title"),
                "thumbnail": thumbnail,
                "color": self.get_color(thumbnail),
                "formats": formats,
            })

        except Exception as e:
            traceback.print_exc()
            return jsonify({"exists": False, "error": f"Error: {str(e)}"}), 400

