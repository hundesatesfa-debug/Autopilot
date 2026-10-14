# AutoPilot AI Vercel Entrypoint
from index import app, application, handler

__all__ = ["app", "application", "handler"]

if __name__ == "__main__":
    from http.server import HTTPServer
    server = HTTPServer(("0.0.0.0", 3000), handler)
    print("AutoPilot AI running on http://localhost:3000")
    server.serve_forever()
