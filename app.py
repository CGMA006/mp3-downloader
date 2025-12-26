import subprocess
import os
from flask import Flask, jsonify, request, send_from_directory, render_template

app = Flask(__name__)

AUDIO_QUALITY = "192k"
YTDLPATH = r"C:\Users\pranj\AppData\Roaming\Python\Python313\Scripts\yt-dlp.exe"
OUTPUT_DIR = r"D:\downloads"
OUTPUT_TEMPLATE = os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s")


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        #  get the filename yt-dlp will create
        result = subprocess.run(
            [YTDLPATH,
             "--get-filename",
             "-x",
             "--audio-format", "mp3",
             "--audio-quality", AUDIO_QUALITY,
             "-o", OUTPUT_TEMPLATE,
             url],
            capture_output=True,
            text=True
        )

        filename = os.path.basename(result.stdout.strip())  # just the file name, not full path

        # Step 2: download the file
        subprocess.run(
            [YTDLPATH,
             "-x",
             "--audio-format", "mp3",
             "--audio-quality", AUDIO_QUALITY,
             "-o", OUTPUT_TEMPLATE,
             url],
            check=True
        )

        return jsonify({"mp3_url": f"/files/{filename}"})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Download failed", "details": str(e)}), 500


@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
