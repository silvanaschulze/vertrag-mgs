/**
 * AppLayout - Layout Principal da Aplicação / Hauptlayout der Anwendung
 * 
 * Container que combina Sidebar + Header + Conteúdo
 * Container, der Sidebar + Header + Inhalt kombiniert
 */
import { Box, Toolbar } from '@mui/material';
import Sidebar from './Sidebar';
import Header from './Header';

const DRAWER_WIDTH = 240;

const AppLayout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex' }}>
      {/* Sidebar Fixa / Feste Sidebar */}
      <Sidebar />

      {/* Área Principal / Hauptbereich */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          minHeight: '100vh',
          width: `calc(100% - ${DRAWER_WIDTH}px)`,
        }}
      >
        {/* Header */}
        <Header />

        {/* Espaço para o Header / Platz für Header */}
        <Toolbar />

        {/* Conteúdo da Página / Seiteninhalt */}
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default AppLayout;
