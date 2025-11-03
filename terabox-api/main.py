from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# This package does the download extraction
from terabox_downloader import TeraboxDownloader

app = FastAPI()

# Restrict to your actual Netlify/portfolio domain in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["https://your-site.netlify.app"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Terabox API is live"}

@app.post("/extract")
async def extract_links(req: Request):
    data = await req.json()
    url = data.get("url")
    if not url or "terabox" not in url:
        return JSONResponse({"status": "error", "message": "Invalid or missing URL"}, status_code=400)

    try:
        tb = TeraboxDownloader()
        results = tb.get_download_link(url)
        # results: {'download_url': ..., 'filename': ... , 'size': ...}
        files = [{
            "name": results.get("filename", "Unknown file"),
            "sizeMB": _pretty_size_mb(results.get("size")),
            "thumb": None,  # TeraBox public links don't expose thumbs in basic API—skip or reconstruct as needed
            "direct_url": results.get("download_url")
        }]
        return {"status": "ok", "files": files}
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Unable to extract link: {str(e)}",
            "files": []
        }, status_code=500)

def _pretty_size_mb(val):
    # TeraBoxDownloader returns bytes as string or int; convert to MB nicely
    try:
        return round(float(val)/1024/1024, 2)
    except:
        return "?"

