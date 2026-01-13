/**
 * ContractDetail - Componente de Detalhes do Contrato
 * Vertragsdetail-Komponente
 * 
 * Exibe informações detalhadas de um contrato
 * Zeigt detaillierte Informationen eines Vertrags an
 */
import { useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import { format } from 'date-fns';
import { useAuthStore } from '../../store/authStore';
import {
  CONTRACT_STATUS_LABELS,
  CONTRACT_STATUS_LABELS_EN,
  CONTRACT_STATUS_COLORS,
  CONTRACT_TYPE_LABELS,
  CONTRACT_TYPE_LABELS_EN,
  LEGAL_FORM_LABELS,
  DATE_FORMAT
} from '../../utils/constants';

/**
 * Formata valor monetário
 * Formatiert Geldwert
 */
const formatCurrency = (value, currency = 'EUR') => {
  if (!value && value !== 0) return '-';
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: currency
  }).format(value);
};

/**
 * Formata data
 * Formatiert Datum
 */
const formatDate = (dateString) => {
  if (!dateString) return '-';
  try {
    return format(new Date(dateString), DATE_FORMAT);
  } catch {
    return dateString;
  }
};

/**
 * Formata data/hora
 * Formatiert Datum/Uhrzeit
 */
const formatDateTime = (dateString) => {
  if (!dateString) return '-';
  try {
    return format(new Date(dateString), 'dd.MM.yyyy HH:mm');
  } catch {
    return dateString;
  }
};

const ContractDetail = ({ contract }) => {
  const user = useAuthStore((state) => state.user);

  /**
   * Verifica se usuário pode ver valores financeiros
   * Prüft, ob Benutzer Finanzwerte sehen kann
   */
  const canSeeFinancialValues = useMemo(() => {
    if (!user) return false;
    return user.access_level === 5 || user.access_level === 4;
  }, [user]);

  if (!contract) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography>Keine Daten / No data</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Card Principal / Haupt-Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3}>
            {/* Título e Status / Titel und Status */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box>
                  <Typography variant="h5" gutterBottom>
                    {contract.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ID: {contract.id}
                  </Typography>
                </Box>
                <Chip
                  label={CONTRACT_STATUS_LABELS[contract.status]}
                  color={CONTRACT_STATUS_COLORS[contract.status] || 'default'}
                  title={CONTRACT_STATUS_LABELS_EN[contract.status]}
                />
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Divider />
            </Grid>

            {/* Informações Básicas / Grundinformationen */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Typ / Type
              </Typography>
              <Typography variant="body1" gutterBottom>
                {CONTRACT_TYPE_LABELS[contract.contract_type]}
                <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                  ({CONTRACT_TYPE_LABELS_EN[contract.contract_type]})
                </Typography>
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Partner
              </Typography>
              <Typography variant="body1">
                {contract.client_name || '-'}
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Firmenname / Company Name
              </Typography>
              <Typography variant="body1">
                {contract.company_name || '-'}
                {contract.company_name && contract.legal_form && (
                  <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                    ({LEGAL_FORM_LABELS[contract.legal_form] || contract.legal_form})
                  </Typography>
                )}
              </Typography>
            </Grid>

            {!contract.company_name && contract.legal_form && (
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Rechtsform / Legal Form
                </Typography>
                <Typography variant="body1">
                  {LEGAL_FORM_LABELS[contract.legal_form] || contract.legal_form}
                </Typography>
              </Grid>
            )}

            {/* Datas / Datum */}
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Startdatum / Start Date
              </Typography>
              <Typography variant="body1">
                {formatDate(contract.start_date)}
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Enddatum / End Date
              </Typography>
              <Typography variant="body1">
                {formatDate(contract.end_date)}
              </Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Verlängerungsdatum / Renewal Date
              </Typography>
              <Typography variant="body1">
                {formatDate(contract.renewal_date)}
              </Typography>
            </Grid>

            {/* Valor (condicional) / Wert (bedingt) */}
            {canSeeFinancialValues && (
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Wert / Value
                </Typography>
                <Typography variant="body1" fontWeight={600}>
                  {formatCurrency(contract.value, contract.currency)}
                </Typography>
              </Grid>
            )}

            {/* Descrição / Beschreibung */}
            {contract.description && (
              <>
                <Grid item xs={12}>
                  <Divider />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Beschreibung / Description
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {contract.description}
                  </Typography>
                </Grid>
              </>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* Informações do Parceiro / Partner-Informationen */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Partner-Informationen / Partner Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Dokument / Document
              </Typography>
              <Typography variant="body1">{contract.client_document || '-'}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                E-Mail
              </Typography>
              <Typography variant="body1">{contract.client_email || '-'}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Telefon / Phone
              </Typography>
              <Typography variant="body1">{contract.client_phone || '-'}</Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Adresse / Address
              </Typography>
              <Typography variant="body1">{contract.client_address || '-'}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Organização / Organisation */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Organisation / Organization
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Bereich / Department
              </Typography>
              <Typography variant="body1">{contract.department || '-'}</Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Team / Team
              </Typography>
              <Typography variant="body1">{contract.team || '-'}</Typography>
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Verantwortlicher Benutzer / Responsible User
              </Typography>
              <Typography variant="body1">
                {contract.responsible_user_id ? `User ID: ${contract.responsible_user_id}` : '-'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Termos e Condições / Geschäftsbedingungen */}
      {contract.terms_and_conditions && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Geschäftsbedingungen / Terms and Conditions
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {contract.terms_and_conditions}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Rent Steps (se existirem) / Mietstaffelungen (falls vorhanden) */}
      {contract.rent_steps && contract.rent_steps.length > 0 && canSeeFinancialValues && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Mietstaffelungen / Rent Steps
            </Typography>
            <Paper variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Datum / Date</TableCell>
                    <TableCell align="right">Betrag / Amount</TableCell>
                    <TableCell>Notiz / Note</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {contract.rent_steps.map((step, index) => (
                    <TableRow key={index}>
                      <TableCell>{formatDate(step.effective_date)}</TableCell>
                      <TableCell align="right">
                        {formatCurrency(step.amount, step.currency || contract.currency)}
                      </TableCell>
                      <TableCell>{step.note || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </CardContent>
        </Card>
      )}

      {/* Notas / Notizen */}
      {contract.notes && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Notizen / Notes
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
              {contract.notes}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Informações de Auditoria / Audit-Informationen */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Audit-Informationen / Audit Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Erstellt / Created
              </Typography>
              <Typography variant="body2">
                {formatDateTime(contract.created_at)}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Aktualisiert / Updated
              </Typography>
              <Typography variant="body2">
                {formatDateTime(contract.updated_at)}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" color="text.secondary">
                Erstellt von / Created by
              </Typography>
              <Typography variant="body2">
                {contract.created_by_name || `User ID: ${contract.created_by}`}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ContractDetail;
