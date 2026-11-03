#!/usr/bin/env python3
"""SHADOW CLIENT launcher - lightweight Tkinter front-end for PortableMC."""
from __future__ import annotations

import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_NAME = "SHADOW CLIENT"
MC_VERSION = "1.21.1"
PORTABLEMC_REPO = "theorzr/portablemc"
MODRINTH_PROJECTS = [
    ("fabric-api", "Fabric API"),
    ("sodium", "Sodium"),
    ("lithium", "Lithium"),
    ("ferrite-core", "FerriteCore"),
    ("immediatelyfast", "ImmediatelyFast"),
    ("entityculling", "Entity Culling"),
]


def app_data_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home() / ".config")
    path = Path(base) / "ShaDowTixi" / "ShadowClient"
    path.mkdir(parents=True, exist_ok=True)
    return path


APP_DIR = app_data_dir()
GAME_DIR = APP_DIR / "game"
BACKEND_DIR = APP_DIR / "backend"
CONFIG_FILE = APP_DIR / "settings.json"
LOG_FILE = APP_DIR / "shadowclient.log"


def load_config() -> dict:
    defaults = {"username": "ShaDowTixi", "ram_mb": 1536, "install_optimizations": True, "server": "", "port": 25565}
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                defaults.update(data)
    except Exception:
        pass
    return defaults


