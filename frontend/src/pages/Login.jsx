/**
 * Login Page - Página de Login / Login-Seite
 * 
 * Formulário de autenticação do sistema
 * Authentifizierungsformular des Systems
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  TextField,
  Typography,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useAuthStore } from '../store/authStore';
import { login as loginApi } from '../services/authApi';

// Schema de validação / Validierungsschema
const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'E-Mail ist erforderlich / Email is required')
    .email('Ungültige E-Mail / Invalid email'),
  password: z
    .string()
    .min(1, 'Passwort ist erforderlich / Password is required'),
});

const Login = () => {
  const navigate = useNavigate();
  const { login: setAuth } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Configurar react-hook-form / react-hook-form konfigurieren
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  // Função de submit / Submit-Funktion
  const onSubmit = async (data) => {
    try {
      setLoading(true);
      setError('');

      // Chama API de login / Login-API aufrufen
      const response = await loginApi(data.email, data.password);

      // Salva token e user no store / Token und Benutzer im Store speichern
      setAuth(response.access_token, response.user);

      // Redireciona para dashboard / Zu Dashboard umleiten
      navigate('/app/dashboard');
    } catch (err) {
      console.error('Login error:', err);
      
      // Mensagem de erro / Fehlermeldung
      if (err.response?.status === 401) {
        setError('Ungültige Anmeldedaten / Invalid credentials');
      } else {
        setError('Verbindungsfehler. Bitte versuchen Sie es später erneut. / Connection error. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'background.default',
      }}
    >
      <Container maxWidth="sm">
        <Card elevation={3}>
          <CardContent sx={{ p: 4 }}>
            {/* Logo e Título / Logo und Titel */}
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <img
                src="/logo.jpg"
                alt="Christburg Logo"
                style={{ maxWidth: '200px', height: 'auto', marginBottom: '16px' }}
              />
              <Typography variant="h4" component="h1" fontWeight={700} gutterBottom>
                Vertrag-MGS
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Vertragsverwaltungssystem / Contract Management System
              </Typography>
            </Box>

            {/* Mensagem de erro / Fehlermeldung */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {/* Formulário / Formular */}
            <form onSubmit={handleSubmit(onSubmit)}>
              {/* Campo Email / E-Mail-Feld */}
              <TextField
                {...register('email')}
                label="E-Mail"
                type="email"
                fullWidth
                margin="normal"
                error={!!errors.email}
                helperText={errors.email?.message}
                disabled={loading}
                autoComplete="email"
                autoFocus
              />

              {/* Campo Senha / Passwort-Feld */}
              <TextField
                {...register('password')}
                label="Passwort / Password"
                type="password"
                fullWidth
                margin="normal"
                error={!!errors.password}
                helperText={errors.password?.message}
                disabled={loading}
                autoComplete="current-password"
              />

              {/* Botão de Login / Login-Schaltfläche */}
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mt: 3, mb: 2 }}
              >
                {loading ? (
                  <>
                    <CircularProgress size={24} sx={{ mr: 1 }} color="inherit" />
                    Anmelden... / Logging in...
                  </>
                ) : (
                  'Anmelden / Login'
                )}
              </Button>
            </form>

            {/* Informações adicionais / Zusätzliche Informationen */}
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary">
                © {new Date().getFullYear()} Christburg. Alle Rechte vorbehalten. / All rights reserved.
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default Login;
