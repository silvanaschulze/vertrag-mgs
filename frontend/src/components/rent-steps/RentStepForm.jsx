import React, { useState, useEffect } from 'react';
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
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
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
import de from 'date-fns/locale/de';
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
  contractStartDate = null,      // yyyy-MM-dd
  contractEndDate = null,        // yyyy-MM-dd
  contractInitialValue = 0,      // valor inicial do contrato
  onSuccess 
}) => {
  // DEBUG: Exibir props recebidas
  // eslint-disable-next-line no-console
  console.log('DEBUG RentStepForm props:', { contractStartDate, contractEndDate, contractInitialValue, currentRentAmount, rentStep });
  const { showSuccess, showError } = useNotification();
  const isEdit = !!rentStep;

  // Estado do formulário
  const [formData, setFormData] = useState({
    effective_date: rentStep?.effective_date ? new Date(rentStep.effective_date) : null,
    end_date: contractEndDate ? new Date(contractEndDate) : null,
    initial_value: contractInitialValue !== undefined && contractInitialValue !== null ? contractInitialValue : '',
    amount: rentStep?.amount !== undefined && rentStep?.amount !== null ? rentStep.amount : '',
    currency: rentStep?.currency || 'EUR',
    note: rentStep?.note || '',
    increase_percentage: '',
    periodicity: rentStep?.periodicity || 'annual',
    periods: 1
  });

  const [finalValue, setFinalValue] = useState('');
  const [retroSim, setRetroSim] = useState(null);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (open && !isEdit) {
      setFormData(prev => ({
        ...prev,
        effective_date: contractStartDate ? new Date(contractStartDate) : null,
        end_date: contractEndDate ? new Date(contractEndDate) : null,
        initial_value: contractInitialValue || '',
      }));
    }
    if (!open) {
      setFinalValue('');
      setRetroSim(null);
      setErrors({});
    }
  }, [open, contractStartDate, contractEndDate, contractInitialValue, isEdit]);

  // Simulação retroativa de aumento
  const handleRetroSimulate = () => {
    if (!formData.effective_date || !formData.end_date || !formData.initial_value || !finalValue) return;
    const start = new Date(formData.effective_date);
    const end = new Date(formData.end_date);
    const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
    const years = months / 12;
    const vi = parseFloat(formData.initial_value);
    const vf = parseFloat(finalValue);
    if (vi <= 0 || vf <= 0 || years <= 0) return;
    const pctTotal = ((vf / vi - 1) * 100).toFixed(2);
    const pctAnual = ((Math.pow(vf / vi, 1 / years) - 1) * 100).toFixed(2);
    const pctMensal = ((Math.pow(vf / vi, 1 / months) - 1) * 100).toFixed(2);
    setRetroSim({
      pctTotal,
      pctAnual,
      pctMensal,
      anos: years.toFixed(2),
      meses: months
    });
  };


  // Validação simples (agora no escopo do componente)
  const validate = () => {
    const errs = {};
    if (!formData.effective_date) errs.effective_date = 'Obrigatório / Erforderlich';
    // amount NÃO é mais obrigatório se modo retroativo (valor será calculado)
    // Só exige amount se modo for "manual" ou "porcentagem" e não houver simulação retroativa
    // Se valor final e inicial e datas estão preenchidos, amount pode ser vazio
    const retroativoPreenchido = formData.initial_value && finalValue && formData.effective_date && formData.end_date;
    if (!retroativoPreenchido && (formData.amount === undefined || formData.amount === null || formData.amount === '' || Number(formData.amount) <= 0)) {
      errs.amount = 'Obrigatório / Erforderlich';
    }
    if (!formData.currency) errs.currency = 'Obrigatório / Erforderlich';
    if (!formData.periodicity || (formData.periodicity !== 'monthly' && formData.periodicity !== 'annual')) errs.periodicity = 'Obrigatório / Erforderlich';
    return errs;
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

  // Renderização dos campos extras para retroativa e projeção
  {/* Valor Inicial do Contrato */}
  <Grid item xs={12} sm={6}>
    <TextField
      fullWidth
      label="Anfangsbetrag / Valor Inicial"
      value={contractInitialValue || ''}
      InputProps={{ readOnly: true }}
      helperText="Wert zu Vertragsbeginn / Valor no início do contrato"
    />
  </Grid>
  {/* Valor Final para simulação retroativa */}
  <Grid item xs={12} sm={6}>
    <TextField
      fullWidth
      label="Endbetrag / Valor Final"
      value={finalValue}
      onChange={e => setFinalValue(e.target.value)}
      type="number"
      inputProps={{ min: 0, step: 0.01 }}
      helperText="Letzter gezahlter Wert / Último valor pago"
    />
  </Grid>
  {/* Botão para simular aumento retroativo */}
  <Grid item xs={12}>
    <Button
      variant="outlined"
      onClick={handleRetroSimulate}
      disabled={!contractStartDate || !contractEndDate || !contractInitialValue || !finalValue}
      sx={{ mb: 1 }}
    >
      Retroaktive Erhöhung simulieren / Simular aumento retroativo
    </Button>
    {retroSim && (
      <Alert severity="info" sx={{ mt: 1 }}>
        <Typography variant="body2">
          <strong>Retroaktive Erhöhung / Aumento retroativo:</strong><br />
          Zeitraum / Período: <b>{retroSim.anos} Jahre / anos</b> ({retroSim.meses} Monate / meses)<br />
          Gesamterhöhung / Aumento total: <b>{retroSim.pctTotal}%</b><br />
          Durchschnitt pro Jahr / Média por ano: <b>{retroSim.pctAnual}%</b><br />
          Durchschnitt pro Monat / Média por mês: <b>{retroSim.pctMensal}%</b>
        </Typography>
      </Alert>
    )}
  </Grid>

  // Handler de submissão
  const handleSubmit = async () => {
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) {
      console.warn('Validação falhou:', errs);
      return;
    }
    setSubmitting(true);
    try {
      // Se amount não foi informado, calcular automaticamente se possível
      let amount = formData.amount !== undefined && formData.amount !== '' ? parseFloat(formData.amount) : undefined;
      if ((amount === undefined || isNaN(amount) || amount <= 0) && formData.initial_value && finalValue) {
        // Cálculo retroativo: usar valor final
        amount = parseFloat(finalValue);
      }
      if (amount === undefined || isNaN(amount) || amount <= 0) {
        showError('Valor do escalonamento não informado ou inválido. Preencha manualmente ou use a simulação.');
        setSubmitting(false);
        return;
      }
      const payload = {
        effective_date: formData.effective_date ? format(formData.effective_date, 'yyyy-MM-dd') : null,
        amount: amount,
        currency: formData.currency,
        note: formData.note || null
      };
      // Log do payload enviado
      // eslint-disable-next-line no-console
      console.log('Enviando payload para createRentStep:', payload);

      let response;
      if (isEdit) {
        response = await updateRentStep(contractId, rentStep.id, payload);
        showSuccess('Mietstaffelung aktualisiert / Escalonamento atualizado');
      } else {
        response = await createRentStep(contractId, payload);
        showSuccess('Mietstaffelung erstellt / Escalonamento criado');
      }
      // Log da resposta
      // eslint-disable-next-line no-console
      console.log('Resposta da API:', response);

      if (onSuccess) onSuccess();
      handleClose();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Erro ao submeter rent step:', error, error?.response);
      let backendMsg = 'Erro desconhecido';
      if (error?.response?.data) {
        if (typeof error.response.data === 'string') {
          backendMsg = error.response.data;
        } else if (error.response.data.detail) {
          backendMsg = error.response.data.detail;
        } else if (error.response.data.errors) {
          backendMsg = JSON.stringify(error.response.data.errors);
        } else {
          backendMsg = JSON.stringify(error.response.data);
        }
      } else if (error?.message) {
        backendMsg = error.message;
      }
      showError(
        backendMsg || 'Fehler beim Speichern / Erro ao salvar'
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
            {/* Data efetiva (Startdatum) */}
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={de}>
                <DatePicker
                  label="Data Inicial / Startdatum *"
                  value={formData.effective_date}
                  onChange={date => handleChange('effective_date', date)}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </LocalizationProvider>
            </Grid>
            {/* Data Final (end_date) */}
            <Grid item xs={12} sm={6}>
              <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={de}>
                <DatePicker
                  label="Data Final / Enddatum"
                  value={formData.end_date}
                  onChange={date => handleChange('end_date', date)}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </LocalizationProvider>
            </Grid>

            {/* Modo de cálculo: Manual ou Porcentagem */}
            {!isEdit && currentRentAmount > 0 && (
              <>
                <Grid item xs={12} sm={8}>
                  <Alert severity="info" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ flex: 1 }}>
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

                {/* CAMPOS RETROATIVOS: manual */}
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Anfangswert"
                    value={formData.initial_value}
                    onChange={e => handleChange('initial_value', e.target.value)}
                    type="number"
                    inputProps={{ min: 0, step: 0.01 }}
                    helperText="Geben Sie den Anfangswert des Vertrags manuell ein"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Endwert"
                    value={finalValue}
                    onChange={e => setFinalValue(e.target.value)}
                    type="number"
                    inputProps={{ min: 0, step: 0.01 }}
                    helperText="Zuletzt gezahlter Betrag bzw. aktueller Wert"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleRetroSimulate}
                    disabled={!formData.effective_date || !formData.end_date || !formData.initial_value || !finalValue}
                    sx={{ mb: 1 }}
                  >
                    Simular Retroativo
                  </Button>
                  {retroSim && (
                    <Alert severity="info" sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        <strong>Retroativo:</strong><br />
                        Periode: <b>{retroSim.anos} Jahre</b> ({retroSim.meses} Monate)<br />
                        % totaler Erhöhung: <b>{retroSim.pctTotal}%</b><br />
                        % äquivalente jährlich: <b>{retroSim.pctAnual}%</b><br />
                        % äquivalente monatlich: <b>{retroSim.pctMensal}%</b>
                      </Typography>
                    </Alert>
                  )}
                </Grid>

                {/* Campos de Porcentagem e Projeção Futura */}
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Erhöhung (%)"
                    type="number"
                    value={formData.increase_percentage}
                    onChange={e => handleChange('increase_percentage', e.target.value)}
                    inputProps={{ min: -100, max: 1000, step: 0.1 }}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    select
                    label="Periodizität"
                    value={formData.periodicity || 'annual'}
                    onChange={e => handleChange('periodicity', e.target.value)}
                  >
                    <MenuItem value="monthly">Monatlich</MenuItem>
                    <MenuItem value="annual">Jährlich</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    fullWidth
                    label="Perioden"
                    type="number"
                    value={formData.periods}
                    onChange={e => handleChange('periods', e.target.value)}
                    inputProps={{ min: 1, max: 120, step: 1 }}
                    helperText={formData.periodicity === 'monthly' ? 'Monate' : 'Jahre'}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => {
                      // Zukünftige Simulation
                      // Apenas atualiza o campo amount
                      if (formData.increase_percentage && formData.periods) {
                        const pct = parseFloat(formData.increase_percentage) / 100;
                        const val = parseFloat(formData.initial_value);
                        const future = val * Math.pow(1 + pct, formData.periods);
                        setFormData(prev => ({ ...prev, amount: future.toFixed(2) }));
                      }
                    }}
                    sx={{ mb: 1 }}
                  >
                    Simular Futuro
                  </Button>
                  {formData.amount && (
                    <Alert severity="success" sx={{ mt: 1 }}>
                      <Typography variant="body2">
                        <strong>Zukünftige Projektion:</strong> Wert nach {formData.periods} {formData.periodicity === 'monthly' ? 'Monaten' : 'Jahren'}: <b>€{formData.amount}</b>
                      </Typography>
                    </Alert>
                  )}
                </Grid>
                          {/* Explicação da lógica de cálculo */}
                          <Grid item xs={12}>
                            <Alert severity="info">
                              <Typography variant="body2">
                                <strong>Wie die Berechnung funktioniert:</strong><br />
                                <u>Retroaktiv:</u> Geben Sie den Anfangswert, den Endwert und die Zeiträume an. Das System berechnet den gesamten Erhöhungsprozentsatz % , den jährlichen Prozentsatz % und den entsprechenden monatlichen % Prozentsatz.<br />
                                <u>Zukünftig:</u> Geben Sie den Erhöhungsprozentsatz % , die Periodizität und die Perioden an. Das System projiziert den zukünftigen Wert mit der Formel:<br />
                                <span style={{ fontFamily: 'monospace' }}>Zukünftiger Wert = Anfangswert × (1 + %/100)<sup>Perioden</sup></span>
                              </Typography>
                            </Alert>
                          </Grid>
              </>
            )}

            {/* Valor e moeda removidos daqui, pois já exibidos acima ao lado de Aktueller Betrag */}

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
