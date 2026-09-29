#!/usr/bin/env python3
"""
ScreenDrop — Instant iPhone-to-PC Photo & Screenshot Transfer Portal
Uses aiohttp for modern multipart file uploads on Python 3.14+.
"""

import os
import sys
import socket
import datetime
import asyncio
from aiohttp import web

PORT = 9999
UPLOAD_DIR = r"C:\Users\mohal\Documents\antigravity\LucidPulse\uploads"
BRAIN_DIR = r"C:\Users\mohal\.gemini\antigravity\brain\97dc109d-f819-4f89-969d-96892bf7d572\.user_uploaded"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

HTML_PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>ScreenDrop — iPhone Photo Transfer</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif;
      background: #07080a;
      color: #f8fafc;
      margin: 0;
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      box-sizing: border-box;
      text-align: center;
    }}
    .container {{
      max-width: 480px;
      width: 100%;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(212, 175, 55, 0.3);
      border-radius: 20px;
      padding: 32px 24px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.8);
    }}
    h1 {{
      font-size: 28px;
      font-weight: 800;
      margin-bottom: 8px;
      background: linear-gradient(120deg, #fff 40%, #d4af37 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    p {{
      color: #94a3b8;
      font-size: 14px;
      margin-bottom: 24px;
      line-height: 1.5;
    }}
    .drop-zone {{
      border: 2px dashed #d4af37;
      border-radius: 16px;
      padding: 40px 20px;
      background: rgba(212, 175, 55, 0.05);
      cursor: pointer;
      transition: all 0.2s;
    }}
    .drop-zone:active {{
      background: rgba(212, 175, 55, 0.15);
      transform: scale(0.98);
    }}
    .drop-icon {{
      font-size: 48px;
      margin-bottom: 12px;
    }}
    .btn-select {{
      background: linear-gradient(135deg, #d4af37, #c5a059);
      color: #000;
      font-weight: 700;
      font-size: 15px;
      padding: 14px 28px;
      border-radius: 12px;
      border: none;
      cursor: pointer;
      display: inline-block;
      margin-top: 16px;
      box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }}
    #status {{
      margin-top: 20px;
      font-size: 15px;
      font-weight: 600;
      color: #10b981;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="drop-icon">📱 ➔ 💻</div>
    <h1>ScreenDrop</h1>
    <p>Tap below to pick your latest Lucid screenshot from your iPhone Photo Library.</p>

    <div class="drop-zone" onclick="document.getElementById('fileInput').click()">
      <div style="font-size: 16px; font-weight: 600; color: #fff;">Tap to Select iPhone Photo</div>
      <div style="font-size: 12px; color: #94a3b8; margin-top: 6px;">Supports All Photo Formats & Screenshots</div>
      <input type="file" id="fileInput" accept="image/*" multiple style="display: none;" onchange="handleUpload(this)">
      <div class="btn-select">Choose Photo / Screenshot</div>
    </div>

    <div id="status"></div>
    <div style="margin-top: 24px; font-size: 12px; color: #64748b;">
      Connected to PC at: <strong>http://{LOCAL_IP}:{PORT}</strong>
    </div>
  </div>

  <script>
    async function handleUpload(input) {{
      if (!input.files || input.files.length === 0) return;
      
      const status = document.getElementById('status');
      status.innerText = "⏳ Uploading " + input.files.length + " photo(s)...";
      status.style.color = "#d4af37";
      
      const formData = new FormData();
      for (let i = 0; i < input.files.length; i++) {{
        formData.append('photo', input.files[i]);
      }}

      try {{
        const resp = await fetch('/upload', {{
          method: 'POST',
          body: formData
        }});
        
        if (resp.ok) {{
          status.innerText = "✅ Successfully sent to PC & Antigravity!";
          status.style.color = "#10b981";
          setTimeout(() => {{ input.value = ''; }}, 2000);
        }} else {{
          status.innerText = "❌ Upload failed. Please retry.";
          status.style.color = "#ef4444";
        }}
      }} catch (err) {{
        status.innerText = "❌ Error: " + err.message;
        status.style.color = "#ef4444";
      }}
    }}
  </script>
</body>
</html>
"""

async def handle_index(request):
    return web.Response(text=HTML_PAGE, content_type='text/html')

async def handle_upload(request):
    reader = await request.multipart()
    saved_files = []
    
    while True:
        field = await reader.next()
        if field is None:
            break
        if field.name == 'photo':
            filename = field.filename or 'upload.png'
            ext = os.path.splitext(filename)[1] or '.png'
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            out_name = f"screendrop_{ts}{ext}"
            
            p1 = os.path.join(UPLOAD_DIR, out_name)
            p2 = os.path.join(BRAIN_DIR, out_name)
            
            content = await field.read()
            with open(p1, 'wb') as f:
                f.write(content)
            with open(p2, 'wb') as f:
                f.write(content)
                
            print(f"[ScreenDrop] Received iPhone photo: {p1}")
            saved_files.append(out_name)
            
    return web.json_response({"status": "ok", "files": saved_files})

def main():
    app = web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_post('/upload', handle_upload)
    
    print("==========================================================")
    print("                 SCREENDROP SERVER ACTIVE                 ")
    print("==========================================================")
    print(f"--> On your iPhone, open Safari and go to:")
    print(f"    http://{LOCAL_IP}:{PORT}")
    print("==========================================================")
    web.run_app(app, port=PORT, print=None)

if __name__ == '__main__':
    main()
