#!/usr/bin/env python3
"""
img_to_base64_gui.py - GUI for converting images to Base64.

Requires: Python 3.8+ (tkinter is included in the standard library)
Optional: pyperclip  (pip install pyperclip)  — enables clipboard copy
"""

import base64
import mimetypes
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# ── optional clipboard support ──────────────────────────────────────────────
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".svg", ".ico", ".tiff", ".tif",
}

# ── conversion logic ─────────────────────────────────────────────────────────
def image_to_base64(image_path: Path, wrap: int = 0, data_uri: bool = False) -> str:
    if not image_path.exists():
        raise FileNotFoundError(f"File not found: {image_path}")
    if not image_path.is_file():
        raise ValueError(f"Not a file: {image_path}")

    with open(image_path, "rb") as f:
        raw = f.read()

    encoded = base64.b64encode(raw).decode("utf-8")

    if data_uri:
        mime_type, _ = mimetypes.guess_type(str(image_path))
        mime_type = mime_type or "image/png"
        return f"data:{mime_type};base64,{encoded}"

    if wrap > 0:
        encoded = "\n".join(
            encoded[i:i + wrap] for i in range(0, len(encoded), wrap)
        )

    return encoded


# ── palette & fonts ──────────────────────────────────────────────────────────
BG          = "#0f0f0f"
PANEL       = "#1a1a1a"
BORDER      = "#2e2e2e"
ACCENT      = "#e8c84a"   # amber / industrial yellow
ACCENT_DIM  = "#a8912e"
TEXT        = "#e8e8e0"
TEXT_DIM    = "#6b6b60"
MONO        = ("Courier New", 9)
LABEL_FONT  = ("Georgia", 9, "italic")
TITLE_FONT  = ("Georgia", 20, "bold")
BTN_FONT    = ("Courier New", 9, "bold")


