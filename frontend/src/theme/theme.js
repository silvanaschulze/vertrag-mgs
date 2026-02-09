/**
 * Material-UI Theme - Vertrag-MGS / Material-UI-Theme - Vertrag-MGS
 * 
 * Define cores, tipografia e estilo global da aplicação
 * Baseado em design moderno com sidebar fixa e topbar
 */
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2563EB',      // Azul vibrante (botões primários)
      light: '#60A5FA',     // Azul claro
      dark: '#1E40AF',      // Azul escuro
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#6B7280',      // Cinza médio (textos secundários, bordas)
      light: '#9CA3AF',     // Cinza claro
      dark: '#4B5563',      // Cinza escuro
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#10B981',      // Verde
      light: '#34D399',
      dark: '#059669',
    },
    warning: {
      main: '#F59E0B',      // Laranja/Amarelo
      light: '#FBBF24',
      dark: '#D97706',
    },
    error: {
      main: '#EF4444',      // Vermelho
      light: '#F87171',
      dark: '#DC2626',
    },
    info: {
      main: '#3B82F6',      // Azul info
      light: '#60A5FA',
      dark: '#2563EB',
    },
    background: {
      default: '#F9FAFB',   // Cinza muito claro (fundo geral)
      paper: '#FFFFFF',     // Branco (cards, modais)
    },
    text: {
      primary: '#111827',   // Texto principal (quase preto)
      secondary: '#6B7280', // Texto secundário (cinza médio)
      disabled: '#9CA3AF',  // Texto desabilitado (cinza claro)
    },
    divider: '#E5E7EB',     // Linhas divisórias (cinza muito claro)
  },
  
  typography: {
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Helvetica',
      'Arial',
      'sans-serif',
    ].join(','),
    fontSize: 14,           // Tamanho base 14px
    h1: {
      fontSize: '2rem',     // 32px
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '1.5rem',   // 24px
      fontWeight: 700,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.25rem',  // 20px
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.125rem', // 18px
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1rem',     // 16px
      fontWeight: 600,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '0.875rem', // 14px
      fontWeight: 600,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '0.875rem', // 14px
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.8125rem', // 13px
      lineHeight: 1.5,
    },
    button: {
      fontSize: '0.875rem', // 14px
      fontWeight: 500,
      textTransform: 'none',
    },
  },
  
  shape: {
    borderRadius: 6,        // Bordas levemente arredondadas
  },
  
  components: {
    // Botões / Buttons
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          padding: '8px 16px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          },
        },
        outlined: {
          borderColor: '#E5E7EB',
          color: '#6B7280',
          '&:hover': {
            borderColor: '#6B7280',
            backgroundColor: '#F9FAFB',
          },
        },
      },
    },
    
    // Inputs / Eingabefelder
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: '#FFFFFF',
            '& fieldset': {
              borderColor: '#E5E7EB',
            },
            '&:hover fieldset': {
              borderColor: '#6B7280',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#2563EB',
            },
          },
        },
      },
    },
    
    // Tabs / Registerkarten
    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #E5E7EB',
        },
        indicator: {
          backgroundColor: '#2563EB',
          height: 3,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '0.875rem',
          color: '#6B7280',
          '&.Mui-selected': {
            color: '#2563EB',
          },
        },
      },
    },
    
    // AppBar / Topbar
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          color: '#111827',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        },
      },
    },
    
    // Drawer / Sidebar
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#FFFFFF',
          borderRight: '1px solid #E5E7EB',
        },
      },
    },
    
    // Cards
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          width: '100%',
          marginLeft: 'auto',
          marginRight: 'auto',
          overflow: 'visible',
          backgroundColor: '#fff',
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          },
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: '24px',
          minWidth: 0,
          overflow: 'visible',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        },
      },
    },
    
    // Tooltips
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: '#111827',
          fontSize: '0.75rem',
        },
      },
    },
  },
});

export default theme;
