import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Paper, Typography, Breadcrumbs, Link, CircularProgress } from '@mui/material';
import { useSnackbar } from 'notistack';
import UserForm from '../../components/users/UserForm';
import usersApi from '../../services/usersApi';

const UserManage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!id);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (id) {
      setLoading(true);
      usersApi.getUser(id)
        .then(setUser)
        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleSubmit = async (data) => {
    setSubmitting(true);
    try {
      let submitData = { ...data };
      // Se for update e password está vazio, remove o campo
      if (id && (!submitData.password || submitData.password === '')) {
        delete submitData.password;
      }
      if (id) {
        await usersApi.updateUser(id, submitData);
        enqueueSnackbar('Benutzer erfolgreich aktualisiert!', { variant: 'success' });
      } else {
        await usersApi.createUser(submitData);
        enqueueSnackbar('Benutzer erfolgreich erstellt! ', { variant: 'success' });
      }
      navigate('/app/users');
    } catch (e) {
      // Erro de senha
      if (e?.response?.data?.detail) {
        const detail = e.response.data.detail;
        if (Array.isArray(detail) && detail.some(d => d.loc && d.loc.includes('password'))) {
          enqueueSnackbar('Fehler beim Passwort: Mindestens 8 Zeichen, mindestens ein Großbuchstabe / Erro na senha: Pelo menos 8 caracteres, pelo menos uma letra maiúscula', { variant: 'error' });
        } else if (typeof detail === 'string') {
          enqueueSnackbar(detail, { variant: 'error' });
        } else {
          enqueueSnackbar('Fehler beim Speichern ', { variant: 'error' });
        }
      } else {
        enqueueSnackbar('Fehler beim Speichern', { variant: 'error' });
      }
    }
    setSubmitting(false);
  };

  return (
    <Container>
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link underline="hover" color="inherit" href="/app/users">Users</Link>
        <Typography color="text.primary">{id ? 'Edit User' : 'New User'}</Typography>
      </Breadcrumbs>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {id ? 'Benutzer bearbeiten ' : 'Neuer Benutzer '}
        </Typography>
        {loading && <CircularProgress />}
        {!loading && (
          <UserForm
            initialData={user}
            onSubmit={handleSubmit}
            onCancel={() => navigate('/app/users')}
            loading={submitting}
          />
        )}
      </Paper>
    </Container>
  );
};

export default UserManage;
