declare module 'react-native-push-notification' {
  export type Importance = number;
  export const Importance: { DEFAULT: Importance; HIGH: Importance };
  export interface ConfigureOptions {
    onRegister?: (token: { os: string; token: string }) => void;
    onNotification?: (notification: any) => void;
    senderID?: string;
    permissions?: { alert?: boolean; badge?: boolean; sound?: boolean };
    popInitialNotification?: boolean;
    requestPermissions?: boolean;
  }
  function configure(opts: ConfigureOptions): void;
  function createChannel(cfg: any, cb?: (created: boolean) => void): void;
  function localNotification(n: any): void;
  const _default: {
    configure: typeof configure;
    createChannel: typeof createChannel;
    localNotification: typeof localNotification;
    FetchResult: { NoData: string };
  };
  export default _default;
}
