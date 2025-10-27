import customtkinter as ctk
from tkinter import filedialog
from modul import downloader as dw
from pathlib import Path
import sys, threading, subprocess, time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def center_window(self, width, height):
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw // 2) - (width // 2)
        y = (sh // 2) - (height // 2)
        return f"{width}x{height}+{x}+{y}"

class fileType(ctk.CTkFrame):
    def __init__(self, frame):
        super().__init__(frame)

        # file type
        typeTitle = ctk.CTkLabel(self, font=("Arial", 18), text="Pilih Jenis File")
        typeTitle.grid(row=3, column=0, padx=20, sticky="w")

        type = ["Video", "Audio"]
        self.typeSelected = ctk.StringVar(value=type[0])
        self.typeOption = ctk.CTkOptionMenu(self, values=type, variable=self.typeSelected)
        self.typeOption.grid(row=4, column=0, padx=20, pady=25, sticky="w")

        # Format file
        self.formatEntry = ctk.CTkEntry(self, width=160, placeholder_text="Format[Optional] e.g mp4")
        self.formatEntry.grid(row=4, column=1, padx=25, sticky="w")


class filePathFrame(ctk.CTkFrame):
    def __init__(self, frame):
        super().__init__(frame)

        pathlabel = ctk.CTkLabel(self, font=("Arial", 18), text="Path/Folder Download")
        pathlabel.grid(row=0, column=0, pady=15, sticky="w")

        #get root directory
        def rootpath():
            if getattr(sys, "frozen", False):
                return Path(sys.executable).resolve().parent
            return Path(__file__).resolve().parent

        default_path = rootpath() / "Download"

        self.path_entry = ctk.CTkEntry(self, width=600)
        self.path_entry.insert(0, str(default_path))
        self.path_entry.grid(row=1, column=0, padx=5)

        def pathbtn():
            path = filedialog.askdirectory(title="Pilih Folder Tujuan")
            if path:
                self.path_entry.delete(0, "end")
                self.path_entry.insert(0, path)

        pathBtn = ctk.CTkButton(self, text="Pilih Folder", command=pathbtn)
        pathBtn.grid(row=1, column=2)


class splashScreen(ctk.CTk):
    def __init__(self, on_done_callback):
        super().__init__()
        self.on_done_callback = on_done_callback
        self.title("Memeriksas Pembaruan")
        self.geometry(center_window(self, 400, 200))
        self.minsize(width=400, height=200)
        self.resizable(False, False)
        self.iconbitmap("assets/favicon.ico")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Menyiapkan Aplikasi")
        self.label.grid(row=0,column=0, sticky="nsew")

        self.progress = ctk.CTkProgressBar(self, width=250, mode="indeterminate")
        self.progress.grid(row=1,column=0, sticky="nsew")
        self.progress.start()

        threading.Thread(target=self.updateYtDlp, daemon=True).start()


    def updateYtDlp(self):
        try:
            self.label.configure(text="Memeriksa Pembaruan...")
            result = subprocess.run(["yt-dlp", "-U"], capture_output=True, text=True)
            if "yt-dlp is up to date" in result.stdout:
                msg = "Yt-Dlp Sudah Versi Terbaru"
            else:
                msg = "yt-dlp Di Perbarui"
            self.label.configure(text=msg)
        except Exception as e:
            self.label.configure(text=f"Error : {e}")

        time.sleep(1.2)
        self.progress.stop()
        self.after(100, self.closeupdategui)

    def closeupdategui(self):
        try:
            for after_id in self.tk.eval('after info').split():
                self.after_cancel(after_id)
        except Exception:
            pass

        self.destroy()
        self.on_done_callback()


class mainGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Setup
        self.title("Youtube Downloader")
        self.geometry(center_window(self, 800, 600))
        self.minsize(width=700, height=540)
        self.grid_columnconfigure((0), weight=1)
        self.iconbitmap("assets/favicon.ico")

        # Font
        labelFont = ctk.CTkFont(family="Arial", size=18)

        # Label title
        titlelab = ctk.CTkLabel(self, font=("Arial", 28), text="YT Downloader\nBy VrwDev Powered Yt-Dlp")
        titlelab.grid(row=0, column=0, pady=20, padx=20)

        # URL input
        urltitle = ctk.CTkLabel(self, font=labelFont, text="Masukkan Url video")
        self.urlentry = ctk.CTkEntry(self, width=600, placeholder_text="Masukkan URL, e.g. https://youtube.com/watch/")
        urltitle.grid(row=1, column=0, padx=20, sticky="w")
        self.urlentry.grid(row=2, column=0, pady=15, padx=20, sticky="w")

        # file type frame
        self.typeFrame = fileType(self)
        self.typeFrame.grid(row=3, column=0, padx=20, sticky="ew")

        # File path frame
        self.file_Path_Frame = filePathFrame(self)
        self.file_Path_Frame.grid(row=4, column=0, padx=20, pady=30, sticky="ew")

        #downloadBtn
        self.downloadLabel = ctk.CTkLabel(self, text="No Active Download")
        self.downloadLabel.grid(row=6, column=0, padx=20,sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.grid(row=7, column=0, padx=5, pady=5, columnspan=2)
        self.progress_bar.set(0)

        def download(formatd):
            try:
                downloadPath = Path(self.file_Path_Frame.path_entry.get())
                downloadPath.mkdir(parents=True, exist_ok=True)
                
                def progress_callback(d):
                    if d['status'] == 'downloading':
                        percent = float(d.get('_percent_str', '0%').replace('%','')) / 100
                        self.after(0, lambda: self.progress_bar.set(percent))
                        self.after(0, lambda: self.downloadLabel.configure(
                            text=f"{d.get('_percent_str', '0%')} @ {d.get('_speed_str', '0 KiB/s')} (Downloading)"
                        ))
                    elif d['status'] == 'postprocessing':
                        # show postprocesing...
                        self.after(0, lambda: self.downloadLabel.configure(
                            text="Converting with ffmpeg..."
                        ))
                    elif d['status'] == 'finished':
                        self.after(0, lambda: self.progress_bar.set(1.0))
                        self.after(0, lambda: self.downloadLabel.configure(
                            text="Done"
                        ))
                downloader = dw.YTDownloader(progress_callback=progress_callback)
                print("Download")
                
                if self.typeFrame.typeSelected.get() == "Video":
                    downloader.downloadVideo(
                        self.urlentry.get(),
                        Path(self.file_Path_Frame.path_entry.get()),
                        formatd
                    )
                else:
                    downloader.downloadAudio(
                        self.urlentry.get(),
                        Path(self.file_Path_Frame.path_entry.get()),
                        formatd
                    )
            except Exception as e:
                self.downloadLabel.configure(f"Error : {str(e)}")
            finally:
                self.downloadBtn.grid()
                self.typeFrame.formatEntry.insert(0, "")
                self.after(1200, lambda: self.downloadLabel.configure(text="No Active Download"))

        def asyncdownload():
            if self.typeFrame.formatEntry.get() == "" and self.typeFrame.typeOption.get() == "Video":
                self.typeFrame.formatEntry.insert(0, "mp4")
            elif self.typeFrame.formatEntry.get() == "" and self.typeFrame.typeOption.get() == "Audio":
                self.typeFrame.formatEntry.insert(0, "mp3")

            if self.urlentry.get() != "":
                self.downloadBtn.grid_remove()
                self.after(0, lambda: self.downloadLabel.configure(
                            text="Starting Download"
                        ))
                thread = threading.Thread(target=download, args=(self.typeFrame.formatEntry.get(),), daemon=True)
                thread.start()

        self.downloadBtn = ctk.CTkButton(self, text="Download", command=asyncdownload)
        self.downloadBtn.grid(row=5,column=0, pady=0, padx=20, sticky="ew")

def startup():
    def openMainGui():
        main = mainGUI()
        main.mainloop()

    splash = splashScreen(on_done_callback=openMainGui)
    splash.mainloop()

if __name__ == "__main__":
    startup()