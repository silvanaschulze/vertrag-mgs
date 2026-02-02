import { useSnackbar } from 'notistack';

/**
 * Hook personalizado para notificações
 * DE: Benutzerdefinierter Hook für Benachrichtigungen
 * PT: Hook personalizado para notificações
 * 
 * Wrapper em torno do notistack para uso consistente
 * Wrapper um notistack für konsistente Nutzung
 */
export const useNotification = () => {
  const { enqueueSnackbar } = useSnackbar();

  const showSuccess = (message) => {
    enqueueSnackbar(message, { variant: 'success' });
  };

  const showError = (message) => {
    enqueueSnackbar(message, { variant: 'error' });
  };

  const showWarning = (message) => {
    enqueueSnackbar(message, { variant: 'warning' });
  };

  const showInfo = (message) => {
    enqueueSnackbar(message, { variant: 'info' });
  };

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
};

export default useNotification;
