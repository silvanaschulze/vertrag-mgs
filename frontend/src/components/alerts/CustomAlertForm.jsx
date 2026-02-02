import { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Grid,
  Box,
  Typography,
  Alert
} from '@mui/material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { de } from 'date-fns/locale';
import { format } from 'date-fns';
import { ALERT_TYPES } from '../../utils/constants';
import alertsApi from '../../services/alertsApi';
import { useNotification } from '../../hooks/useNotification';

/**
 * Formulário para criar alerta customizado
 * DE: Formular zum Erstellen benutzerdefinierter Warnungen
 * PT: Formulário para criar alerta customizado
 */
const CustomAlertForm = ({ open, onClose, contractId, contractTitle, onSuccess }) => {
  const { showSuccess, showError } = useNotification();

  const [formData, setFormData] = useState({
    alert_type: 'BENUTZERDEFINIERT',
    scheduled_for: new Date(),
    recipient: '',
    subject: '',
    custom_message: ''
  });

  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Validação
  const validate = () => {
    const newErrors = {};

    if (!formData.scheduled_for) {
      newErrors.scheduled_for = 'Datum erforderlich / Data obrigatória';
    }

    if (!formData.recipient || !formData.recipient.trim()) {
      newErrors.recipient = 'E-Mail erforderlich / E-mail obrigatório';
    } else {
      // Suporta múltiplos emails separados por vírgula ou ponto e vírgula
      const emails = formData.recipient.split(/[,;]/).map(e => e.trim());
      const invalidEmails = emails.filter(email => !email.includes('@') || !email.includes('.'));
      if (invalidEmails.length > 0) {
        newErrors.recipient = `Ungültige E-Mail(s): ${invalidEmails.join(', ')} / E-mail(s) inválido(s)`;
      }
    }

    if (!formData.subject || formData.subject.trim().length === 0) {
      newErrors.subject = 'Betreff erforderlich / Assunto obrigatório';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handler de mudanças
  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Limpar erro do campo
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  // Submeter formulário
  const handleSubmit = async () => {
    if (!validate()) return;

    setSubmitting(true);
    try {
      // Se há múltiplos emails, usar apenas o primeiro (backend aceita apenas 1)
      const recipientEmail = formData.recipient.split(/[,;]/)[0].trim();
      
      const payload = {
        contract_id: contractId,
        scheduled_for: format(formData.scheduled_for, "yyyy-MM-dd'T'HH:mm:ss"),
        recipient: recipientEmail,
        subject: formData.subject,
        custom_message: formData.custom_message || null
      };

      await alertsApi.createAlert(payload);
      showSuccess('Benutzerdefinierte Warnung erstellt / Alerta customizado criado');

      if (onSuccess) onSuccess();
      handleClose();
    } catch (error) {
      console.error('Error creating custom alert:', error);
      showError(
        error.response?.data?.detail || 
        'Fehler beim Erstellen / Erro ao criar'
      );
    } finally {
      setSubmitting(false);
    }
  };

  // Fechar dialog
  const handleClose = () => {
    setFormData({
      alert_type: 'BENUTZERDEFINIERT',
      scheduled_for: new Date(),
      recipient: '',
      subject: '',
      custom_message: ''
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>
        Benutzerdefinierte Warnung erstellen / Criar Alerta Customizado
      </DialogTitle>

      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Vertrag / Contrato:</strong> {contractTitle}
            </Typography>
            <Typography variant="caption">
              Erstellen Sie eine benutzerdefinierte Warnung für diesen Vertrag.
              <br />
              Crie um alerta customizado para este contrato.
            </Typography>
          </Alert>

          <Grid container spacing={2}>
            {/* Data/Hora de envio */}
            <Grid item xs={12}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={de}>
                <DateTimePicker
                  label="Sendedatum / Data de Envio *"
                  value={formData.scheduled_for}
                  onChange={(date) => handleChange('scheduled_for', date)}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      error: !!errors.scheduled_for,
                      helperText: errors.scheduled_for || 'Wann soll die Warnung gesendet werden? / Quando o alerta deve ser enviado?'
                    }
                  }}
                  minDateTime={new Date()}
                />
              </LocalizationProvider>
            </Grid>

            {/* Destinatário */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                type="text"
                label="Empfänger E-Mail / E-mail do Destinatário *"
                value={formData.recipient}
                onChange={(e) => handleChange('recipient', e.target.value)}
                error={!!errors.recipient}
                helperText={errors.recipient || 'Nur die erste E-Mail wird verwendet / Apenas o primeiro e-mail será usado'}
                placeholder="beispiel@firma.de"
              />
            </Grid>

            {/* Assunto */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                required
                label="Betreff / Assunto *"
                value={formData.subject}
                onChange={(e) => handleChange('subject', e.target.value)}
                error={!!errors.subject}
                helperText={errors.subject}
                placeholder="Vertragserinnerung / Lembrete de contrato"
              />
            </Grid>

            {/* Mensagem customizada */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Benutzerdefinierte Nachricht / Mensagem Customizada"
                value={formData.custom_message}
                onChange={(e) => handleChange('custom_message', e.target.value)}
                placeholder="Optionale zusätzliche Nachricht, die in der E-Mail enthalten sein wird. / Mensagem adicional opcional que será incluída no e-mail."
                helperText="Optional / Opcional"
              />
            </Grid>

            {/* Informações sobre permissões */}
            <Grid item xs={12}>
              <Alert severity="warning">
                <Typography variant="body2">
                  <strong>Hinweis / Nota:</strong> Die Warnung wird zum geplanten Zeitpunkt automatisch gesendet.
                  <br />
                  O alerta será enviado automaticamente no horário programado.
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={handleClose}
          disabled={submitting}
        >
          Abbrechen / Cancelar
        </Button>
        <Button 
          onClick={handleSubmit}
          variant="contained"
          disabled={submitting}
        >
          {submitting 
            ? 'Erstellen... / Criando...' 
            : 'Erstellen / Criar'
          }
        </Button>
      </DialogActions>
    </Dialog>
  );
};

CustomAlertForm.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  contractId: PropTypes.number.isRequired,
  contractTitle: PropTypes.string.isRequired,
  onSuccess: PropTypes.func
};

export default CustomAlertForm;
