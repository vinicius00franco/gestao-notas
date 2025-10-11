# Limitações do Expo Go

## Problema com Notificações Push

A partir do Expo SDK 53, as notificações push remotas não são mais suportadas no Expo Go. Isso causa os seguintes avisos/erros:

```
ERROR expo-notifications: Android Push notifications (remote notifications) functionality provided by expo-notifications was removed from Expo Go with the release of SDK 53.
WARN Failed to configure notifications [Error: No "projectId" found.]
```

## Soluções

### Opção 1: Usar Development Build (Recomendado)

Para ter funcionalidade completa de notificações push, você precisa usar um development build ao invés do Expo Go:

1. **Configurar o projectId no app.config.ts**:
   - Execute `npx eas init` para criar um projeto EAS
   - O projectId será gerado automaticamente
   - Atualize o valor em `app.config.ts` no campo `extra.eas.projectId`

2. **Criar um development build**:
   ```bash
   # Para Android
   npx eas build --profile development --platform android
   
   # Para iOS
   npx eas build --profile development --platform ios
   ```

3. **Instalar o build no dispositivo**:
   - Após o build finalizar, baixe e instale o APK/IPA gerado
   - Execute `npx expo start --dev-client`

### Opção 2: Continuar com Expo Go (Limitado)

Se você quiser continuar usando Expo Go por enquanto:

- As notificações locais continuam funcionando
- As notificações push remotas NÃO funcionarão
- Os avisos serão exibidos mas não afetam outras funcionalidades do app

O código foi atualizado para:
- Detectar quando está rodando no Expo Go e pular a configuração de push notifications
- Continuar permitindo notificações locais
- Mostrar avisos informativos ao invés de erros

## Documentação

- [Development Builds](https://docs.expo.dev/develop/development-builds/introduction/)
- [Expo Notifications](https://docs.expo.dev/versions/latest/sdk/notifications/)
- [EAS Build](https://docs.expo.dev/build/introduction/)