# ── main app ─────────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("img → base64")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(620, 560)

        self._image_path: Path | None = None
        self._result: str = ""

        self._build_ui()
        self._center()

    # ── layout ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = self

        # ── title bar ────────────────────────────────────────────────────────
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 4))

        tk.Label(header, text="img", font=TITLE_FONT,
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Label(header, text=" →", font=TITLE_FONT,
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(header, text=" base64", font=TITLE_FONT,
                 bg=BG, fg=TEXT).pack(side="left")

        tk.Label(root, text="drag & drop or browse an image file",
                 font=LABEL_FONT, bg=BG, fg=TEXT_DIM).pack(anchor="w", padx=26)

        self._sep(root)

        # ── file picker ───────────────────────────────────────────────────────
        file_row = tk.Frame(root, bg=BG)
        file_row.pack(fill="x", padx=24, pady=(10, 0))

        self.path_var = tk.StringVar(value="no file selected")
        path_entry = tk.Entry(
            file_row, textvariable=self.path_var,
            font=MONO, bg=PANEL, fg=TEXT_DIM,
            insertbackground=ACCENT, relief="flat",
            bd=0, highlightthickness=1,
            highlightbackground=BORDER, highlightcolor=ACCENT,
            state="readonly", readonlybackground=PANEL,
        )
        path_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

        self._btn(file_row, "browse", self._browse).pack(side="left")

        self._sep(root)

        # ── options ───────────────────────────────────────────────────────────
        opt_frame = tk.Frame(root, bg=BG)
        opt_frame.pack(fill="x", padx=24, pady=8)

        tk.Label(opt_frame, text="options", font=LABEL_FONT,
                 bg=BG, fg=TEXT_DIM).grid(row=0, column=0, sticky="w",
                                           columnspan=4, pady=(0, 6))

        # data URI toggle
        self.data_uri_var = tk.BooleanVar(value=False)
        self._checkbox(opt_frame, "data URI output", self.data_uri_var,
                       row=1, col=0)

        # wrap toggle + entry
        self.wrap_var = tk.BooleanVar(value=False)
        self._checkbox(opt_frame, "wrap at", self.wrap_var, row=1, col=2,
                       command=self._toggle_wrap)

        self.wrap_n = tk.IntVar(value=76)
        self.wrap_entry = tk.Spinbox(
            opt_frame, from_=10, to=999, textvariable=self.wrap_n,
            width=5, font=MONO, bg=PANEL, fg=TEXT,
            buttonbackground=BORDER, relief="flat",
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, state="disabled",
        )
        self.wrap_entry.grid(row=1, column=3, padx=(4, 0))
        tk.Label(opt_frame, text="chars", font=LABEL_FONT,
                 bg=BG, fg=TEXT_DIM).grid(row=1, column=4, padx=(4, 0))

        opt_frame.columnconfigure(1, minsize=20)
        opt_frame.columnconfigure(5, weight=1)

        self._sep(root)

        # ── action buttons ────────────────────────────────────────────────────
        btn_row = tk.Frame(root, bg=BG)
        btn_row.pack(fill="x", padx=24, pady=10)

        self._btn(btn_row, "convert", self._convert,
                  primary=True).pack(side="left", padx=(0, 8))
        self._btn(btn_row, "save output", self._save).pack(side="left", padx=(0, 8))

        if HAS_PYPERCLIP:
            self._btn(btn_row, "copy", self._copy).pack(side="left", padx=(0, 8))
        else:
            tk.Label(btn_row, text="tip: pip install pyperclip for clipboard copy",
                     font=LABEL_FONT, bg=BG, fg=TEXT_DIM).pack(side="left")

        self._btn(btn_row, "clear", self._clear).pack(side="right")

        # ── output area ───────────────────────────────────────────────────────
        out_label_row = tk.Frame(root, bg=BG)
        out_label_row.pack(fill="x", padx=24, pady=(4, 0))
        tk.Label(out_label_row, text="output", font=LABEL_FONT,
                 bg=BG, fg=TEXT_DIM).pack(side="left")
        self.stats_label = tk.Label(out_label_row, text="", font=LABEL_FONT,
                                    bg=BG, fg=ACCENT)
        self.stats_label.pack(side="left", padx=(12, 0))

        out_frame = tk.Frame(root, bg=BORDER, bd=0, highlightthickness=0)
        out_frame.pack(fill="both", expand=True, padx=24, pady=(4, 20))

        self.output = tk.Text(
            out_frame, font=MONO, bg=PANEL, fg=TEXT,
            insertbackground=ACCENT, relief="flat", bd=10,
            wrap="word", state="disabled",
        )
        self.output.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(out_frame, command=self.output.yview,
                                 bg=PANEL, troughcolor=PANEL,
                                 activebackground=ACCENT, width=10,
                                 relief="flat", bd=0)
        scrollbar.pack(side="right", fill="y")
        self.output.config(yscrollcommand=scrollbar.set)

        # ── drag & drop (best-effort) ─────────────────────────────────────────
        try:
            self.drop_target_register("DND_Files")   # type: ignore[attr-defined]
            self.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
        except Exception:
            pass  # tkinterdnd2 not installed; silently skip

    # ── helpers ───────────────────────────────────────────────────────────────
    def _sep(self, parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=24, pady=4)

    def _btn(self, parent, text: str, cmd, primary=False):
        bg = ACCENT if primary else PANEL
        fg = BG if primary else TEXT
        abg = ACCENT_DIM if primary else BORDER
        b = tk.Button(
            parent, text=text.upper(), command=cmd,
            font=BTN_FONT, bg=bg, fg=fg, activebackground=abg,
            activeforeground=fg, relief="flat", bd=0,
            padx=14, pady=6, cursor="hand2",
        )
        b.bind("<Enter>", lambda _: b.config(bg=abg))
        b.bind("<Leave>", lambda _: b.config(bg=bg))
        return b

    def _checkbox(self, parent, text, var, row, col, command=None):
        cb = tk.Checkbutton(
            parent, text=text, variable=var,
            font=LABEL_FONT, bg=BG, fg=TEXT,
            selectcolor=PANEL, activebackground=BG,
            activeforeground=ACCENT, cursor="hand2",
            command=command,
        )
        cb.grid(row=row, column=col, sticky="w")

    def _center(self):
        self.update_idletasks()
        w, h = 680, 600
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//2}")

    # ── callbacks ─────────────────────────────────────────────────────────────
    def _toggle_wrap(self):
        state = "normal" if self.wrap_var.get() else "disabled"
        self.wrap_entry.config(state=state)

    def _browse(self):
        exts = " ".join(f"*{e}" for e in sorted(SUPPORTED_EXTENSIONS))
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", exts), ("All files", "*.*")],
        )
        if path:
            self._set_path(Path(path))

    def _on_drop(self, event):
        path = event.data.strip().strip("{}")
        self._set_path(Path(path))

    def _set_path(self, path: Path):
        self._image_path = path
        self.path_var.set(str(path))

    def _convert(self):
        if not self._image_path:
            messagebox.showwarning("No file", "Please select an image first.")
            return
        try:
            result = image_to_base64(
                self._image_path,
                wrap=self.wrap_n.get() if self.wrap_var.get() else 0,
                data_uri=self.data_uri_var.get(),
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._result = result
        self._set_output(result)

        chars = len(result)
        kb = len(result.encode()) / 1024
        self.stats_label.config(text=f"{chars:,} chars · {kb:.1f} KB")

    def _set_output(self, text: str):
        self.output.config(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.config(state="disabled")

    def _save(self):
        if not self._result:
            messagebox.showwarning("Nothing to save", "Convert an image first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save output",
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")],
        )
        if path:
            Path(path).write_text(self._result, encoding="utf-8")
            messagebox.showinfo("Saved", f"Output saved to:\n{path}")

    def _copy(self):
        if not self._result:
            messagebox.showwarning("Nothing to copy", "Convert an image first.")
            return
        pyperclip.copy(self._result)
        messagebox.showinfo("Copied", "Result copied to clipboard.")

    def _clear(self):
        self._image_path = None
        self._result = ""
        self.path_var.set("no file selected")
        self.stats_label.config(text="")
        self._set_output("")


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # If a path is passed as an argument, pre-load it
    app = App()
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if p.is_file():
            app._set_path(p)
    app.mainloop()
