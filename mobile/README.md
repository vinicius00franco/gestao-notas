# Mobile App (React Native + Expo)

Aplicativo móvel para o sistema de gestão de notas fiscais, baseado nas rotas e regras de negócio da API Django.

Principais telas e fluxos mapeados a partir das rotas e requisitos:
- Upload e processamento assíncrono de notas (POST `/api/processar-nota/`) [RF001, RF002, RN013]
- Acompanhamento de status de job por UUID (GET `/api/jobs/:uuid/`) [RF005, RN006, RN012]
- Listas de Contas a Pagar (GET `/api/contas-a-pagar/`) e a Receber (GET `/api/contas-a-receber/`) [RF006, RF007, RN014]
- Dashboard gerencial (GET `/api/dashboard/`) [RF008]

## Arquitetura
- Expo (React Native)
- Navegação: React Navigation (Tabs + Stack)
- Estado do servidor: TanStack Query (cache, polling, revalidação)
- Estado local: Zustand (tema/flags)
- HTTP: Axios com baseURL configurável via `API_BASE_URL`
- Boas práticas: ErrorBoundary, retry/backoff, separação de camadas (screens/services/components/store)

## Estrutura
```
mobile/
	app.config.ts        # Lê API_BASE_URL e injeta em Constants.manifest.extra
	App.tsx              # Ponto de entrada (reexport de src/App)
	babel.config.js      # Plugin do reanimated habilitado
	package.json         # Dependências e scripts
	tsconfig.json        # TS com lib DOM (FormData) e paths @/
	assets/              # Coloque ícones/splash se desejar
	src/
		App.tsx
		navigation/RootNavigator.tsx
		screens/
			DashboardScreen.tsx
			ContasAPagarScreen.tsx
			ContasAReceberScreen.tsx
			UploadNotaScreen.tsx
			JobStatusScreen.tsx
		services/
			api.ts            # axios + endpoints
			queries.ts        # hooks de dados (React Query)
		store/ui.ts         # Zustand
		components/         # UI reusável
			Loading.tsx
			ErrorView.tsx
			EmptyState.tsx
			ListItem.tsx
			ErrorBoundary.tsx
		theme/index.ts
```

## Setup
1) Pré-requisitos
- Node LTS (>=18)
- pnpm (recomendado) ou npm
- Android Studio (emulador) ou Expo Go no celular

2) Instalação
```bash
cd mobile
pnpm install && pnpm expo install
# ou
npm install && npx expo install
```

3) Configurar API Base URL (padrão: http://localhost:8000)
```bash
export API_BASE_URL="http://localhost:8000"
```

4) Rodar o app
```bash
pnpm start
# ou
npm run start
```

## Mapeamento de Telas -> Endpoints
- Dashboard: GET `/api/dashboard/`
- Pagar: GET `/api/contas-a-pagar/`
- Receber: GET `/api/contas-a-receber/`
- Upload: POST `/api/processar-nota/` (multipart: `arquivo`, `meu_cnpj`)
- Status do Job: GET `/api/jobs/:uuid/`

## Notas
- O app assume API sem autenticação no momento. Se necessário, adicione interceptors no `services/api.ts` e telas de login.
- Polling de status para jobs ocorre a cada 2s enquanto status estiver `PENDENTE`/`PROCESSANDO`.
- Listas usam cache e revalidação com TanStack Query.

## Próximos passos sugeridos
- Tema dark/light customizado e ícones de tabs
- Tela de detalhes do lançamento (quando API expor rota) e de parceiro
- Otimizações de rede (gzip/br, pag paginação/infinite scroll)
