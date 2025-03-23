import sys
import os
import yt_dlp
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QProgressBar, QFileDialog, QHBoxLayout, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
from plyer import notification

class DownloadThread(QThread):
    update_progress = pyqtSignal(int)
    download_finished = pyqtSignal()
    paused = False

    def __init__(self, urls, folder, format_choice):
        super().__init__()
        self.urls = urls
        self.folder = folder
        self.format_choice = format_choice

    def run(self):
        for url in self.urls:
            playlist_name = self.get_playlist_name(url)
            folder_path = os.path.join(self.folder, playlist_name) if playlist_name else self.folder
            os.makedirs(folder_path, exist_ok=True)
            self.download_video(url, folder_path)

        self.download_finished.emit()

    def get_playlist_name(self, url):
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict.get('title', 'No Title')

    def download_video(self, url, folder):
        ydl_opts = {
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'format': self.format_choice,
            'progress_hooks': [self.progress_hook],
            'verbose': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                notification.notify(title="İndirme Hatası", message=f"Video indirilirken hata oluştu: {e}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                while self.paused:
                    self.msleep(100)
                progress = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
                self.update_progress.emit(progress)

    def pause_download(self):
        self.paused = True

    def resume_download(self):
        self.paused = False

class VideoDownloader(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Video İndirme Aracı")
        self.setGeometry(300, 300, 750, 600)
        self.setStyleSheet("background-color: #2e2e2e; color: white; font-family: Arial, sans-serif; font-size: 14px;")
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title_label = QLabel("YouTube Video İndirme")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffcc00; text-align: center;")
        layout.addWidget(self.title_label)

        self.url_label = QLabel("Video URL'lerini Girin (Satır satır):")
        layout.addWidget(self.url_label)

        self.url_text = QTextEdit(self)
        self.url_text.setPlaceholderText("Video URL'lerini buraya yapıştırın...")
        layout.addWidget(self.url_text)

        self.folder_label = QLabel("İndirilecek Klasörü Seçin:")
        layout.addWidget(self.folder_label)

        self.folder_button = QPushButton("Klasör Seç", self)
        self.folder_button.setStyleSheet("""background-color: #ffcc00; color: black; font-weight: bold; padding: 10px; border-radius: 5px;""")
        self.folder_button.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_button)

        self.folder_line = QLineEdit(self)
        self.folder_line.setReadOnly(True)
        layout.addWidget(self.folder_line)

        # Format Seçme (MP4 ve MKV seçenekleri)
        self.format_label = QLabel("Video Formatını Seçin:")
        layout.addWidget(self.format_label)

        self.format_combo = QComboBox(self)
        self.format_combo.addItem("MP4")
        self.format_combo.addItem("MKV")
        layout.addWidget(self.format_combo)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        self.download_button = QPushButton("İndirmeyi Başlat", self)
        self.download_button.setStyleSheet("""background-color: #28a745; color: white; font-weight: bold; padding: 12px; border-radius: 5px;""")
        self.download_button.clicked.connect(self.start_download)
        layout.addWidget(self.download_button)

        self.pause_button = QPushButton("Duraklat", self)
        self.pause_button.setStyleSheet("""background-color: #dc3545; color: white; font-weight: bold; padding: 12px; border-radius: 5px;""")
        self.pause_button.clicked.connect(self.pause_download)
        layout.addWidget(self.pause_button)

        self.resume_button = QPushButton("Devam Et", self)
        self.resume_button.setStyleSheet("""background-color: #007bff; color: white; font-weight: bold; padding: 12px; border-radius: 5px;""")
        self.resume_button.clicked.connect(self.resume_download)
        layout.addWidget(self.resume_button)

        # Geliştirici Bilgileri Paneli
        dev_layout = QHBoxLayout()
        dev_label = QLabel("👨‍💻 Geliştirici: Caner Ergün")
        dev_label.setStyleSheet("color: #ffcc00; font-size: 14px; font-weight: bold;")
        dev_layout.addWidget(dev_label)

        # LinkedIn Butonu
        linkedin_button = QPushButton("LinkedIn")
        linkedin_button.setStyleSheet("""background-color: #0A66C2; color: white; border-radius: 5px; padding: 5px;""")
        linkedin_button.clicked.connect(lambda: self.open_url("https://www.linkedin.com/in/devseu/"))
        dev_layout.addWidget(linkedin_button)

        # GitHub Butonu
        github_button = QPushButton("GitHub")
        github_button.setStyleSheet("""background-color: #333; color: white; border-radius: 5px; padding: 5px;""")
        github_button.clicked.connect(lambda: self.open_url("https://github.com/canerergun"))
        dev_layout.addWidget(github_button)

        # Instagram Butonu
        instagram_button = QPushButton("Instagram")
        instagram_button.setStyleSheet("""background-color: #C13584; color: white; border-radius: 5px; padding: 5px;""")
        instagram_button.clicked.connect(lambda: self.open_url("https://www.instagram.com/devseu"))
        dev_layout.addWidget(instagram_button)

        # Twitch Butonu
        twitch_button = QPushButton("Twitch")
        twitch_button.setStyleSheet("""background-color: #9146FF; color: white; border-radius: 5px; padding: 5px;""")
        twitch_button.clicked.connect(lambda: self.open_url("https://www.twitch.tv/devseu"))
        dev_layout.addWidget(twitch_button)

        layout.addLayout(dev_layout)

        self.thread = None
        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç", "")
        if folder:
            self.folder_line.setText(folder)

    def start_download(self):
        urls = self.url_text.toPlainText().strip().splitlines()
        folder = self.folder_line.text()
        format_choice = self.get_selected_format()

        if not urls or not folder:
            notification.notify(title="Hata", message="Lütfen video URL'lerini ve klasörü girin.")
            return

        self.thread = DownloadThread(urls, folder, format_choice)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.download_finished.connect(self.download_finished)
        self.thread.start()

    def get_selected_format(self):
        format_choice = self.format_combo.currentText()
        # Formatları kontrol et
        available_formats = self.get_available_formats()

        if format_choice.lower() in available_formats:
            if format_choice == "MKV":
                return 'bestvideo[ext=mkv]+bestaudio[ext=m4a]/mkv'
            else:
                return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'
        else:
            # Eğer seçilen format mevcut değilse, MP4'ü tercih et
            notification.notify(title="Format Bulunamadı", message="Seçilen format mevcut değil. MP4 formatı indiriliyor.")
            return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'

    def get_available_formats(self):
        # Video formatlarını kontrol et
        ydl_opts = {'quiet': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = self.url_text.toPlainText().strip().splitlines()[0]  # İlk URL'yi al
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            return [fmt['ext'] for fmt in formats]

    def pause_download(self):
        if self.thread:
            self.thread.pause_download()

    def resume_download(self):
        if self.thread:
            self.thread.resume_download()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self):
        notification.notify(title="İndirme Tamamlandı", message="Tüm videolar başarıyla indirildi!")

    def open_url(self, url):
        webbrowser.open(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoDownloader()
    window.show()
    sys.exit(app.exec_())
