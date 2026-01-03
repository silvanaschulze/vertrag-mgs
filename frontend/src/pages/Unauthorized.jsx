/**
 * Unauthorized Page - Página 403 / Nicht autorisierte Seite - 403
 * 
 * Exibida quando usuário tenta acessar recurso sem permissão
 * Wird angezeigt, wenn Benutzer versucht auf Ressource ohne Berechtigung zuzugreifen
 */
import { Box, Button, Container, Typography } from '@mui/material';
import { Block as BlockIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Unauthorized = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          textAlign: 'center',
        }}
      >
        {/* Ícone de bloqueado / Gesperrt-Symbol */}
        <BlockIcon
          sx={{
            fontSize: 120,
            color: 'error.main',
            mb: 3,
          }}
        />

        {/* Título / Titel */}
        <Typography variant="h3" component="h1" gutterBottom fontWeight={700}>
          403
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom color="text.secondary">
          Zugriff verweigert / Access Denied
        </Typography>

        {/* Mensagem / Nachricht */}
        <Typography variant="body1" color="text.secondary" sx={{ mt: 2, mb: 4 }}>
          Sie haben keine Berechtigung, auf diese Ressource zuzugreifen.
          <br />
          You don't have permission to access this resource.
        </Typography>

        {/* Botão voltar / Zurück-Schaltfläche */}
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/app/dashboard')}
        >
          Zurück zum Dashboard / Back to Dashboard
        </Button>
      </Box>
    </Container>
  );
};

export default Unauthorized;
