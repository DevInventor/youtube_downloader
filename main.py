from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import yt_dlp

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DOWNLOADS_PATH = "downloads"
os.makedirs(DOWNLOADS_PATH, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    files = os.listdir(DOWNLOADS_PATH)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "files": files
    })

@app.post("/api/download")
async def api_download(link: str = Form(...), format: str = Form(...)):
    try:
        ydl_opts = {
            'ffmpeg_location': 'E:/ffmpeg/bin',  # adjust if needed
            'outtmpl': os.path.join(DOWNLOADS_PATH, '%(title)s.%(ext)s'),
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format == 'mp3' else []
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        return JSONResponse({"success": True, "message": "Download completed."})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)})

@app.get("/api/files")
async def list_downloaded_files():
    files = os.listdir(DOWNLOADS_PATH)
    return JSONResponse({"files": files})
