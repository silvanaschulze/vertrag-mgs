import React, { useState } from 'react';
import { Box, Typography, Button, CircularProgress, Paper, Stepper, Step, StepLabel, Alert } from '@mui/material';
import DropzoneUpload from './DropzoneUpload';
import PDFPreview from './PDFPreview';
import ExtractedDataForm from './ExtractedDataForm';
import importApi from '../../services/importApi';

/**
 * ImportPage.jsx
 * Página principal do fluxo de importação de PDF de contrato
 * Passos: Upload → Preview → Editar Dados → Salvar
 */
const steps = ['PDF hochladen', 'PDF anzeigen', 'Daten bearbeiten', 'Vertrag speichern'];

const ImportPage = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [file, setFile] = useState(null);
  const [extracted, setExtracted] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // 1. Upload PDF
  const handleFileAccepted = async (file) => {
    setFile(file);
    setLoading(true);
    setError('');
    try {
      const result = await importApi.uploadPDF(file);
      setExtracted(result.extracted_data);
      setFormData({ ...result.extracted_data });
      setActiveStep(1);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Fehler beim Extrahieren der PDF-Daten.');
    } finally {
      setLoading(false);
    }
  };

  // 2. Avançar para edição
  const handleContinue = () => {
    setActiveStep(2);
  };

  // 3. Salvar contrato
  const handleSave = async () => {
    setLoading(true);
    setError('');
    try {
      const payload = { ...formData, original_file_storage_name: extracted.original_file_storage_name };
      await importApi.confirmImport(payload);
      setSuccess(true);
      setActiveStep(3);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Fehler beim Speichern des Vertrags.');
    } finally {
      setLoading(false);
    }
  };

  // 4. Resetar fluxo
  const handleReset = () => {
    setFile(null);
    setExtracted(null);
    setFormData({});
    setActiveStep(0);
    setError('');
    setSuccess(false);
  };

  return (
    <Paper sx={{ maxWidth: 700, mx: 'auto', mt: 4, p: 3 }}>
      <Typography variant="h5" gutterBottom>Vertrag importieren (PDF)</Typography>
      <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 3 }}>
        {steps.map((label) => (
          <Step key={label}><StepLabel>{label}</StepLabel></Step>
        ))}
      </Stepper>
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {activeStep === 0 && (
        <DropzoneUpload onFileAccepted={handleFileAccepted} disabled={loading} helperText="Nur PDF-Dateien bis 10MB." />
      )}
      {activeStep === 1 && extracted && (
        <>
          {/* Preview entfernt: kein temporärer PDF-Preview-Endpunkt */}
          <Button variant="contained" onClick={handleContinue} sx={{ mt: 2 }}>Daten bearbeiten</Button>
        </>
      )}
      {activeStep === 2 && (
        <>
          {/* Preview wird nur angezeigt, wenn eine echte contract_id existiert */}
          <ExtractedDataForm data={formData} onChange={setFormData} disabled={loading} />
          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <Button variant="contained" onClick={handleSave} disabled={loading}>Vertrag speichern</Button>
            <Button variant="outlined" onClick={handleReset} disabled={loading}>Abbrechen</Button>
          </Box>
        </>
      )}
      {activeStep === 3 && success && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="success.main">Vertrag erfolgreich importiert!</Typography>
          <Button variant="outlined" onClick={handleReset} sx={{ mt: 2 }}>Weiteren Vertrag importieren</Button>
        </Box>
      )}
      {loading && <CircularProgress sx={{ position: 'absolute', top: 24, right: 24 }} />}
    </Paper>
  );
};

export default ImportPage;
