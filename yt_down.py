import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("500x400")

        # YouTube URL Label and Entry / Ярлык и запись URL-адреса YouTube
        self.url_label = tk.Label(root, text="Enter YouTube URL:")
        self.url_label.pack(pady=10)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Dropdown for video formats / Раскрывающийся список видеоформатов
        self.format_label = tk.Label(root, text="Select format (Video + Audio or Video-only):")
        self.format_label.pack(pady=10)

        self.format_combobox = ttk.Combobox(root, state="readonly", width=50)
        self.format_combobox.pack(pady=5)

        # Button to fetch video formats / Кнопка для загрузки видеоформатов
        self.fetch_button = tk.Button(root, text="Fetch Formats", command=self.fetch_formats)
        self.fetch_button.pack(pady=10)

        # Label to show percentage of downloading / Ярлык, показывающий процент загрузки
        self.percentage_label = tk.Label(root, text="Download Progress: 0%")
        self.percentage_label.pack(pady=10)

        # Button to download the video / Кнопка для скачивания видео
        self.download_button = tk.Button(root, text="Download Video", state="disabled", command=self.download_video)
        self.download_button.pack(pady=10)

        self.formats = []  # To store format options / Чтобы сохранить параметры формата

    def fetch_formats(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        try:
            # Extract video info and formats using yt-dlp / Извлеките информацию и форматы видео с помощью yt-dlp
            ydl_opts = {}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            self.formats = info.get('formats', [])
            if not self.formats:
                messagebox.showerror("Error", "No available formats for this video.")
                return

            # Populate combobox with available formats (including video-only for higher resolutions)
            # / Заполните поле со списком доступными форматами (включая только видео для более высоких разрешений).
            format_options = []
            for f in self.formats:
                resolution = f.get('format_note', 'Unknown resolution')
                audio_video_status = 'Video + Audio' if f.get('vcodec') != 'none' and f.get(
                    'acodec') != 'none' else 'Video-only'
                format_options.append(f"Resolution: {resolution}, ID: {f['format_id']}, {audio_video_status}")

            self.format_combobox['values'] = format_options
            self.format_combobox.current(0)
            self.download_button.config(state="normal")  # Enable download button

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def progress_hook(self, d):
        """Handle download progress. / Управлять ходом загрузки."""
        if d['status'] == 'downloading':
            # Update percentage label / Обновить метку процента
            percentage = d.get('percent', 0)
            self.percentage_label.config(text=f"Download Progress: {percentage:.2f}%")
            self.root.update_idletasks()  # Update the UI in real-time / Обновляйте пользовательский интерфейс в режиме реального времени

        elif d['status'] == 'finished':
            # Notify when the download is finished / Уведомить об окончании загрузки
            self.percentage_label.config(text="Download Progress: 100%")
            messagebox.showinfo("Success", "Download complete!")
            self.download_button.config(state="normal")  # Re-enable the download button / Снова включите кнопку загрузки

    def download_video(self):
        selected_format_index = self.format_combobox.current()
        chosen_format = self.formats[selected_format_index]
        chosen_format_id = chosen_format['format_id']

        url = self.url_entry.get()
        self.download_button.config(state="disabled")  # Disable the button during download / Отключить кнопку во время загрузки

        ydl_opts = {
            'format': f'{chosen_format_id}+bestaudio/best',  # Download video + best audio stream separately / Скачать видео + лучший аудиопоток отдельно
            'outtmpl': '%(title)s.%(ext)s',  # Save with video title as the filename / Сохранить с названием видео в качестве имени файла.
            'merge_output_format': 'mp4',  # Ensure video and audio are merged into MP4 / Убедитесь, что видео и аудио объединены в MP4.
            'progress_hooks': [self.progress_hook],  # Track download progress / Отслеживайте ход загрузки
        }

        try:
            self.percentage_label.config(text="Download Progress: 0%")  # Reset percentage to 0% / Перезагрузить прогресс на 0%
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during download: {e}")
            self.download_button.config(state="normal")  # Re-enable the download button / Включить заново кнопку загрузки


root = tk.Tk()

app = YouTubeDownloaderApp(root)

root.mainloop()