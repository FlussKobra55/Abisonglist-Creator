"""
Dieser Code lädt mithilfe einer csv-Datei die Audio Dateien von jedem SuS herunter,
schneidet es auf die richtige laenge und bennent die Datei richtig.
Vorraussetzungen:
    Python installieren
    pip install yt-dlp
    pip install certifi
    ffmpeg muss installiert sein

Dev: Steinacker Julian, ABI 26
"""

import ssl
import certifi
import yt_dlp
import csv
import unicodedata

missingSuS = []

def readTable():
    table = []
    with open("Liste-Abisongs.csv", "r", encoding="utf-8-sig") as f:
        csvf = csv.reader(f, delimiter=";")
        next(csvf)
        for row in csvf:
            name = row[0] + "_" + row[1]
            name = replaceUmlaute(name)

            songUrl = row[4]
            songLen = row[5]

            if songUrl == "" or songLen == "":
                missingSuS.append(name)
            else:
                table.append([name, songUrl, songLen])
    return table

def replaceUmlaute(name: str):
    replacements = {
        "ä": "ae", "Ä": "Ae",
        "ö": "oe", "Ö": "Oe",
        "ü": "ue", "Ü": "Ue",
        "ß": "ss", "ẞ": "SS",
    }
    for char, replacement in replacements.items():
        name = name.replace(char, replacement)
    return unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode("ascii")

def convMin2Sec(min: str):
    min = [int(i) for i in min.split(":")]
    sec = min[1]
    sec += int(min[0]*60)
    return sec

def downloadAudio(url: str, start: int, name: str):
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())

    ydl_opts = {
        "format": "bestaudio/best",
        "download_ranges": yt_dlp.utils.download_range_func(None, [(start, start+30)]),
        "force_keyframes_at_cuts": True,
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": f"Abisongs/{name}.%(ext)s",
        #SSL Fixes
        "nocheckcertificate": False,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
        "ssl_certificate": certifi.where(),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    for i in readTable():
        downloadAudio(i[1], convMin2Sec(i[2]), i[0])
        print(i[0], "ist heruntergeladen")

    print(f"Es fehlt: {', '.join([*missingSuS])}")