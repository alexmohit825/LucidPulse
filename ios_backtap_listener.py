#!/usr/bin/env python3
"""
iOS Back Tap Universal Receiver
Listens for raw image POSTs from iOS Shortcut (Double Tap Back of iPhone)
Accepts: Raw binary PNG/JPEG, Multipart Form Data, Base64, on any path.
"""

import os
import sys
import datetime
import asyncio
from aiohttp import web

UPLOAD_DIR = r"C:\Users\mohal\Documents\antigravity\LucidPulse\uploads"
BRAIN_DIR = r"C:\Users\mohal\.gemini\antigravity\brain\97dc109d-f819-4f89-969d-96892bf7d572\.user_uploaded"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

async def handle_any(request):
    try:
        content_type = request.headers.get('Content-Type', '')
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Multipart Form
        if 'multipart/form-data' in content_type:
            reader = await request.multipart()
            while True:
                part = await reader.next()
                if part is None:
                    break
                data = await part.read()
                if data:
                    save_image(data, f"backtap_{ts}.png")
            return web.Response(text="OK - Received Multipart")
            
        # 2. Raw Binary Body (Direct image from iOS Shortcut)
        body = await request.read()
        if body:
            save_image(body, f"backtap_{ts}.png")
            return web.Response(text="OK - Received Binary Image")
            
    except Exception as e:
        print(f"Error receiving image: {e}")
        return web.Response(status=500, text=str(e))
        
    return web.Response(text="OK")

def save_image(data, filename):
    p1 = os.path.join(UPLOAD_DIR, filename)
    p2 = os.path.join(BRAIN_DIR, filename)
    with open(p1, 'wb') as f:
        f.write(data)
    with open(p2, 'wb') as f:
        f.write(data)
    print(f"\n=======================================================")
    print(f"📸 [BACK TAP CAPTURED!] Received screenshot from iPhone")
    print(f"   Saved to: {p1}")
    print(f"=======================================================\n")

async def start_listeners():
    # Ports to listen on simultaneously so any existing iOS Shortcut connects seamlessly
    ports = [5000, 8000, 8080, 9999]
    apps = []
    
    for port in ports:
        app = web.Application()
        app.router.add_route('*', '/{tail:.*}', handle_any)
        runner = web.AppRunner(app)
        await runner.setup()
        try:
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            print(f"[*] iOS Back Tap Listener ACTIVE on port {port}")
            apps.append(runner)
        except Exception as e:
            print(f"[-] Port {port} unavailable: {e}")
            
    print("\n--> Ready! Double-tap the back of your iPhone now.")
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(start_listeners())
    except KeyboardInterrupt:
        pass
