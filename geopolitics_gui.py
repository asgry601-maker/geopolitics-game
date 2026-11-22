"""Windowed (Tkinter) launcher for geopolitics.py - avoids Windows 7 console font/codepage problems."""
import codecs
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
import tkinter.scrolledtext as st


def base_dir():
    return os.path.dirname(os.path.abspath(__file__))


class App(object):
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.dec = codecs.getincrementaldecoder("utf-8")("replace")
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        cmd = [sys.executable, os.path.join(base_dir(), "geopolitics.py"), "play"]
        self.proc = subprocess.Popen(
            cmd, cwd=base_dir(), env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, bufsize=0,
        )
        root.title("\u0698\u0626\u0648\u067e\u0644\u06cc\u062a\u06cc\u06a9: \u0631\u0642\u0627\u0628\u062a \u0642\u062f\u0631\u062a\u200c\u0647\u0627")
        root.geometry("940x640")
        self.text = st.ScrolledText(root, font=("Tahoma", 11), state="disabled",
                                    wrap="word", bg="#12161c", fg="#eaeaea")
        self.text.pack(fill="both", expand=True)
        bottom = tk.Frame(root)
        bottom.pack(fill="x")
        self.entry = tk.Entry(bottom, font=("Tahoma", 11))
        self.entry.pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self.entry.bind("<Return>", self.send)
        self.entry.focus()
        tk.Button(bottom, text="\u0627\u0631\u0633\u0627\u0644 (Enter)", width=14,
                  command=self.send).pack(side="right", padx=6, pady=6)
        threading.Thread(target=self.reader, daemon=True).start()
        root.after(80, self.pump)
        root.protocol("WM_DELETE_WINDOW", self.close)

    def reader(self):
        try:
            while True:
                b = self.proc.stdout.read(1)
                if not b:
                    break
                self.q.put(b)
        except Exception:
            pass
        self.q.put(None)

    def pump(self):
        try:
            chunks = []
            while True:
                b = self.q.get_nowait()
                if b is None:
                    self.show("\n\n[\u26a0 \u0628\u0627\u0632\u06cc \u0628\u0633\u062a\u0647 \u0634\u062f \u2014 \u0628\u0631\u0627\u06cc \u0627\u062f\u0627\u0645\u0647\u060c \u062f\u0648\u0628\u0627\u0631\u0647 play_window.bat \u0631\u0627 \u0627\u062c\u0631\u0627 \u06a9\u0646]")
                    self.proc.wait()
                    return
                chunks.append(b)
            if chunks:
                self.show(self.dec.decode(b"".join(chunks)))
        except queue.Empty:
            pass
        self.root.after(80, self.pump)

    def show(self, s):
        if not s:
            return
        self.text.configure(state="normal")
        self.text.insert("end", s)
        self.text.see("end")
        self.text.configure(state="disabled")

    def send(self, event=None):
        s = self.entry.get()
        self.entry.delete(0, "end")
        if self.proc.poll() is not None:
            return
        try:
            self.proc.stdin.write((s + "\n").encode("utf-8"))
            self.proc.stdin.flush()
        except Exception:
            pass

    def close(self):
        try:
            if self.proc.poll() is None:
                self.proc.terminate()
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
