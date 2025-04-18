
from datetime import datetime
from flask import render_template, request, jsonify, Response, stream_with_context, send_file
from Down_vid import app
from Down_vid.controllers.process_controller import process_controller
import requests
import os
import uuid
import yt_dlp
from urllib.parse import quote

@app.route('/')
@app.route('/home')
def home():
    return render_template(
        'index.html',
        year=datetime.now().year,
    )

@app.route('/analyze', methods=['POST'])
def analyze_video():
    data = request.get_json(force=True)
    url = data.get("url")

    return process_controller().analyze_video(url)

@app.route('/download', methods=['POST'])
def download_file():
    data = request.form
    url = data.get('url')
    file_name = data.get('filename')

    if not url:
        return "Missing 'url' query parameter", 400

    # Forward range headers to the source
    headers = {}
    range_header = request.headers.get('Range')
    if range_header:
        headers['Range'] = range_header
    
    try:
        # Stream the video with range support
        req = requests.get(url, headers=headers, stream=True)
        req.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching video: {str(e)}", 502

    # Create response with correct headers
    response = Response(
        req.iter_content(chunk_size=8192),
        status=req.status_code,
        content_type=req.headers.get('content-type', 'video/mp4')
    )
    
    # 1. Content Disposition - Force download with proper filename
    safe_filename = quote(file_name)  # URL-encode the filename
    response.headers['Content-Disposition'] = f'attachment; filename="{file_name}"; filename*=UTF-8\'\'{safe_filename}'
    
    # 2. Caching Headers (adjust as needed)
    response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 day cache
    response.headers['ETag'] = f'"{hash(url)}"'  # Simple ETag based on URL
    
    # 3. Range support headers
    response.headers['Accept-Ranges'] = 'bytes'
    if 'Content-Range' in req.headers:
        response.headers['Content-Range'] = req.headers['Content-Range']
    if 'Content-Length' in req.headers:
        response.headers['Content-Length'] = req.headers['Content-Length']
    
    return response

