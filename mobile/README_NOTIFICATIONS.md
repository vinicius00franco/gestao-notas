# Notificações sem Firebase (Polling + Local Notifications)

Este app usa `react-native-push-notification` para exibir notificações locais e consulta o backend em `/api/notifications/pending/` para buscar notificações pendentes por usuário.

## Fluxo
- Backend cria `Notification` por usuário (via `PushStoreObserver` em `lancamento_created`).
- Mobile chama `fetchAndShowPendingNotifications()` ao entrar em foreground (e opcionalmente em background) e exibe notificações locais.
- Mobile confirma entrega via POST `/api/notifications/ack/`.

## Requisitos
- Build nativo (EAS ou bare). `react-native-push-notification` não funciona no Expo Go.
- Android: configurar ícone `ic_notification` e canal.
- iOS: permissões de notificações e capabilities de background fetch se desejar entrega em background.

## Background Fetch (opcional)
- iOS: habilite `Background Modes` > `Background fetch` e use um timer/Task Manager para chamar `fetchAndShowPendingNotifications()` periodicamente.
- Android: use WorkManager/Headless JS para agendar chamadas de `fetchAndShowPendingNotifications()`.

> Observação: background fetch é oportunista e dependente do SO. Para entrega garantida quando app está fechado por longos períodos, considere usar um serviço de push (APNs/FCM).

## Endpoint backend
- POST `/api/notifications/register-device/` { token, platform }
- GET `/api/notifications/pending/` (autenticado por JWT de empresa ou `Authorization` de usuário; também aceita header `X-Device-Token`)
- POST `/api/notifications/ack/` { id } (mesmas credenciais; opcional `device` e header `X-Device-Token`)

## Ajuste de destinatários
- O `PushStoreObserver` notifica usuários com `Device` ativo vinculado à empresa do Job.
- Garanta que o app registre o `Device` após login para associar `user` e `empresa`.
 - Se usar o login por CNPJ/senha (JWT de Empresa), inclua o token `X-Device-Token` nos requests de pending/ack para que o backend resolva o usuário associado ao device.