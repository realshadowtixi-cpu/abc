# Troubleshooting

## PortableMC download fails

Check that Windows can open GitHub and that the system date/time is correct. The launcher downloads the x64 archive from the official PortableMC release page. If GitHub is blocked, automatic backend installation will fail.

## The game closes immediately

Open the launch log from `%APPDATA%\ShaDowTixi\ShadowClient\shadowclient.log`. Verify Java 21 support, graphics drivers, free RAM and Fabric version compatibility. Try 1280 MB or 1536 MB RAM. Do not allocate all 4 GB to Minecraft because Windows also needs memory.

## Mod download fails

The launcher selects releases from Modrinth's public API. If the API is unavailable, turn off "Install compatible FPS mods" and try launching Fabric first. You can retry later.

## Server connection fails

An offline username only works on servers whose operators have intentionally enabled offline mode. Online-mode servers require a properly authenticated account. A server may also require a specific Minecraft version, whitelist, or username registration.

## Fabric mod does not load

Make sure the mod JAR was built for Minecraft 1.21.1, Java 21 and Fabric. Ensure Fabric API is installed in the same game's `mods` directory. Check `latest.log` and the Gradle build output for the exact exception.
