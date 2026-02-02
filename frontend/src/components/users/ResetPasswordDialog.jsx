import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Box } from '@mui/material';

const ResetPasswordDialog = ({ open, userId, userName, onClose, onSubmit, loading }) => {
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    if (password.length < 8) {
      setError('Das Passwort muss mindestens 8 Zeichen haben.');
      return;
    }
    if (password !== confirm) {
      setError('Passwörter stimmen nicht überein.');
      return;
    }
    setError('');
    onSubmit(password);
    setPassword('');
    setConfirm('');
  };

  const handleClose = () => {
    setPassword('');
    setConfirm('');
    setError('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="xs" fullWidth>
      <DialogTitle>Passwort zurücksetzen / Reset Password</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          Benutzer: <b>{userName}</b>
        </Box>
        <TextField
          label="Neues Passwort / New Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          fullWidth
          margin="dense"
          autoFocus
        />
        <TextField
          label="Bestätigen / Confirm Password"
          type="password"
          value={confirm}
          onChange={e => setConfirm(e.target.value)}
          fullWidth
          margin="dense"
        />
        {error && <Box sx={{ color: 'error.main', mt: 1 }}>{error}</Box>}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>Abbrechen / Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>Zurücksetzen / Reset</Button>
      </DialogActions>
    </Dialog>
  );
};

ResetPasswordDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  userId: PropTypes.number,
  userName: PropTypes.string,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

export default ResetPasswordDialog;
