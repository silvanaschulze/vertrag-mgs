import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, CircularProgress } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useNavigate } from 'react-router-dom';
import UserTable from '../../components/users/UserTable';
import UserFilters from '../../components/users/UserFilters';
import ResetPasswordDialog from '../../components/users/ResetPasswordDialog';
import usersApi from '../../services/usersApi';

const UsersPage = () => {
    const handleDelete = async (userId) => {
      if (!window.confirm('Tem certeza que deseja excluir este usuário?')) return;
      setLoading(true);
      try {
        await usersApi.deleteUser(userId);
        fetchUsers();
      } catch (e) {}
      setLoading(false);
    };
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [totalRows, setTotalRows] = useState(0);
  const [filters, setFilters] = useState({});
  const [sortBy, setSortBy] = useState(null);
  const [resetPasswordOpen, setResetPasswordOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [selectedUserName, setSelectedUserName] = useState('');
  const navigate = useNavigate();

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = {
        page: page + 1,
        page_size: pageSize,
        ...filters,
        sort_by: sortBy?.field,
        sort_order: sortBy?.sort,
      };
      const res = await usersApi.getUsers(params);
      setUsers(res.items || []);
      setTotalRows(res.total || 0);
    } catch (e) {
      // TODO: toast error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
    // eslint-disable-next-line
  }, [page, pageSize, filters, sortBy]);

  const handleEdit = (userId) => navigate(`/app/users/${userId}/edit`);
  const handleResetPassword = (userId) => {
    const user = users.find(u => u.id === userId);
    setSelectedUserId(userId);
    setSelectedUserName(user?.name || '');
    setResetPasswordOpen(true);
  };
  const handleToggleActive = async (userId, isActive) => {
    setLoading(true);
    try {
      if (isActive) await usersApi.activateUser(userId);
      else await usersApi.deactivateUser(userId);
      fetchUsers();
    } catch (e) {}
    setLoading(false);
  };
  const handleResetPasswordSubmit = async (newPassword) => {
    setLoading(true);
    try {
      await usersApi.resetPassword(selectedUserId, newPassword);
      setResetPasswordOpen(false);
      // TODO: toast sucesso
    } catch (e) {}
    setLoading(false);
  };
  const handleFilterChange = (f) => { setFilters(f); setPage(0); };
  const handleClearFilters = () => { setFilters({}); setPage(0); };

  // TODO: checar permissão para criar usuário
  const canCreateUser = true;

  return (
    <Container>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Benutzer / Users</Typography>
        {canCreateUser && (
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => navigate('/app/users/new')}>
            Neuer Benutzer / New User
          </Button>
        )}
      </Box>
      <UserFilters filters={filters} onChange={handleFilterChange} onClear={handleClearFilters} />
      <UserTable
        users={users}
        loading={loading}
        page={page}
        pageSize={pageSize}
        totalRows={totalRows}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
        onSortChange={setSortBy}
        onEdit={handleEdit}
        onResetPassword={handleResetPassword}
        onToggleActive={handleToggleActive}
        onDelete={handleDelete}
      />
      <ResetPasswordDialog
        open={resetPasswordOpen}
        userId={selectedUserId}
        userName={selectedUserName}
        onClose={() => setResetPasswordOpen(false)}
        onSubmit={handleResetPasswordSubmit}
        loading={loading}
      />
      {loading && <CircularProgress sx={{ position: 'fixed', top: 24, right: 24 }} />}
    </Container>
  );
};

export default UsersPage;
