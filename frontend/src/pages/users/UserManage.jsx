import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Paper, Typography, Breadcrumbs, Link, CircularProgress } from '@mui/material';
import UserForm from '../../components/users/UserForm';
import usersApi from '../../services/usersApi';

const UserManage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
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
      if (id) await usersApi.updateUser(id, submitData);
      else await usersApi.createUser(submitData);
      navigate('/app/users');
    } catch (e) {
      // TODO: toast error
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
          {id ? 'Benutzer bearbeiten / Edit User' : 'Neuer Benutzer / New User'}
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
