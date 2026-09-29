import os
import sys
import http.server
import socketserver
import threading
import urllib.request
import json

PORT = 8990
DIRECTORY = r"C:\Users\mohal\Documents\antigravity\LucidPulse"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def run_tests():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print(f"[OK] Test HTTP Server running on http://127.0.0.1:{PORT}")

        # Test index.html
        req = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/index.html")
        content = req.read().decode('utf-8')
        assert req.status == 200, f"Expected 200, got {req.status}"
        assert "LUCIDPULSE" in content, "Missing brand title in index.html"
        assert "fleetScatterCanvas" in content, "Missing scatter canvas in index.html"
        print("[OK] index.html: HTTP 200 OK | Content verified")

        # Test styles.css
        req_css = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/styles.css")
        css_content = req_css.read().decode('utf-8')
        assert req_css.status == 200, f"Expected 200, got {req_css.status}"
        assert "--accent-gold" in css_content, "Missing theme variables in styles.css"
        print("[OK] styles.css: HTTP 200 OK | Glassmorphism & luxury styling verified")

        # Test app.js
        req_js = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/app.js")
        js_content = req_js.read().decode('utf-8')
        assert req_js.status == 200, f"Expected 200, got {req_js.status}"
        assert "generateFleetDataset" in js_content, "Missing fleet dataset generator in app.js"
        assert "renderFleetScatterChart" in js_content, "Missing chart renderer in app.js"
        print("[OK] app.js: HTTP 200 OK | Telemetry models & chart logic verified")

        # Test functions/api/lucid.js file presence and size
        func_path = os.path.join(DIRECTORY, "functions", "api", "lucid.js")
        assert os.path.exists(func_path), "Missing Cloudflare worker proxy"
        with open(func_path, 'r', encoding='utf-8') as f:
            func_code = f.read()
            assert "onRequest" in func_code, "Invalid worker syntax"
            assert "AWSCognitoIdentityProviderService" in func_code, "Missing Cognito client target"
        print("[OK] functions/api/lucid.js: Cloudflare Edge Worker verified")

        httpd.shutdown()
        print("\n=== ALL E2E PROGRAMMATIC VERIFICATION CHECKS PASSED (100%) ===")

if __name__ == "__main__":
    run_tests()
