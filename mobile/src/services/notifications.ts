/**
 * notifications.ts
 * Lightweight integration with `react-native-push-notification`.
 *
 * Notes:
 * - This project uses Expo. `react-native-push-notification` requires native modules
 *   and therefore a bare workflow or EAS build. If you keep using Expo Go, use
 *   `expo-notifications` or `@react-native-firebase/messaging` with a custom dev client.
 * - The file below provides the initialization and token registration flow expected
 *   in a bare React Native app. It also exposes helpers to send the token to your
 *   backend (via existing `api` service).
 */

import PushNotification, {Importance} from 'react-native-push-notification';
import {Platform} from 'react-native';
import {api} from './api';

const NOTIF_CHANNEL_ID = 'gestao-notas-general';
let CURRENT_DEVICE_TOKEN: string | undefined;

export function configureNotifications({onNotification}: {onNotification?: (n: any) => void} = {}) {
  // Defensive: the native PushNotification module is not available when running
  // inside Expo Go. Check presence of native functions before calling them.
  const hasCreateChannel = !!PushNotification && typeof (PushNotification as any).createChannel === 'function';
  const hasConfigure = !!PushNotification && typeof (PushNotification as any).configure === 'function';

  if (Platform.OS === 'android' && hasCreateChannel) {
    try {
      PushNotification.createChannel(
        {
          channelId: NOTIF_CHANNEL_ID,
          channelName: 'Gestão de Notas',
          importance: Importance.HIGH,
          vibrate: true,
        },
        (created) => {
          // channel created (or already existed)
        }
      );
    } catch (err) {
      console.warn('Failed to create notification channel', err);
    }
  } else if (Platform.OS === 'android' && !hasCreateChannel) {
    console.warn('PushNotification native module not available: skipping createChannel. If you are using Expo Go, migrate to expo-notifications or use a dev client/EAS build.');
  }

  if (hasConfigure) {
    try {
      PushNotification.configure({
        // (optional) Called when Token is generated (iOS and Android)
        onRegister: function (token) {
          // token: { os: 'ios'|'android', token: '...' }
          // Send token to server
          CURRENT_DEVICE_TOKEN = token.token;
          registerDeviceToken(token.token, token.os).catch(() => {});
        },

        // (required) Called when a remote or local notification is opened or received
        onNotification: function (notification) {
          if (onNotification) onNotification(notification);
          // Required on iOS only (see library docs)
          notification.finish && notification.finish(PushNotification.FetchResult.NoData);
        },

        // Android only: GCM or FCM Sender ID (deprecated in modern FCM usage)
        senderID: undefined,

        // IOS only
        permissions: {
          alert: true,
          badge: true,
          sound: true,
        },

        popInitialNotification: true,
        requestPermissions: true,
      });
    } catch (err) {
      console.warn('PushNotification.configure failed', err);
    }
  } else {
    console.warn('PushNotification native module not available: skipping configure. If you are using Expo Go, migrate to expo-notifications or use a dev client/EAS build.');
  }
}

export async function registerDeviceToken(token: string, platform?: string) {
  try {
    // API path to register device tokens should be implemented server-side.
    // Example payload: { token, platform }
    await api.post('/api/notifications/register-device/', { token, platform });
  } catch (err) {
    // ignore failures silently for now
    console.warn('Failed to register device token', err);
  }
}

export function localNotify({title, message, data}: {title: string; message: string; data?: any}) {
  if (!!PushNotification && typeof (PushNotification as any).localNotification === 'function') {
    try {
      PushNotification.localNotification({
        channelId: NOTIF_CHANNEL_ID,
        title,
        message,
        smallIcon: 'ic_notification',
        playSound: true,
        soundName: 'default',
        userInfo: data,
      });
    } catch (err) {
      console.warn('localNotify failed', err);
    }
  } else {
    // Fallback: running in Expo Go (no native) — no-op or optionally show an in-app alert
    console.warn('localNotify skipped because PushNotification native module is not available (Expo Go).');
  }
}

// Polling-based delivery: fetch pending server-side notifications for the logged
// user and show them as local notifications. This avoids FCM entirely and makes
// delivery dependent on the app being opened (or background fetch configured).
export async function fetchAndShowPendingNotifications(deviceToken?: string) {
  try {
    const token = deviceToken || CURRENT_DEVICE_TOKEN;
    const res = await api.get('/api/notifications/pending/', {
      headers: token ? { 'X-Device-Token': token } : undefined,
    });
    const items = res.data as Array<any>;
    for (const it of items) {
      try {
        localNotify({ title: it.title, message: it.body, data: it.data });
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

