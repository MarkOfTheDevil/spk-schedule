package ru.spk.schedule;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.ContentResolver;
import android.content.Context;
import android.content.res.Resources;
import android.media.AudioAttributes;
import android.net.Uri;

/** Selects the optional branded channel for scheduled and test reminders. */
final class PulseReminderChannel {
    static final String EXISTING_CHANNEL_ID = "tomorrow_classes_v1";
    static final String PULSE_CHANNEL_ID = "tomorrow_classes_pulse_v1";

    private PulseReminderChannel() {}

    static String select(Context context, boolean usePulseSound, int soundResource) {
        if (!usePulseSound) return EXISTING_CHANNEL_ID;

        NotificationManager manager = context.getSystemService(NotificationManager.class);
        if (manager == null) return EXISTING_CHANNEL_ID;
        if (manager.getNotificationChannel(PULSE_CHANNEL_ID) != null) return PULSE_CHANNEL_ID;

        NotificationChannel existing = manager.getNotificationChannel(EXISTING_CHANNEL_ID);
        int importance = existing == null
                ? NotificationManager.IMPORTANCE_DEFAULT : existing.getImportance();

        Uri sound = soundUri(context.getResources(), soundResource);
        AudioAttributes audio = new AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build();
        NotificationChannel channel = new NotificationChannel(
                PULSE_CHANNEL_ID, "Пары на завтра · Pulse", importance);
        channel.setDescription("Расписание выбранной группы на следующий день");
        channel.setSound(sound, audio);
        if (existing != null) {
            channel.setShowBadge(existing.canShowBadge());
            channel.setLockscreenVisibility(existing.getLockscreenVisibility());
            long[] pattern = existing.getVibrationPattern();
            if (pattern != null) channel.setVibrationPattern(pattern);
            channel.enableVibration(existing.shouldVibrate());
        }
        manager.createNotificationChannel(channel);
        return PULSE_CHANNEL_ID;
    }

    private static Uri soundUri(Resources resources, int resource) {
        return new Uri.Builder()
                .scheme(ContentResolver.SCHEME_ANDROID_RESOURCE)
                .authority(resources.getResourcePackageName(resource))
                .appendPath(resources.getResourceTypeName(resource))
                .appendPath(resources.getResourceEntryName(resource))
                .build();
    }
}
