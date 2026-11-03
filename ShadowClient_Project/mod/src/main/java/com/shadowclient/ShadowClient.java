package com.shadowclient;

import com.shadowclient.util.CpsTracker;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.util.InputUtil;
import net.minecraft.text.Text;
import org.lwjgl.glfw.GLFW;

public final class ShadowClient implements ClientModInitializer {
    private static boolean hudVisible = true;
    private static KeyBinding toggleHudKey;

    @Override
    public void onInitializeClient() {
        toggleHudKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.shadowclient.toggle_hud",
                InputUtil.Type.KEYSYM,
                GLFW.GLFW_KEY_F8,
                "category.shadowclient"
        ));

        ClientTickEvents.END_CLIENT_TICK.register(client -> {
            while (toggleHudKey.wasPressed()) {
                hudVisible = !hudVisible;
            }
            CpsTracker.prune();
        });

        HudRenderCallback.EVENT.register((drawContext, tickCounter) -> renderHud(MinecraftClient.getInstance(), drawContext));
    }

    private static void renderHud(MinecraftClient client, net.minecraft.client.gui.DrawContext context) {
        if (!hudVisible || client.player == null || client.options.hudHidden) return;

        int x = 8;
        int y = 8;
        int color = 0xFFF2F0F4;
        String[] lines = new String[] {
                "SHADOW CLIENT",
                "FPS: " + client.getCurrentFps(),
                "CPS: " + CpsTracker.leftCps() + " | " + CpsTracker.rightCps(),
                "XYZ: " + client.player.getBlockX() + " " + client.player.getBlockY() + " " + client.player.getBlockZ(),
                "W " + key(client.options.forwardKey.isPressed()) + "  A " + key(client.options.leftKey.isPressed())
                        + "  S " + key(client.options.backKey.isPressed()) + "  D " + key(client.options.rightKey.isPressed())
                        + "  SPACE " + key(client.options.jumpKey.isPressed())
        };

        int width = 0;
        for (String line : lines) width = Math.max(width, client.textRenderer.getWidth(line));
        context.fill(x - 4, y - 4, x + width + 6, y + lines.length * 11 + 4, 0x990D0D12);
        for (int i = 0; i < lines.length; i++) {
            int lineColor = i == 0 ? 0xFFFF5577 : color;
            context.drawTextWithShadow(client.textRenderer, Text.literal(lines[i]), x, y + i * 11, lineColor);
        }
    }

    private static String key(boolean pressed) {
        return pressed ? "ON" : "--";
    }
}
