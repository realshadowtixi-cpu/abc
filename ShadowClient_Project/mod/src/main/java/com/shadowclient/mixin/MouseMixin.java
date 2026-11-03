package com.shadowclient.mixin;

import com.shadowclient.util.CpsTracker;
import net.minecraft.client.Mouse;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.lwjgl.glfw.GLFW;

@Mixin(Mouse.class)
public abstract class MouseMixin {
    @Inject(method = "onMouseButton", at = @At("HEAD"))
    private void shadowclient$trackClick(long window, int button, int action, int modifiers, CallbackInfo ci) {
        if (action == GLFW.GLFW_PRESS && (button == GLFW.GLFW_MOUSE_BUTTON_1 || button == GLFW.GLFW_MOUSE_BUTTON_2)) {
            CpsTracker.register(button == GLFW.GLFW_MOUSE_BUTTON_1 ? 0 : 1);
        }
    }
}
