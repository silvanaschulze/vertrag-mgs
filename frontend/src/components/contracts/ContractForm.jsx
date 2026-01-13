/**
 * ContractForm - Formulário de Contratos (Create/Edit)
 * Vertragsformular (Erstellen/Bearbeiten)
 * 
 * Formulário reutilizável para criar e editar contratos
 * Wiederverwendbares Formular zum Erstellen und Bearbeiten von Verträgen
 */
import { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Button,
  Grid,
  TextField,
  MenuItem,
  Typography,
  Paper
} from '@mui/material';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { 
  CONTRACT_STATUS, 
  CONTRACT_STATUS_LABELS,
  CONTRACT_TYPES,
  CONTRACT_TYPE_LABELS,
  LEGAL_FORMS,
  LEGAL_FORM_LABELS,
  PAYMENT_FREQUENCY,
  PAYMENT_FREQUENCY_LABELS,
  DEFAULT_CURRENCY
} from '../../utils/constants';
import { format, parseISO } from 'date-fns';

/**
 * Schema de validação Zod
 * Zod-Validierungsschema
 */
const contractSchema = z.object({
  title: z.string()
    .min(2, 'Title must have at least 2 characters')
    .max(200, 'Title must have max 200 characters'),
  
  client_name: z.string()
    .min(2, 'Partner name must have at least 2 characters')
    .max(200, 'Partner name must have max 200 characters'),
  
  company_name: z.string()
    .min(2, 'Company name must have at least 2 characters')
    .max(200, 'Company name must have max 200 characters')
    .optional()
    .nullable()
    .or(z.literal('')),
  
  legal_form: z.string()
    .optional()
    .nullable(),
  
  contract_type: z.string()
    .min(1, 'Contract type is required'),
  
  status: z.string()
    .min(1, 'Status is required'),
  
  start_date: z.string()
    .min(1, 'Start date is required'),
  
  end_date: z.string()
    .optional()
    .nullable(),
  
  renewal_date: z.string()
    .optional()
    .nullable(),
  
  value: z.number()
    .min(0, 'Value must be positive')
    .optional()
    .nullable(),
  
  currency: z.string()
    .length(3, 'Currency must be 3 characters')
    .default(DEFAULT_CURRENCY),
  
  description: z.string()
    .max(1000, 'Description must have max 1000 characters')
    .optional()
    .nullable(),
  
  client_document: z.string()
    .regex(/^[\d/-]*$/, 'Document must contain only numbers, / and -')
    .max(20, 'Document must have max 20 characters')
    .optional()
    .nullable()
    .or(z.literal('')),
  
  client_email: z.string()
    .email('Invalid email')
    .optional()
    .nullable()
    .or(z.literal('')),
  
  client_phone: z.string()
    .max(20, 'Phone must have max 20 characters')
    .optional()
    .nullable(),
  
  client_address: z.string()
    .max(300, 'Address must have max 300 characters')
    .optional()
    .nullable(),
  
  notes: z.string()
    .max(500, 'Notes must have max 500 characters')
    .optional()
    .nullable(),
  
  department: z.string()
    .max(100, 'Department must have max 100 characters')
    .optional()
    .nullable(),
  
  team: z.string()
    .max(100, 'Team must have max 100 characters')
    .optional()
    .nullable(),
  
  responsible_user_id: z.number()
    .optional()
    .nullable(),
  
  terms_and_conditions: z.string()
    .optional()
    .nullable(),
  
  payment_frequency: z.string()
    .optional()
    .nullable(),
  
  payment_custom_years: z.number()
    .min(1, 'Custom years must be at least 1')
    .max(100, 'Custom years must be max 100')
    .optional()
    .nullable(),
  
  pdfFile: z.any()
    .optional()
    .nullable()
});

/**
 * Valores padrão do formulário
 * Standard-Formularwerte
 */
const defaultValues = {
  title: '',
  client_name: '',
  company_name: '',
  legal_form: '',
  contract_type: CONTRACT_TYPES.OTHER,
  status: CONTRACT_STATUS.DRAFT,
  start_date: format(new Date(), 'yyyy-MM-dd'),
  end_date: '',
  renewal_date: '',
  value: null,
  currency: DEFAULT_CURRENCY,
  description: '',
  client_document: '',
  client_email: '',
  client_phone: '',
  client_address: '',
  notes: '',
  department: '',
  team: '',
  responsible_user_id: null,
  terms_and_conditions: '',
  payment_frequency: '',
  payment_custom_years: null,
  pdfFile: null
};

