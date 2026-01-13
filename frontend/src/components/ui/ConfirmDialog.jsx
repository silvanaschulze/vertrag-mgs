/**
 * ConfirmDialog - Diálogo de Confirmação
 * Bestätigungsdialog
 * 
 * Diálogo reutilizável para confirmação de ações destrutivas
 * Wiederverwendbarer Dialog zur Bestätigung destruktiver Aktionen
 */
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button
} from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';

const ConfirmDialog = ({
  open = false,
  title = 'Bestätigung / Confirm',
  message = 'Sind Sie sicher? / Are you sure?',
  confirmText = 'Bestätigen / Confirm',
  cancelText = 'Abbrechen / Cancel',
  onConfirm,
  onCancel,
  severity = 'warning' // 'warning', 'error', 'info'
}) => {
  const getColor = () => {
    switch (severity) {
      case 'error':
        return 'error';
      case 'info':
        return 'info';
      default:
        return 'warning';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      aria-labelledby="confirm-dialog-title"
      aria-describedby="confirm-dialog-description"
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle id="confirm-dialog-title" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <WarningIcon color={getColor()} />
        {title}
      </DialogTitle>
      
      <DialogContent>
        <DialogContentText id="confirm-dialog-description">
          {message}
        </DialogContentText>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onCancel} variant="outlined">
          {cancelText}
        </Button>
        <Button 
          onClick={onConfirm} 
          variant="contained" 
          color={getColor()}
          autoFocus
        >
          {confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ConfirmDialog;