def save_config(data: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "ShadowClient/0.1 (personal launcher)"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, destination: Path, progress=None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ShadowClient/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response, destination.open("wb") as out:
        total = int(response.headers.get("Content-Length", "0") or 0)
        done = 0
        while True:
            chunk = response.read(256 * 1024)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if progress and total:
                progress(done, total)


def find_portablemc() -> Path | None:
    for p in BACKEND_DIR.rglob("portablemc.exe"):
        return p
    return None


def ensure_portablemc(log) -> Path:
    existing = find_portablemc()
    if existing:
        return existing
    log("Downloading official PortableMC Windows x64 backend...")
    release = http_json(f"https://api.github.com/repos/{PORTABLEMC_REPO}/releases/latest")
    asset = None
    for item in release.get("assets", []):
        name = item.get("name", "")
        if name.endswith("windows-x86_64-msvc.zip"):
            asset = item
            break
    if not asset:
        raise RuntimeError("Official PortableMC Windows x64 release asset was not found.")
    archive = BACKEND_DIR / asset["name"]
    BACKEND_DIR.mkdir(parents=True, exist_ok=True)
    download_file(asset["browser_download_url"], archive)
    digest = asset.get("digest")
    if digest and digest.startswith("sha256:"):
        import hashlib
        hasher = hashlib.sha256()
        with archive.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                hasher.update(chunk)
        if hasher.hexdigest().lower() != digest.split(":", 1)[1].lower():
            archive.unlink(missing_ok=True)
            raise RuntimeError("PortableMC download SHA-256 check failed. The file was discarded.")
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            target = (BACKEND_DIR / member.filename).resolve()
            if not str(target).startswith(str(BACKEND_DIR.resolve()) + os.sep):
                raise RuntimeError("Unsafe path found in PortableMC archive; extraction stopped.")
        zf.extractall(BACKEND_DIR)
    archive.unlink(missing_ok=True)
    result = find_portablemc()
    if not result:
        raise RuntimeError("PortableMC archive extracted, but portablemc.exe was not found.")
    log("PortableMC backend ready.")
    return result


def install_modrinth_mods(log) -> None:
    mods_dir = GAME_DIR / "mods"
    mods_dir.mkdir(parents=True, exist_ok=True)
    for slug, display in MODRINTH_PROJECTS:
        log(f"Checking {display} for Minecraft {MC_VERSION}...")
        query = urllib.parse.urlencode({
            "game_versions": json.dumps([MC_VERSION]),
            "loaders": json.dumps(["fabric"]),
        })
        versions = http_json(f"https://api.modrinth.com/v2/project/{slug}/version?{query}")
        if not versions:
            log(f"No compatible release found for {display}; skipped.")
            continue
        # Prefer stable releases, then newest publication date.
        versions.sort(key=lambda v: (v.get("version_type") == "release", v.get("date_published", "")), reverse=True)
        version = versions[0]
        files = version.get("files", [])
        if not files:
            log(f"No downloadable file listed for {display}; skipped.")
            continue
        file = next((f for f in files if f.get("primary")), files[0])
        filename = Path(file.get("filename", f"{slug}.jar")).name
        target = mods_dir / filename
        if target.exists() and target.stat().st_size > 0:
            log(f"{display} already installed.")
            continue
        download_file(file["url"], target)
        log(f"Installed {display} ({version.get('version_number', 'compatible release')}).")


class ShadowLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SHADOW CLIENT | ShaDowTixi")
        self.root.geometry("820x620")
        self.root.minsize(760, 560)
        self.root.configure(bg="#101014")
        self.events: queue.Queue = queue.Queue()
        self.worker = None
        self.backend_process = None
        self.config = load_config()
        self._build_ui()
        self.root.after(120, self._drain_events)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TCombobox", fieldbackground="#23232b", background="#23232b", foreground="#f4f4f6")
        style.configure("Horizontal.TScale", background="#101014", troughcolor="#2b2433")

        header = tk.Frame(self.root, bg="#15151d", height=112)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="SHADOW", bg="#15151d", fg="#f4f4f6", font=("Segoe UI", 28, "bold")).pack(anchor="w", padx=28, pady=(18, 0))
        tk.Label(header, text="CLIENT  •  PERSONAL EDITION  •  by ShaDowTixi", bg="#15151d", fg="#bd4667", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=30, pady=(0, 12))

        content = tk.Frame(self.root, bg="#101014")
        content.pack(fill="both", expand=True, padx=24, pady=18)
        left = tk.Frame(content, bg="#191920", highlightbackground="#2c2631", highlightthickness=1)
        left.pack(side="left", fill="y", padx=(0, 14))
        left.configure(width=290)
        left.pack_propagate(False)

        tk.Label(left, text="GAME PROFILE", bg="#191920", fg="#c8c3d1", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=18, pady=(20, 7))
        tk.Label(left, text="Minecraft Java 1.21.1", bg="#191920", fg="white", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=18)
        tk.Label(left, text="Fabric Loader • auto-managed", bg="#191920", fg="#9a95a2", font=("Segoe UI", 9)).pack(anchor="w", padx=18, pady=(2, 18))

        tk.Label(left, text="OFFLINE PROFILE NAME", bg="#191920", fg="#c8c3d1", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18)
        self.username = tk.StringVar(value=str(self.config.get("username", "ShaDowTixi")))
        tk.Entry(left, textvariable=self.username, bg="#262631", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 11)).pack(fill="x", padx=18, pady=(6, 15), ipady=8)

        tk.Label(left, text="MINECRAFT RAM", bg="#191920", fg="#c8c3d1", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18)
        self.ram = tk.StringVar(value=str(self.config.get("ram_mb", 1536)))
        ram_combo = ttk.Combobox(left, textvariable=self.ram, values=["1024", "1280", "1536", "1792"], state="readonly")
        ram_combo.pack(fill="x", padx=18, pady=(6, 16), ipady=4)
        tk.Label(left, text="1,536 MB recommended for your 4 GB laptop.", bg="#191920", fg="#9a95a2", wraplength=250, justify="left", font=("Segoe UI", 8)).pack(anchor="w", padx=18, pady=(0, 14))

        self.optimize = tk.BooleanVar(value=bool(self.config.get("install_optimizations", True)))
        tk.Checkbutton(left, text="Install compatible FPS mods", variable=self.optimize, bg="#191920", fg="#e4e0e9", activebackground="#191920", activeforeground="white", selectcolor="#262631", font=("Segoe UI", 9)).pack(anchor="w", padx=14)
        tk.Label(left, text="Sodium • Lithium • FerriteCore\nImmediatelyFast • Entity Culling", bg="#191920", fg="#9a95a2", justify="left", font=("Segoe UI", 8)).pack(anchor="w", padx=34, pady=(0, 18))

        right = tk.Frame(content, bg="#101014")
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="READY WHEN YOU ARE", bg="#101014", fg="#f4f4f6", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(8, 4))
        tk.Label(right, text="A lightweight launcher for low-end PCs. First launch downloads Minecraft and Fabric files.", bg="#101014", fg="#aaa5b1", wraplength=440, justify="left", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 17))

        tk.Label(right, text="OPTIONAL SERVER ADDRESS (OFFLINE-MODE SERVERS ONLY)", bg="#101014", fg="#c8c3d1", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.server = tk.StringVar(value=str(self.config.get("server", "")))
        tk.Entry(right, textvariable=self.server, bg="#20202a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 10)).pack(fill="x", pady=(6, 15), ipady=8)
        tk.Label(right, text="Port", bg="#101014", fg="#c8c3d1", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.port = tk.StringVar(value=str(self.config.get("port", 25565)))
        tk.Entry(right, textvariable=self.port, bg="#20202a", fg="white", insertbackground="white", relief="flat", font=("Segoe UI", 10), width=10).pack(anchor="w", pady=(6, 18), ipady=6)

        self.play_button = tk.Button(right, text="▶   INSTALL & PLAY", command=self._start_launch, bg="#8d2444", fg="white", activebackground="#a63156", activeforeground="white", relief="flat", font=("Segoe UI", 12, "bold"), cursor="hand2", pady=12)
        self.play_button.pack(fill="x", pady=(4, 10))
        self.status = tk.StringVar(value="Status: waiting")
        tk.Label(right, textvariable=self.status, bg="#101014", fg="#d48aa0", font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 8))
        tk.Label(right, text="LOG", bg="#101014", fg="#c8c3d1", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.log_box = tk.Text(right, height=13, bg="#17171e", fg="#d9d5df", insertbackground="white", relief="flat", font=("Consolas", 8), wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True, pady=(6, 0))

        footer = tk.Frame(self.root, bg="#15151d")
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text="SHADOW CLIENT is unofficial and not affiliated with Mojang or Microsoft.", bg="#15151d", fg="#77727f", font=("Segoe UI", 8)).pack(side="left", padx=22, pady=10)
        tk.Label(footer, text="F8: toggle in-game HUD", bg="#15151d", fg="#bd4667", font=("Segoe UI", 8, "bold")).pack(side="right", padx=22)

    def log(self, message: str):
        self.events.put(("log", message))

    def _write_log(self, message: str):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        try:
            with LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(message + "\n")
        except Exception:
            pass

    def _drain_events(self):
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == "log":
                    self._write_log(value)
                elif kind == "status":
                    self.status.set("Status: " + value)
                elif kind == "done":
                    self.play_button.configure(state="normal", text="▶   INSTALL & PLAY")
        except queue.Empty:
            pass
        self.root.after(120, self._drain_events)

    def _start_launch(self):
        username = self.username.get().strip()
        if not re.fullmatch(r"[A-Za-z0-9_]{3,16}", username):
            messagebox.showerror("Invalid player name", "Use 3–16 letters, numbers, or underscores.")
            return
        try:
            ram = int(self.ram.get())
            port = int(self.port.get().strip() or "25565")
            if ram not in (1024, 1280, 1536, 1792):
                raise ValueError
            if not 1 <= port <= 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid settings", "Choose a listed RAM value and a port from 1 to 65535.")
            return
        server = self.server.get().strip()
        if server and (" " in server or "/" in server or "\\" in server):
            messagebox.showerror("Invalid server address", "Enter a hostname or IP address only; put the port in the Port field.")
            return
        self.config = {"username": username, "ram_mb": ram, "install_optimizations": self.optimize.get(), "server": server, "port": port}
        save_config(self.config)
        self.play_button.configure(state="disabled", text="PLEASE WAIT…")
        self.status.set("Status: preparing launcher")
        self.worker = threading.Thread(target=self._launch_worker, args=(username, ram, server, port, self.optimize.get()), daemon=True)
        self.worker.start()

    def _launch_worker(self, username, ram, server, port, install_mods):
        try:
            GAME_DIR.mkdir(parents=True, exist_ok=True)
            self.log("Preparing SHADOW CLIENT...")
            self.events.put(("status", "checking launcher engine"))
            backend = ensure_portablemc(self.log)
            if install_mods:
                self.events.put(("status", "installing compatible optimization mods"))
                install_modrinth_mods(self.log)
            else:
                (GAME_DIR / "mods").mkdir(parents=True, exist_ok=True)
            cmd = [str(backend), "start", f"fabric:{MC_VERSION}", "-u", username, f"--jvm-args=-Xms512M -Xmx{ram}M -XX:+UseG1GC"]
            if server:
                cmd.extend(["-s", server, "-p", str(port)])
            env = os.environ.copy()
            # PortableMC uses PMC_MC_DIR for the game working directory.
            env["PMC_MC_DIR"] = str(GAME_DIR)
            self.log("Launching Fabric " + MC_VERSION + " with player " + username + ".")
            self.log("RAM cap: " + str(ram) + " MB. First run may download game assets and Java runtime.")
            self.events.put(("status", "downloading / launching Minecraft"))
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            self.backend_process = subprocess.Popen(cmd, cwd=str(APP_DIR), env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", creationflags=creationflags)
            for line in self.backend_process.stdout:
                self.log(line.rstrip())
            code = self.backend_process.wait()
            self.log(f"PortableMC exited with code {code}.")
            self.events.put(("status", "game process ended" if code == 0 else "launch failed — check the log"))
        except Exception as exc:
            self.log("ERROR: " + str(exc))
            self.events.put(("status", "error — check the log"))
            self.events.put(("log", "See docs/TROUBLESHOOTING.md for common fixes."))
        finally:
            self.events.put(("done", None))

    def _on_close(self):
        if self.backend_process and self.backend_process.poll() is None:
            if not messagebox.askyesno("Minecraft is running", "Close the launcher window? Minecraft will keep running."):
                return
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ShadowLauncher().run()