const ContractForm = ({ 
  initialData = null, 
  onSubmit, 
  onCancel,
  loading = false 
}) => {
  /**
   * React Hook Form setup
   */
  const {
    control,
    handleSubmit,
    formState: { errors, isDirty }
  } = useForm({
    resolver: zodResolver(contractSchema),
    defaultValues: initialData 
      ? {
          ...initialData,
          start_date: initialData.start_date 
            ? (typeof initialData.start_date === 'string' 
                ? initialData.start_date.split('T')[0] 
                : format(parseISO(initialData.start_date), 'yyyy-MM-dd'))
            : '',
          end_date: initialData.end_date 
            ? (typeof initialData.end_date === 'string' 
                ? initialData.end_date.split('T')[0] 
                : format(parseISO(initialData.end_date), 'yyyy-MM-dd'))
            : '',
          renewal_date: initialData.renewal_date 
            ? (typeof initialData.renewal_date === 'string' 
                ? initialData.renewal_date.split('T')[0] 
                : format(parseISO(initialData.renewal_date), 'yyyy-MM-dd'))
            : '',
          client_email: initialData.client_email || '',
          client_phone: initialData.client_phone || '',
          client_address: initialData.client_address || '',
          company_name: initialData.company_name || '',
          legal_form: initialData.legal_form || '',
          notes: initialData.notes || '',
          department: initialData.department || '',
          team: initialData.team || '',
          responsible_user_id: initialData.responsible_user_id || null,
          terms_and_conditions: initialData.terms_and_conditions || '',
          payment_frequency: initialData.payment_frequency || '',
          payment_custom_years: initialData.payment_custom_years || null
        }
      : defaultValues
  });

  // Estado para arquivo PDF e payment frequency
  const [pdfFile, setPdfFile] = useState(null);
  const [selectedPaymentFrequency, setSelectedPaymentFrequency] = useState(
    initialData?.payment_frequency || ''
  );

  const handleFormSubmit = (data) => {
    // Limpa campos vazios opcionais e garante null ao invés de strings vazias
    // Leert optionale leere Felder und garantiert null statt leere Strings
    const cleanedData = {
      title: data.title,
      client_name: data.client_name,
      company_name: data.company_name && data.company_name.trim() !== '' ? data.company_name : null,
      legal_form: data.legal_form && data.legal_form !== '' ? data.legal_form : null,
      contract_type: data.contract_type,
      status: data.status,
      start_date: data.start_date,
      end_date: data.end_date && data.end_date !== '' ? data.end_date : null,
      renewal_date: data.renewal_date && data.renewal_date !== '' ? data.renewal_date : null,
      value: data.value && data.value > 0 ? data.value : null,
      currency: data.currency || 'EUR',
      description: data.description && data.description.trim() !== '' ? data.description : null,
      client_document: data.client_document && data.client_document.trim() !== '' ? data.client_document : null,
      client_email: data.client_email && data.client_email.trim() !== '' ? data.client_email : null,
      client_phone: data.client_phone && data.client_phone.trim() !== '' ? data.client_phone : null,
      client_address: data.client_address && data.client_address.trim() !== '' ? data.client_address : null,
      notes: data.notes && data.notes.trim() !== '' ? data.notes : null,
      department: data.department && data.department.trim() !== '' ? data.department : null,
      team: data.team && data.team.trim() !== '' ? data.team : null,
      responsible_user_id: data.responsible_user_id || null,
      terms_and_conditions: data.terms_and_conditions && data.terms_and_conditions.trim() !== '' ? data.terms_and_conditions : null,
      payment_frequency: data.payment_frequency && data.payment_frequency !== '' ? data.payment_frequency : null,
      payment_custom_years: data.payment_custom_years && data.payment_custom_years > 0 ? data.payment_custom_years : null,
      pdfFile: pdfFile
    };

    onSubmit(cleanedData);
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Box component="form" onSubmit={handleSubmit(handleFormSubmit)}>
        <Grid container spacing={3}>
          {/* Informações Básicas / Grundlegende Informationen */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Grundlegende Informationen / Basic Information
            </Typography>
          </Grid>

          {/* Título / Titel */}
          <Grid item xs={12} md={8}>
            <Controller
              name="title"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Titel / Title *"
                  error={!!errors.title}
                  helperText={errors.title?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Status */}
          <Grid item xs={12} md={4}>
            <Controller
              name="status"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  select
                  fullWidth
                  label="Status *"
                  error={!!errors.status}
                  helperText={errors.status?.message}
                  disabled={loading}
                >
                  {Object.entries(CONTRACT_STATUS).map(([key, value]) => (
                    <MenuItem key={value} value={value}>
                      {CONTRACT_STATUS_LABELS[value]}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Grid>

          {/* Tipo / Typ */}
          <Grid item xs={12} md={6}>
            <Controller
              name="contract_type"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  select
                  fullWidth
                  label="Typ / Type *"
                  error={!!errors.contract_type}
                  helperText={errors.contract_type?.message}
                  disabled={loading}
                >
                  {Object.entries(CONTRACT_TYPES).map(([key, value]) => (
                    <MenuItem key={value} value={value}>
                      {CONTRACT_TYPE_LABELS[value]}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Grid>

          {/* Descrição / Beschreibung */}
          <Grid item xs={12}>
            <Controller
              name="description"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  multiline
                  rows={3}
                  label="Beschreibung / Description"
                  error={!!errors.description}
                  helperText={errors.description?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Upload de PDF / PDF-Upload */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 1 }}>
              Vertragsdokument / Contract Document *
            </Typography>
            <input
              accept="application/pdf"
              style={{ display: 'none' }}
              id="pdf-upload-button"
              type="file"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  if (file.type !== 'application/pdf') {
                    alert('Bitte wählen Sie nur PDF-Dateien / Please select PDF files only');
                    e.target.value = '';
                    return;
                  }
                  setPdfFile(file);
                }
              }}
              disabled={loading}
            />
            <label htmlFor="pdf-upload-button">
              <Button
                variant="outlined"
                component="span"
                disabled={loading}
                sx={{ mr: 2 }}
              >
                PDF auswählen / Select PDF
              </Button>
            </label>
            {pdfFile && (
              <Typography variant="body2" component="span" color="success.main">
                Ausgewählt / Selected: {pdfFile.name} ({(pdfFile.size / 1024 / 1024).toFixed(2)} MB)
              </Typography>
            )}
            {!pdfFile && !initialData && (
              <Typography variant="caption" color="error" display="block">
                * PDF-Upload ist obligatorisch / PDF upload is required
              </Typography>
            )}
          </Grid>

          {/* Parceiro / Partner */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Partner-Informationen / Partner Information
            </Typography>
          </Grid>

          {/* Nome do Parceiro / Partnername */}
          <Grid item xs={12} md={6}>
            <Controller
              name="client_name"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Partnername / Partner Name *"
                  error={!!errors.client_name}
                  helperText={errors.client_name?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Nome da Empresa / Firmenname */}
          <Grid item xs={12} md={6}>
            <Controller
              name="company_name"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  label="Firmenname / Company Name"
                  error={!!errors.company_name}
                  helperText={errors.company_name?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Forma Jurídica / Rechtsform */}
          <Grid item xs={12} md={6}>
            <Controller
              name="legal_form"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  select
                  fullWidth
                  label="Rechtsform / Legal Form"
                  error={!!errors.legal_form}
                  helperText={errors.legal_form?.message}
                  disabled={loading}
                >
                  <MenuItem value="">
                    <em>Keine / None</em>
                  </MenuItem>
                  {Object.entries(LEGAL_FORMS).map(([key, value]) => (
                    <MenuItem key={value} value={value}>
                      {LEGAL_FORM_LABELS[value]}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Grid>

          {/* Documento / Dokument */}
          <Grid item xs={12} md={6}>
            <Controller
              name="client_document"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  label="Dokument / Document"
                  placeholder="Tax ID, Register Nr."
                  error={!!errors.client_document}
                  helperText={errors.client_document?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Email */}
          <Grid item xs={12} md={4}>
            <Controller
              name="client_email"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  type="email"
                  label="E-Mail"
                  error={!!errors.client_email}
                  helperText={errors.client_email?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Telefone / Telefon */}
          <Grid item xs={12} md={4}>
            <Controller
              name="client_phone"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  label="Telefon / Phone"
                  error={!!errors.client_phone}
                  helperText={errors.client_phone?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Endereço / Adresse */}
          <Grid item xs={12} md={4}>
            <Controller
              name="client_address"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  label="Adresse / Address"
                  error={!!errors.client_address}
                  helperText={errors.client_address?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Datas e Valores / Datum und Werte */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Datum und Werte / Dates and Values
            </Typography>
          </Grid>

          {/* Data Início / Startdatum */}
          <Grid item xs={12} md={4}>
            <Controller
              name="start_date"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  type="date"
                  label="Startdatum / Start Date *"
                  InputLabelProps={{ shrink: true }}
                  error={!!errors.start_date}
                  helperText={errors.start_date?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Data Fim / Enddatum */}
          <Grid item xs={12} md={4}>
            <Controller
              name="end_date"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  type="date"
                  label="Enddatum / End Date"
                  InputLabelProps={{ shrink: true }}
                  error={!!errors.end_date}
                  helperText={errors.end_date?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Data Renovação / Verlängerungsdatum */}
          <Grid item xs={12} md={4}>
            <Controller
              name="renewal_date"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  type="date"
                  label="Verlängerungsdatum / Renewal Date"
                  InputLabelProps={{ shrink: true }}
                  error={!!errors.renewal_date}
                  helperText={errors.renewal_date?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Valor / Wert */}
          <Grid item xs={12} md={3}>
            <Controller
              name="value"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  onChange={(e) => {
                    const value = e.target.value === '' ? null : parseFloat(e.target.value);
                    field.onChange(value);
                  }}
                  fullWidth
                  type="number"
                  label="Wert / Value"
                  inputProps={{ step: '0.01', min: 0 }}
                  error={!!errors.value}
                  helperText={errors.value?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Moeda / Währung */}
          <Grid item xs={12} md={1}>
            <Controller
              name="currency"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Currency"
                  disabled
                  error={!!errors.currency}
                  helperText={errors.currency?.message}
                />
              )}
            />
          </Grid>

          {/* Frequência de Pagamento / Zahlungshäufigkeit */}
          <Grid item xs={12} md={4}>
            <Controller
              name="payment_frequency"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  select
                  fullWidth
                  label="Zahlungshäufigkeit / Payment Frequency"
                  error={!!errors.payment_frequency}
                  helperText={errors.payment_frequency?.message}
                  disabled={loading}
                  onChange={(e) => {
                    field.onChange(e);
                    setSelectedPaymentFrequency(e.target.value);
                  }}
                >
                  <MenuItem value="">
                    <em>Auswählen / Select</em>
                  </MenuItem>
                  {Object.entries(PAYMENT_FREQUENCY).map(([key, value]) => (
                    <MenuItem key={value} value={value}>
                      {PAYMENT_FREQUENCY_LABELS[value]}
                    </MenuItem>
                  ))}
                </TextField>
              )}
            />
          </Grid>

          {/* Anos Customizados / Benutzerdefinierte Jahre - Condicional */}
          {selectedPaymentFrequency === PAYMENT_FREQUENCY.CUSTOM_YEARS && (
            <Grid item xs={12} md={4}>
              <Controller
                name="payment_custom_years"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    value={field.value || ''}
                    onChange={(e) => {
                      const value = e.target.value === '' ? null : parseInt(e.target.value);
                      field.onChange(value);
                    }}
                    fullWidth
                    type="number"
                    label="Alle X Jahre / Every X Years"
                    inputProps={{ min: 1, max: 100, step: 1 }}
                    error={!!errors.payment_custom_years}
                    helperText={errors.payment_custom_years?.message}
                    disabled={loading}
                  />
                )}
              />
            </Grid>
          )}

          {/* Organização / Organisation */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Organisation / Organization
            </Typography>
          </Grid>

          <Grid item xs={12} md={4}>
            <Controller
              name="department"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  label="Bereich / Department"
                  error={!!errors.department}
                  helperText={errors.department?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <Controller
              name="team"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  label="Team / Team"
                  error={!!errors.team}
                  helperText={errors.team?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <Controller
              name="responsible_user_id"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  onChange={(e) => {
                    const value = e.target.value === '' ? null : parseInt(e.target.value);
                    field.onChange(value);
                  }}
                  fullWidth
                  type="number"
                  label="Verantwortlicher Benutzer ID / Responsible User ID"
                  error={!!errors.responsible_user_id}
                  helperText={errors.responsible_user_id?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Termos e Condições / Geschäftsbedingungen */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Geschäftsbedingungen / Terms and Conditions
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Controller
              name="terms_and_conditions"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  multiline
                  rows={4}
                  label="Geschäftsbedingungen / Terms and Conditions"
                  error={!!errors.terms_and_conditions}
                  helperText={errors.terms_and_conditions?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Notas / Notizen */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Notizen / Notes
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Controller
              name="notes"
              control={control}
              render={({ field }) => (
                <TextField
                  {...field}
                  value={field.value || ''}
                  fullWidth
                  multiline
                  rows={3}
                  label="Notizen / Notes"
                  error={!!errors.notes}
                  helperText={errors.notes?.message}
                  disabled={loading}
                />
              )}
            />
          </Grid>

          {/* Botões / Buttons */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
              <Button
                variant="outlined"
                startIcon={<CancelIcon />}
                onClick={onCancel}
                disabled={loading}
              >
                Abbrechen / Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={<SaveIcon />}
                disabled={loading || !isDirty}
              >
                {loading ? 'Speichern... / Saving...' : 'Speichern / Save'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default ContractForm;
