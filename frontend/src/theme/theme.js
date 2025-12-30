/**
 * Material-UI Theme / Material-UI-Theme
 * 
 * Define cores, tipografia e estilo global da aplicação
 */
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',      // Azul principal
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',      // Rosa/vermelho
      light: '#f73378',
      dark: '#9a0036',
    },
    success: {
      main: '#4caf50',      // Verde
    },
    warning: {
      main: '#ff9800',      // Laranja
    },
    error: {
      main: '#f44336',      // Vermelho
    },
    info: {
      main: '#2196f3',      // Azul claro
    },
    background: {
      default: '#f5f5f5',   // Cinza claro (fundo)
      paper: '#ffffff',     // Branco (cards)
    },
  },
  
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
  },
  
  components: {
    // Customizações de componentes
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Remove UPPERCASE dos botões
        },
      },
    },
    MuiAppBar: {
      defaultProps: {
        elevation: 1, // Sombra mais suave
      },
    },
  },
});

export default theme;
