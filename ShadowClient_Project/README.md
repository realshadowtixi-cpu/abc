# SHADOW CLIENT — Personal Edition (starter build)

**Developer:** ShaDowTixi  
**Target:** Minecraft Java 1.21.1 · Fabric · Java 21 · Windows x64  
**Design:** lightweight dark UI with crimson/purple accents

This repository contains two pieces:

1. `launcher/` — a small Tkinter desktop launcher. It downloads the official PortableMC Windows x64 backend on first run, then uses it to install/launch Fabric 1.21.1. PortableMC supports Fabric and offline username sessions. The offline username works only on servers configured to accept offline-mode players; it does not bypass authentication on online-mode servers.
2. `mod/` — the SHADOW CLIENT Fabric mod source. The first implementation provides a HUD with FPS, CPS, coordinates and keystrokes, toggled with **F8**.

The launcher and mod are separate deliverables. The launcher does not contain Minecraft's proprietary game files. It downloads game assets and libraries when you first launch, from their official metadata/CDN sources through PortableMC.

## Your laptop settings

For the AMD A9-9420 / Radeon R5 / 4 GB RAM system, the launcher defaults to a **1536 MB maximum heap**. Close browsers and other heavy apps before starting Minecraft. The launcher uses a separate game folder under `%APPDATA%\ShaDowTixi\ShadowClient\game`.

## How to use the source

### Option A — build the Windows `.exe` with GitHub Actions (no IDE on your laptop)

1. Create a new GitHub repository and upload the contents of this project ZIP.
2. Open the repository's **Actions** tab and enable Actions if prompted.
3. Select **Build SHADOW CLIENT for Windows** and click **Run workflow**. A push to `main` or `master` also starts the workflow.
4. When both jobs finish, open the workflow run. Download artifacts:
   - `ShadowClient-Windows-x64` → `ShadowClient.exe`
   - `ShadowClient-Fabric-Mod` → `ShadowClient-0.1.0.jar`
5. Put the Fabric mod JAR into `%APPDATA%\ShaDowTixi\ShadowClient\game\mods\` after the first launcher run has created that folder. Keep the optimization mods enabled in the launcher if you want them.

GitHub-hosted workflows have usage quotas and may require a GitHub account. This project does not guarantee that the cloud workflow will be available without any account or usage limits.

### Option B — run the launcher from source

Install Python 3.11 or newer, then run:

```bat
py launcher\shadow_launcher.py
```

### Building the Fabric mod locally

Install JDK 21 and make sure internet access is available for Gradle/Fabric dependencies. Then run:

```bat
build-mod.bat
```

The custom mod JAR will be created under `mod\build\libs\`.

## Launcher behaviour

- Minecraft version is fixed to 1.21.1.
- Fabric Loader is installed by PortableMC when the game is launched.
- The first run downloads game files and may take time/data.
- Offline player names must be 3–16 characters using letters, digits or underscore.
- Optional server auto-connect is available. Use it only for servers that explicitly allow offline-mode players.
- Optimisation mods are fetched from Modrinth's public API for Minecraft 1.21.1 + Fabric. The exact compatible release is selected at install time.
- The launcher backend is fetched from the official PortableMC GitHub release page. The launcher does not redistribute PortableMC's binary in this source ZIP.

## Included first-build features

- Custom SHADOW CLIENT launcher UI
- Username field for offline-mode sessions
- RAM cap selector (1024–1792 MB; 1536 MB default)
- Optional compatible optimization mod installation: Fabric API, Sodium, Lithium, FerriteCore, ImmediatelyFast, Entity Culling
- Optional server address + port
- Download/launch log output
- Fabric HUD: FPS, left/right CPS, coordinates, WASD + Space state
- F8 HUD visibility toggle
- Windows GitHub Actions build for launcher EXE and Fabric mod JAR

## Important limits

- This is **v0.1 starter implementation**, not a finished Lunar/Feather-scale client.
- The Windows `.exe` is built by the included GitHub Actions workflow; it is not precompiled in this ZIP.
- The Fabric mod source and launcher have not been compiled together on this machine. The environment used to generate this ZIP has no Gradle installation and cannot fetch build dependencies. Treat the mod JAR as unverified until the workflow or your local Gradle build succeeds.
- Windows 10 version 1607 is old. PortableMC's current Windows release lists Windows 10 / Server 2016 as its minimum, but this specific old build may still encounter TLS, runtime, or graphics-driver compatibility issues. Updating Windows is recommended where possible.
- No Minecraft game JAR, assets, or proprietary files are bundled.

## Project structure

```text
ShadowClient_Project/
├── .github/workflows/build-windows.yml
├── launcher/shadow_launcher.py
├── launcher/requirements-build.txt
├── mod/
│   ├── build.gradle
│   ├── gradle.properties
│   ├── settings.gradle
│   └── src/main/...
├── build-mod.bat
├── gradlew.bat
└── README.md
```

## Credits / third-party components

- PortableMC is a separate open-source project and remains under its own license. It is downloaded from its official release page at runtime.
- Fabric Loader / Fabric API are separate open-source projects.
- Optional performance mods are downloaded from Modrinth at runtime and retain their own licenses.
- Minecraft is a Mojang/Microsoft product. SHADOW CLIENT is unofficial and is not affiliated with Mojang or Microsoft.

## After downloading the workflow artifacts

1. Run `ShadowClient.exe` once and use the launcher to install Fabric 1.21.1.
2. Copy the `ShadowClient-0.1.0.jar` artifact into `%APPDATA%\ShaDowTixi\ShadowClient\game\mods\`.
3. Launch again. In a world, press **F8** to show or hide the SHADOW HUD.

The initial HUD is deliberately small: it displays FPS, left/right CPS, block coordinates, and movement-key status. More modules can be added after this first build is confirmed to launch correctly.
