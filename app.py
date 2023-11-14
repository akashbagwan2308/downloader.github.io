from flask import Flask, render_template, request,Response
from pytube import YouTube
from tqdm import tqdm
from stqdm import stqdm
from time import sleep
import time
import youtube_dl
import os

app = Flask(__name__)


def download_video(video_url, output_path):
    try:
        # Create a YouTube object
        youtube = YouTube(video_url)

        # Get the highest resolution stream available
        video_stream = youtube.streams.get_highest_resolution()

        total_size = video_stream.filesize

        # Define the progress bar
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading')
        for i in range(total_size):
            progress_bar.update()

        # Download the video to the specified output path
        video_stream.download(output_path)

        return True, f"Video downloaded successfully to {output_path}"

    except Exception as e:
        return False, f"An error occurred: {e}"

def download_playlist(vid_list, output_path_playlist):
    if not os.path.exists(output_path_playlist):
        os.makedirs(output_path_playlist)
    for video_link in stqdm(vid_list, desc='Downloading Playlist'):
        success, message = download_video(video_link, output_path_playlist)
        if not success:
            break
    return True, f"Playlist downloaded successfully to {output_path_playlist}"

def get_playlist_video_links(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        video_links = []

        if 'entries' in result:
            for entry in result['entries']:
                video_links.append(entry['url'])

        return video_links

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['video_url']
    output_path = request.form.get('output_path')

    success, message = download_video(video_url, output_path)

    return render_template('result.html', success=success, message=message)


@app.route('/download_playlist', methods=['POST'])
def download_playlist_route():
    playlist_url = request.form['playlist_url']
    output_path_playlist = request.form.get('output_path_playlist')

    video_links = get_playlist_video_links(playlist_url)
    vid_list = []

    if video_links:
        for link in video_links:
            vid_list.append("https://www.youtube.com/watch?v=" + link)
    else:
        return render_template('result.html', success=False, message="Unable to fetch video links. Please check the playlist URL.")

    success, message = download_playlist(vid_list, output_path_playlist)

    return render_template('result.html', success=success, message=message)

if __name__ == "__main__":
    app.run(debug=True)
