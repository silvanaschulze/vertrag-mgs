import { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Typography,
  Alert,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { de } from 'date-fns/locale';
import { format } from 'date-fns';
import { CURRENCIES, CURRENCY_LABELS } from '../../utils/constants';
import { createRentStep, updateRentStep } from '../../services/rentStepsApi';
import { useNotification } from '../../hooks/useNotification';

/**
 * Formulário para criar ou editar um Rent Step
 * DE: Formular zum Erstellen oder Bearbeiten einer Mietstaffelung
 * PT: Formulário para criar ou editar um escalonamento de aluguel
 */
const RentStepForm = ({ 
  open, 
  onClose, 
  contractId, 
  rentStep = null,
  currentRentAmount = 0,
  onSuccess 
}) => {
  const { showSuccess, showError } = useNotification();
  const isEdit = !!rentStep;

  // Estado do formulário
  const [formData, setFormData] = useState({
    effective_date: rentStep?.effective_date ? new Date(rentStep.effective_date) : null,
    amount: rentStep?.amount || '',
    currency: rentStep?.currency || 'EUR',
    note: rentStep?.note || '',
    use_percentage: false,
    increase_percentage: '',
    periodicity: 'annual', // mensal, trimestral, semestral, anual
    periods: 1 // número de períodos
  });

  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  // Calcular valor baseado na porcentagem e periodicidade
  const calculateAmountFromPercentage = (percentage, periodicity, periods) => {
    if (!currentRentAmount || !percentage || !periods) return '';
    
    const rate = parseFloat(percentage) / 100;
    const numPeriods = parseInt(periods) || 1;
    
    // Calcular aumento composto: valor_inicial * (1 + taxa)^períodos
    const finalAmount = parseFloat(currentRentAmount) * Math.pow(1 + rate, numPeriods);
    
    return finalAmount.toFixed(2);
  };

  // Validação
  const validate = () => {
    const newErrors = {};

    if (!formData.effective_date) {
      newErrors.effective_date = 'Datum erforderlich / Data obrigatória';
    }

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = 'Betrag muss größer als 0 sein / Valor deve ser maior que 0';
    }

    if (!formData.currency) {
      newErrors.currency = 'Währung erforderlich / Moeda obrigatória';
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
      const payload = {
        effective_date: format(formData.effective_date, 'yyyy-MM-dd'),
        amount: parseFloat(formData.amount),
        currency: formData.currency,
        note: formData.note || null
      };

      if (isEdit) {
        await updateRentStep(contractId, rentStep.id, payload);
        showSuccess('Mietstaffelung aktualisiert / Escalonamento atualizado');
      } else {
        await createRentStep(contractId, payload);
        showSuccess('Mietstaffelung erstellt / Escalonamento criado');
      }

      if (onSuccess) onSuccess();
      handleClose();
    } catch (error) {
      console.error('Error submitting rent step:', error);
      showError(
        error.response?.data?.detail || 
        'Fehler beim Speichern / Erro ao salvar'
      );
    } finally {
      setSubmitting(false);
    }
  };

  // Fechar dialog
  const handleClose = () => {
    setFormData({
      effective_date: null,
      amount: '',
      currency: 'EUR',
      note: ''
    });
    setErrors({});
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>
        {isEdit 
          ? 'Mietstaffelung bearbeiten / Editar Escalonamento'
          : 'Neue Mietstaffelung / Novo Escalonamento'
        }
      </DialogTitle>

      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            {/* Data efetiva */}
            <Grid item xs={12}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={de}>
                <DatePicker
                  label="Gültig ab / Data de Vigência *"
                  value={formData.effective_date}
                  onChange={(date) => handleChange('effective_date', date)}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      error: !!errors.effective_date,
                      helperText: errors.effective_date
                    }
                  }}
                />
              </LocalizationProvider>
              <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                Ab diesem Datum gilt der neue Mietbetrag / A partir desta data vigora o novo valor
              </Typography>
            </Grid>

            {/* Modo de cálculo: Manual ou Porcentagem */}
            {!isEdit && currentRentAmount > 0 && (
              <>
                <Grid item xs={12}>
                  <Alert severity="info" sx={{ mb: 1 }}>
                    <Typography variant="body2">
                      <strong>Aktueller Betrag / Valor Atual:</strong> €{parseFloat(currentRentAmount).toFixed(2)}
                    </Typography>
                  </Alert>
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    select
                    label="Berechnungsmodus / Modo de Cálculo"
                    value={formData.use_percentage ? 'percentage' : 'manual'}
                    onChange={(e) => {
                      const usePercentage = e.target.value === 'percentage';
                      setFormData(prev => ({
                        ...prev,
                        use_percentage: usePercentage,
                        amount: usePercentage && prev.increase_percentage 
                          ? calculateAmountFromPercentage(prev.increase_percentage, prev.periodicity, prev.periods)
                          : prev.amount,
                        increase_percentage: usePercentage ? prev.increase_percentage : '',
                        periodicity: usePercentage ? prev.periodicity : 'annual',
                        periods: usePercentage ? prev.periods : 1
                      }));
                    }}
                  >
                    <MenuItem value="manual">Manuell / Manual</MenuItem>
                    <MenuItem value="percentage">Prozentsatz / Porcentagem</MenuItem>
                  </TextField>
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                    Wählen Sie, ob Sie den Betrag manuell eingeben oder anhand eines Prozentsatzes berechnen möchten / 
                    Escolha se deseja inserir o valor manualmente ou calcular por porcentagem
                  </Typography>
                </Grid>

                {/* Campos de Porcentagem - aparecem apenas se use_percentage = true */}
                {formData.use_percentage && (
                  <>
                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="Erhöhung / Aumento (%)"
                        type="number"
                        value={formData.increase_percentage}
                        onChange={(e) => {
                          const percentage = e.target.value;
                          setFormData(prev => ({
                            ...prev,
                            increase_percentage: percentage,
                            amount: percentage ? calculateAmountFromPercentage(percentage, prev.periodicity, prev.periods) : ''
                          }));
                        }}
                        inputProps={{
                          min: -100,
                          max: 1000,
                          step: 0.1
                        }}
                      />
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        select
                        label="Periodizität / Periodicidade"
                        value={formData.periodicity}
                        onChange={(e) => {
                          const periodicity = e.target.value;
                          setFormData(prev => ({
                            ...prev,
                            periodicity,
                            amount: prev.increase_percentage ? calculateAmountFromPercentage(prev.increase_percentage, periodicity, prev.periods) : ''
                          }));
                        }}
                      >
                        <MenuItem value="monthly">Monatlich / Mensal</MenuItem>
                        <MenuItem value="quarterly">Vierteljährlich / Trimestral</MenuItem>
                        <MenuItem value="semiannual">Halbjährlich / Semestral</MenuItem>
                        <MenuItem value="annual">Jährlich / Anual</MenuItem>
                      </TextField>
                    </Grid>

                    <Grid item xs={12} sm={4}>
                      <TextField
                        fullWidth
                        label="Perioden / Períodos"
                        type="number"
                        value={formData.periods}
                        onChange={(e) => {
                          const periods = e.target.value;
                          setFormData(prev => ({
                            ...prev,
                            periods,
                            amount: prev.increase_percentage ? calculateAmountFromPercentage(prev.increase_percentage, prev.periodicity, periods) : ''
                          }));
                        }}
                        inputProps={{
                          min: 1,
                          max: 120,
                          step: 1
                        }}
                        helperText={
                          formData.periodicity === 'monthly' ? 'Monate / Meses' :
                          formData.periodicity === 'quarterly' ? 'Quartale / Trimestres' :
                          formData.periodicity === 'semiannual' ? 'Halbjahre / Semestres' :
                          'Jahre / Anos'
                        }
                      />
                    </Grid>

                    <Grid item xs={12}>
                      <Alert severity="success">
                        <Typography variant="body2">
                          <strong>Berechnung / Cálculo:</strong> 
                          {' '}€{parseFloat(currentRentAmount).toFixed(2)} × (1 + {formData.increase_percentage || 0}%)
                          <sup>{formData.periods || 1}</sup>
                          {' '}= <strong>€{formData.amount || '0.00'}</strong>
                        </Typography>
                        <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5, display: 'block' }}>
                          {formData.increase_percentage && formData.periods > 1 ? (
                            <>
                              Zusammengesetzter Zinseffekt über {formData.periods}{' '}
                              {formData.periodicity === 'monthly' ? 'Monate / meses' :
                               formData.periodicity === 'quarterly' ? 'Quartale / trimestres' :
                               formData.periodicity === 'semiannual' ? 'Halbjahre / semestres' :
                               'Jahre / anos'}
                            </>
                          ) : (
                            'Einfache Erhöhung / Aumento simples'
                          )}
                        </Typography>
                      </Alert>
                    </Grid>

                    {/* Tabela de Projeções */}
                    {formData.increase_percentage && (
                      <Grid item xs={12}>
                        <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'action.hover' }}>
                          <Typography variant="subtitle2" gutterBottom>
                            📊 Projeção de Valores / Wertprojektion
                          </Typography>
                          <Typography variant="caption" color="textSecondary" gutterBottom display="block">
                            {formData.periodicity === 'monthly' ? 'Nach Monaten / Por meses' :
                             formData.periodicity === 'quarterly' ? 'Nach Quartalen / Por trimestres' :
                             formData.periodicity === 'semiannual' ? 'Nach Halbjahren / Por semestres' :
                             'Nach Jahren / Por anos'}
                          </Typography>
                          <Box sx={{ mt: 1 }}>
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell><strong>Periode / Período</strong></TableCell>
                                  <TableCell align="right"><strong>Betrag / Valor</strong></TableCell>
                                  <TableCell align="right"><strong>Gesamterhöhung / Aumento Total</strong></TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {[1, 2, 3, 5, 10].map(p => {
                                  const projectedValue = calculateAmountFromPercentage(formData.increase_percentage, formData.periodicity, p);
                                  const totalIncrease = ((parseFloat(projectedValue) - parseFloat(currentRentAmount)) / parseFloat(currentRentAmount) * 100).toFixed(2);
                                  const isSelected = p === parseInt(formData.periods);
                                  return (
                                    <TableRow 
                                      key={p}
                                      sx={{ 
                                        backgroundColor: isSelected ? 'primary.light' : 'inherit'
                                      }}
                                    >
                                      <TableCell sx={{ fontWeight: isSelected ? 'bold' : 'normal' }}>
                                        {p}{' '}
                                        {formData.periodicity === 'monthly' ? (p === 1 ? 'mês' : 'meses') :
                                         formData.periodicity === 'quarterly' ? (p === 1 ? 'trimestre' : 'trimestres') :
                                         formData.periodicity === 'semiannual' ? (p === 1 ? 'semestre' : 'semestres') :
                                         (p === 1 ? 'ano' : 'anos')}
                                        {isSelected && ' ⬅️'}
                                      </TableCell>
                                      <TableCell align="right" sx={{ fontWeight: isSelected ? 'bold' : 'normal' }}>
                                        €{projectedValue}
                                      </TableCell>
                                      <TableCell 
                                        align="right" 
                                        sx={{ 
                                          color: 'success.dark',
                                          fontWeight: 'bold'
                                        }}
                                      >
                                        +{totalIncrease}%
                                      </TableCell>
                                    </TableRow>
                                  );
                                })}
                              </TableBody>
                            </Table>
                          </Box>
                        </Paper>
                      </Grid>
                    )}
                  </>
                )}
              </>
            )}

            {/* Valor */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Betrag / Valor *"
                type="number"
                value={formData.amount}
                onChange={(e) => handleChange('amount', e.target.value)}
                error={!!errors.amount}
                helperText={errors.amount || (formData.use_percentage ? 'Automatisch berechnet / Calculado automaticamente' : '')}
                disabled={formData.use_percentage}
                inputProps={{
                  min: 0,
                  step: 0.01
                }}
              />
            </Grid>

            {/* Moeda */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                select
                label="Währung / Moeda *"
                value={formData.currency}
                onChange={(e) => handleChange('currency', e.target.value)}
                error={!!errors.currency}
                helperText={errors.currency}
              >
                {Object.entries(CURRENCIES).map(([key, value]) => (
                  <MenuItem key={value} value={value}>
                    {CURRENCY_LABELS[value]}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Observações */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Anmerkungen / Observações"
                value={formData.note}
                onChange={(e) => handleChange('note', e.target.value)}
                placeholder="Optionale Anmerkungen zu dieser Mieterhöhung / Observações opcionais sobre este aumento"
              />
            </Grid>

            {/* Informação sobre permissões */}
            {!isEdit && (
              <Grid item xs={12}>
                <Alert severity="info">
                  <Typography variant="body2">
                    <strong>Hinweis / Nota:</strong> Nur Manager und Administratoren können Mietstaffelungen erstellen.
                    <br />
                    Somente Gerentes e Administradores podem criar escalonamentos.
                  </Typography>
                </Alert>
              </Grid>
            )}
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
            ? 'Speichern... / Salvando...' 
            : (isEdit ? 'Aktualisieren / Atualizar' : 'Erstellen / Criar')
          }
        </Button>
      </DialogActions>
    </Dialog>
  );
};

RentStepForm.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  contractId: PropTypes.number.isRequired,
  rentStep: PropTypes.shape({
    id: PropTypes.number,
    effective_date: PropTypes.string,
    amount: PropTypes.number,
    currency: PropTypes.string,
    note: PropTypes.string
  }),
  currentRentAmount: PropTypes.number,
  onSuccess: PropTypes.func
};

export default RentStepForm;
