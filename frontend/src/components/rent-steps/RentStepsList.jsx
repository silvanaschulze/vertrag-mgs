import { useState, useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';
import { useNotification } from '../../hooks/useNotification';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Button,
  Chip,
  Alert,
  Tooltip,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  TrendingUp as TrendingUpIcon,
  CalendarToday as CalendarIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { format, parseISO, isFuture, isPast } from 'date-fns';
import { de } from 'date-fns/locale';
import { 
  getRentSteps, 
  deleteRentStep, 
  calculatePercentageIncrease,
  getNextRentStep
} from '../../services/rentStepsApi';
import { CURRENCY_SYMBOLS } from '../../utils/constants';
import RentStepForm from './RentStepForm';
import ConfirmDialog from '../ui/ConfirmDialog';
import PropTypes from 'prop-types';

/**
 * Lista de Rent Steps com CRUD
 * DE: Liste der Mietstaffelungen mit CRUD
 * PT: Lista de escalonamentos de aluguel com CRUD
 */
const RentStepsList = ({ contractId, currentRentAmount, currentCurrency = 'EUR', contractStartDate, contractEndDate, contractInitialValue }) => {
  const { user } = useAuthStore();
  const { showSuccess, showError } = useNotification();

  const [rentSteps, setRentSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [editingStep, setEditingStep] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [stepToDelete, setStepToDelete] = useState(null);
  const [projectionDialogOpen, setProjectionDialogOpen] = useState(false);
  const [stepToProject, setStepToProject] = useState(null);

  // Permissões: access_level >= 3 (TEAM_LEAD, MANAGER, DIRECTOR, SYSTEM_ADMIN)
  const canManage = user && user.access_level >= 3;

  // Carregar rent steps
  const isContractDataReady = !!contractStartDate && !!contractInitialValue;

  const loadRentSteps = async () => {
    try {
      setLoading(true);
      const data = await getRentSteps(contractId);
      setRentSteps(data);
    } catch (error) {
      console.error('Error loading rent steps:', error);
      showError('Fehler beim Laden der Mietstaffelungen / Erro ao carregar escalonamentos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (contractId) {
      loadRentSteps();
    }
  }, [contractId]);

  // Abrir formulário para criar
  const handleCreate = () => {
    // Só permite abrir se dados essenciais estiverem disponíveis
    if (!contractStartDate || !contractInitialValue) {
      // eslint-disable-next-line no-alert
      alert('Die Vertragsdaten wurden noch nicht geladen. Bitte warten Sie einige Sekunden und versuchen Sie es erneut.');
      return;
    }
    setEditingStep(null);
    setFormOpen(true);
  };


  // Handler para editar escalonamento
  const handleEdit = (step) => {
    setEditingStep(step);
    setFormOpen(true);
  };

  // Abrir dialog de projeções
  const handleViewProjection = (step) => {
    setStepToProject(step);
    setProjectionDialogOpen(true);
  };

  // Confirmar exclusão
  const handleDeleteClick = (step) => {
    setStepToDelete(step);
    setDeleteDialogOpen(true);
  };

  // Excluir rent step
  const handleDeleteConfirm = async () => {
    if (!stepToDelete) return;

    try {
      await deleteRentStep(contractId, stepToDelete.id);
      showSuccess('Mietstaffelung gelöscht / Escalonamento excluído');
      loadRentSteps();
    } catch (error) {
      console.error('Error deleting rent step:', error);
      showError('Fehler beim Löschen / Erro ao excluir');
    } finally {
      setDeleteDialogOpen(false);
      setStepToDelete(null);
    }
  };

  // Sucesso no formulário
  const handleFormSuccess = () => {
    loadRentSteps();
  };

  // Formatar moeda
  const formatCurrency = (amount, currency) => {
    const symbol = CURRENCY_SYMBOLS[currency] || currency;
    return `${symbol} ${parseFloat(amount).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  // Calcular aumento percentual
  const calculateIncrease = (index) => {
    if (index === 0) {
      // Primeiro step - comparar com rent atual do contrato
      if (currentRentAmount && rentSteps[0].amount) {
        return calculatePercentageIncrease(currentRentAmount, rentSteps[0].amount);
      }
      return null;
    }
    // Steps subsequentes - comparar com step anterior
    const prevAmount = rentSteps[index - 1].amount;
    const currentAmount = rentSteps[index].amount;
    return calculatePercentageIncrease(prevAmount, currentAmount);
  };

  // Status do step (passado, presente, futuro)
  const getStepStatus = (effectiveDate) => {
    const date = parseISO(effectiveDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (isPast(date) && date < today) {
      return { label: 'Aktiv / Ativo', color: 'success' };
    }
    if (isFuture(date)) {
      return { label: 'Geplant / Planejado', color: 'info' };
    }
    return { label: 'Heute / Hoje', color: 'warning' };
  };

  // Próximo aumento
  const nextStep = getNextRentStep(rentSteps);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography>Lade Mietstaffelungen... / Carregando escalonamentos...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Cabeçalho */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h6" gutterBottom>
            Mietstaffelungen / Escalonamentos de Aluguel
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Geplante Mieterhöhungen für diesen Vertrag / Aumentos de aluguel planejados para este contrato
          </Typography>
        </Box>
        {canManage && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
          >
            Hinzufügen / Adicionar
          </Button>
        )}
      </Box>

      {/* Alerta sobre próximo aumento */}
      {nextStep && (
        <Alert severity="info" icon={<CalendarIcon />} sx={{ mb: 2 }}>
          <Typography variant="body2">
            <strong>Nächste Mieterhöhung / Próximo Aumento:</strong>{' '}
            {formatCurrency(nextStep.amount, nextStep.currency)} ab{' '}
            {format(parseISO(nextStep.effective_date), 'dd.MM.yyyy', { locale: de })}
          </Typography>
        </Alert>
      )}

      {/* Tabela */}
      {rentSteps.length === 0 ? (
        <Alert severity="info">
          Keine Mietstaffelungen definiert. / Nenhum escalonamento definido.
          {canManage && ' Klicken Sie auf "Hinzufügen", um eine zu erstellen. / Clique em "Adicionar" para criar.'}
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Gültig ab / Data de Vigência</TableCell>
                <TableCell>Betrag / Valor</TableCell>
                <TableCell>Erhöhung / Aumento</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Anmerkungen / Observações</TableCell>
                <TableCell align="right">Aktionen / Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rentSteps.map((step, index) => {
                const status = getStepStatus(step.effective_date);
                const increase = calculateIncrease(index);

                return (
                  <TableRow key={step.id}>
                    {/* Data */}
                    <TableCell>
                      <Typography variant="body2">
                        {format(parseISO(step.effective_date), 'dd.MM.yyyy', { locale: de })}
                      </Typography>
                    </TableCell>

                    {/* Valor */}
                    <TableCell>
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(step.amount, step.currency)}
                      </Typography>
                    </TableCell>

                    {/* Aumento percentual */}
                    <TableCell>
                      {increase !== null && increase !== 0 && (
                        <Chip
                          icon={<TrendingUpIcon />}
                          label={`${increase > 0 ? '+' : ''}${increase.toFixed(2)}%`}
                          color={increase > 0 ? 'warning' : 'default'}
                          size="small"
                        />
                      )}
                    </TableCell>

                    {/* Status */}
                    <TableCell>
                      <Chip 
                        label={status.label} 
                        color={status.color} 
                        size="small" 
                      />
                    </TableCell>

                    {/* Observações */}
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {step.note || '-'}
                      </Typography>
                    </TableCell>

                    {/* Ações */}
                    <TableCell align="right">
                      <Tooltip title="Projektion anzeigen / Ver projeções">
                        <IconButton 
                          size="small" 
                          onClick={() => handleViewProjection(step)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {canManage && (
                        <>
                          <Tooltip title="Bearbeiten / Editar">
                            <IconButton 
                              size="small" 
                              onClick={() => handleEdit(step)}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Löschen / Excluir">
                            <IconButton 
                              size="small" 
                              color="error"
                              onClick={() => handleDeleteClick(step)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Formulário de criação/edição */}
      <RentStepForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditingStep(null);
        }}
        contractId={contractId}
        rentStep={editingStep}
        currentRentAmount={currentRentAmount}
        contractStartDate={contractStartDate}
        contractEndDate={contractEndDate}
        contractInitialValue={contractInitialValue}
        onSuccess={handleFormSuccess}
      />

      {/* Dialog de Projeções Futuras */}
      <Dialog
        open={projectionDialogOpen}
        onClose={() => setProjectionDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          📊 Projeção de Valores / Wertprojektion
        </DialogTitle>
        <DialogContent>
          {stepToProject && (
            <Box sx={{ pt: 2 }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Valor Base / Basiswert:</strong> {CURRENCY_SYMBOLS[stepToProject.currency]}{parseFloat(stepToProject.amount).toFixed(2)}
                </Typography>
                <Typography variant="body2">
                  <strong>Data de Vigência / Gültigkeitsdatum:</strong> {format(parseISO(stepToProject.effective_date), 'dd.MM.yyyy', { locale: de })}
                </Typography>
              </Alert>

              <Typography variant="subtitle2" gutterBottom>
                Projeções de aumento anual / Jährliche Erhöhungsprojektionen
              </Typography>
              <Typography variant="caption" color="textSecondary" gutterBottom display="block" sx={{ mb: 2 }}>
                Calcule quanto será o valor com diferentes percentuais de aumento / 
                Berechnen Sie, wie hoch der Wert bei verschiedenen Erhöhungsprozentsätzen sein wird
              </Typography>

              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Aumento / Erhöhung</strong></TableCell>
                      <TableCell align="right"><strong>1 ano</strong></TableCell>
                      <TableCell align="right"><strong>2 anos</strong></TableCell>
                      <TableCell align="right"><strong>3 anos</strong></TableCell>
                      <TableCell align="right"><strong>5 anos</strong></TableCell>
                      <TableCell align="right"><strong>10 anos</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {[2, 3, 5, 7, 10].map(percentage => (
                      <TableRow key={percentage}>
                        <TableCell>
                          <Chip 
                            label={`${percentage}%`} 
                            color="primary" 
                            size="small"
                            sx={{ fontWeight: 'bold' }}
                          />
                        </TableCell>
                        {[1, 2, 3, 5, 10].map(years => {
                          const baseAmount = parseFloat(stepToProject.amount);
                          const projectedValue = baseAmount * Math.pow(1 + (percentage / 100), years);
                          return (
                            <TableCell key={years} align="right">
                              <Typography variant="body2" fontWeight="medium">
                                {CURRENCY_SYMBOLS[stepToProject.currency]}{projectedValue.toFixed(2)}
                              </Typography>
                              <Typography variant="caption" color="success.dark">
                                +{((projectedValue - baseAmount) / baseAmount * 100).toFixed(1)}%
                              </Typography>
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProjectionDialogOpen(false)}>
            Schließen / Fechar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de confirmação de exclusão */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Mietstaffelung löschen? / Excluir Escalonamento?"
        message={
          stepToDelete
            ? `Möchten Sie die Mietstaffelung für ${format(parseISO(stepToDelete.effective_date), 'dd.MM.yyyy')} wirklich löschen? / Deseja realmente excluir o escalonamento de ${format(parseISO(stepToDelete.effective_date), 'dd.MM.yyyy')}?`
            : ''
        }
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setDeleteDialogOpen(false);
          setStepToDelete(null);
        }}
      />
    </Box>
  );
};

RentStepsList.propTypes = {
  contractId: PropTypes.number.isRequired,
  currentRentAmount: PropTypes.number,
  currentCurrency: PropTypes.string,
  contractStartDate: PropTypes.string,
  contractEndDate: PropTypes.string,
  contractInitialValue: PropTypes.number
};

export default RentStepsList;
