/**
 * notifications.ts
 * Integration with `expo-notifications` for Expo apps.
 */

import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { api } from './api';

const NOTIF_CHANNEL_ID = 'gestao-notas-general';
let CURRENT_DEVICE_TOKEN: string | undefined;

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

export async function configureNotifications({ onNotification }: { onNotification?: (n: any) => void } = {}) {
  try {
    // Request permissions
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.warn('Notification permissions not granted');
      return;
    }

    // Get push token
    const token = await Notifications.getExpoPushTokenAsync();
    CURRENT_DEVICE_TOKEN = token.data;
    await registerDeviceToken(token.data, Platform.OS);

    // Set up notification listener
    const notificationListener = Notifications.addNotificationReceivedListener(notification => {
      if (onNotification) onNotification(notification);
    });

    const responseListener = Notifications.addNotificationResponseReceivedListener(response => {
      if (onNotification) onNotification(response.notification);
    });

    // Store listeners for cleanup if needed
    (global as any).__notificationListeners = { notificationListener, responseListener };

  } catch (err) {
    console.warn('Failed to configure notifications', err);
  }
}

export async function registerDeviceToken(token: string, platform?: string) {
  try {
    await api.post('/api/notifications/register-device/', { token, platform });
  } catch (err) {
    console.warn('Failed to register device token', err);
  }
}

export async function localNotify({ title, message, data }: { title: string; message: string; data?: any }) {
  try {
    await Notifications.scheduleNotificationAsync({
      content: {
        title,
        body: message,
        data: data || {},
        sound: 'default',
      },
      trigger: null, // Show immediately
    });
  } catch (err) {
    console.warn('localNotify failed', err);
  }
}

// Polling-based delivery: fetch pending server-side notifications
export async function fetchAndShowPendingNotifications(deviceToken?: string) {
  try {
    const token = deviceToken || CURRENT_DEVICE_TOKEN;
    const res = await api.get('/api/notifications/pending/', {
      headers: token ? { 'X-Device-Token': token } : undefined,
    });
    const items = res.data as Array<any>;
    for (const it of items) {
      try {
        await localNotify({ title: it.title, message: it.body, data: it.data });
        // acknowledge so server marks delivered
        await api.post(
          '/api/notifications/ack/',
          { id: it.id, device: token },
          { headers: token ? { 'X-Device-Token': token } : undefined }
        );
      } catch (inner) {
        console.warn('failed to show/ack notification', inner);
      }
    }
  } catch (err) {
    // ignore network errors
  }
}

export default {
  configureNotifications,
  registerDeviceToken,
  localNotify,
  fetchAndShowPendingNotifications,
};

