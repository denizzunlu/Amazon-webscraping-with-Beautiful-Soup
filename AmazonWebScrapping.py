import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup
import requests

class Worker(QThread):
    finished = pyqtSignal()
    data_ready = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        url = "https://www.amazon.com.tr/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, "html.parser")
            urunler = soup.find_all('div', attrs={'id': 'gridItemRoot', 'class': 'a-column a-span12 a-text-center _cDEzb_grid-column_2hIsc'})

            headers = {"User-Agent": "Kendi user agent'ınızı giriniz."} ### KENDİ USER-AGENT'INIZI GİRİNİZ.

            for urun in urunler:
                urun_linki = urun.find('a', class_='a-link-normal')
                if urun_linki:
                    link = urun_linki.get('href')
                    tam_link = "https://www.amazon.com.tr" + link
                    self.data_ready.emit("Ürün Linki: " + tam_link)

                    detay = requests.get(tam_link, headers=headers, timeout=10)
                    detay.raise_for_status()
                    detay_soup = BeautifulSoup(detay.content, "html.parser")

                    try:
                        urun_hakkinda = detay_soup.find("div", {"id": "feature-bullets"}).find_all("span", class_="a-list-item")
                        self.data_ready.emit("Ürün Hakkında Bilgiler:")
                        for bilgi in urun_hakkinda:
                            self.data_ready.emit("  - " + bilgi.text.strip())
                    except AttributeError:
                        self.data_ready.emit("Ürün hakkında bilgi bulunamadı.")

                    fiyat_span = detay_soup.find("span", class_="a-price")
                    if fiyat_span:
                        fiyat = fiyat_span.find("span", class_="a-offscreen").text.strip()
                        self.data_ready.emit("Ürün Fiyatı: " + fiyat)
                    else:
                        self.data_ready.emit("Ürün fiyatı bulunamadı.")

                    self.data_ready.emit("\n" + "="*50 + "\n")
        except requests.RequestException as e:
            self.data_ready.emit("Bir hata oluştu: " + str(e))

        self.finished.emit()

class AmazonScrapingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Amazon Ürün Scraping Uygulaması')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        label_giris = QLabel("Amazon Ürün Scraping Uygulamasına Hoş Geldiniz!")
        label_giris.setStyleSheet("font-size: 20px; color: #333; margin-bottom: 20px;")
        layout.addWidget(label_giris)

        label_aciklama = QLabel("Bu uygulama, Amazon'dan en çok satan elektronik ürünlerin bilgilerini çeker.")
        label_aciklama.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 20px;")
        layout.addWidget(label_aciklama)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: #f0f0f0; color: #333; font-size: 14px; border: 1px solid #ccc; border-radius: 5px; padding: 10px;")
        layout.addWidget(self.text_edit)

        button_scrape = QPushButton('Ürünleri Çek')
        button_scrape.setStyleSheet("font-size: 16px; background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px;")
        button_scrape.clicked.connect(self.start_worker)
        layout.addWidget(button_scrape)

        button_kapat = QPushButton('Kapat')
        button_kapat.setStyleSheet("font-size: 16px; background-color: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 5px;")
        button_kapat.clicked.connect(self.close)
        layout.addWidget(button_kapat)

        self.worker = Worker()
        self.worker.data_ready.connect(self.update_text_edit)
        self.worker.finished.connect(self.worker_finished)

    def start_worker(self):
        self.text_edit.clear()
        self.worker.start()

    def update_text_edit(self, text):
        self.text_edit.append(text)

    def worker_finished(self):
        pass

    def closeEvent(self, event):
        self.worker.terminate()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AmazonScrapingApp()
    window.show()
    sys.exit(app.exec_())
