# Configuração do EAS (Expo Application Services)

## Passos para configurar o projeto com EAS

### 1. Criar conta no Expo (se ainda não tiver)

Acesse https://expo.dev e crie uma conta gratuita.

### 2. Fazer login no EAS CLI

```bash
npx eas login
```

Ou se preferir usar token:
```bash
npx eas login --help
```

### 3. Inicializar o projeto EAS

Após fazer login com sucesso:

```bash
npx eas init
```

Este comando irá:
- Criar um projeto no Expo
- Gerar um `projectId` único
- Atualizar o `app.config.ts` com o `projectId`

### 4. Configurar notificações (opcional)

Se quiser usar notificações push remotas, você precisará criar um development build:

```bash
# Para Android
npx eas build --profile development --platform android

# Para iOS (requer conta Apple Developer)
npx eas build --profile development --platform ios
```

### 5. Executar o app

**Com Expo Go (limitado - sem push notifications remotas):**
```bash
npm start
```

**Com development build (completo - com push notifications):**
```bash
npm start -- --dev-client
```

## Notas Importantes

- **Expo Go**: Suporta apenas notificações locais (não push remotas)
- **Development Build**: Suporta todas as funcionalidades incluindo push notifications
- **Dependências descontinuadas**: Os avisos de dependências descontinuadas vêm do próprio `eas-cli` e serão corrigidos pela equipe do Expo nas próximas versões

## Recursos

- [Documentação EAS](https://docs.expo.dev/eas/)
- [Development Builds](https://docs.expo.dev/develop/development-builds/introduction/)
- [Expo Notifications](https://docs.expo.dev/versions/latest/sdk/notifications/)
