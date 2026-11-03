package com.shadowclient.util;

import java.util.ArrayDeque;
import java.util.Deque;

public final class CpsTracker {
    private static final Deque<Long> LEFT = new ArrayDeque<>();
    private static final Deque<Long> RIGHT = new ArrayDeque<>();
    private static final long WINDOW_MS = 1000L;

    private CpsTracker() {}

    public static synchronized void register(int button) {
        long now = System.currentTimeMillis();
        if (button == 0) LEFT.addLast(now);
        if (button == 1) RIGHT.addLast(now);
        prune(now);
    }

    public static synchronized void prune() {
        prune(System.currentTimeMillis());
    }

    private static void prune(long now) {
        while (!LEFT.isEmpty() && now - LEFT.peekFirst() > WINDOW_MS) LEFT.removeFirst();
        while (!RIGHT.isEmpty() && now - RIGHT.peekFirst() > WINDOW_MS) RIGHT.removeFirst();
    }

    public static synchronized int leftCps() {
        prune(System.currentTimeMillis());
        return LEFT.size();
    }

    public static synchronized int rightCps() {
        prune(System.currentTimeMillis());
        return RIGHT.size();
    }
}
