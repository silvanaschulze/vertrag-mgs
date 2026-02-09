
# Frontend - Vertrag-MGS

Interface web do sistema de gerenciamento de contratos (Vertrag-MGS).

## Stack
- React 18 + Vite 5
- Material-UI 5 (MUI)
- Zustand, React Hook Form, Zod, Notistack
- Axios, React Router DOM

## Comandos principais

```bash
# Instalar dependências
npm install

# Rodar em modo desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview

# Lint
npm run lint
```

## Variáveis de ambiente

Configure o backend no arquivo `.env`:

```
VITE_API_URL=http://localhost:8000/api
```
Para produção, use a URL do backend real:
```
VITE_API_URL=https://seuservidor/api
```

## Build e Deploy
- O build gera arquivos estáticos em `dist/`.
- Use um servidor web (Apache, Nginx, etc) para servir o conteúdo de `dist/`.
- O proxy para `/api` é configurado no `vite.config.js` apenas para desenvolvimento.

## Estrutura
- `src/components/` - Componentes reutilizáveis
- `src/pages/` - Páginas principais
- `src/services/` - Serviços de API
- `src/store/` - Zustand stores
- `src/theme/` - Tema MUI
- `src/utils/` - Utilitários

## Contato
Consulte o README principal na raiz do projeto para mais detalhes gerais.
