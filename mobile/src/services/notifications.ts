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
  // create channel for Android
  if (Platform.OS === 'android') {
    PushNotification.createChannel(
      {
        channelId: NOTIF_CHANNEL_ID,
        channelName: 'Gestão de Notas',
        importance: Importance.HIGH,
        vibrate: true,
      },
      (created) => {
        // console.log(`createChannel returned '${created}'`);
      }
    );
  }

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
  PushNotification.localNotification({
    channelId: NOTIF_CHANNEL_ID,
    title,
    message,
    smallIcon: 'ic_notification',
    playSound: true,
    soundName: 'default',
    userInfo: data,
  });
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

