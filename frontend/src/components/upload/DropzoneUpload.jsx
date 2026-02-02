import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, Button } from '@mui/material';

/**
 * DropzoneUpload
 * Componente de upload de PDF com drag-and-drop
 *
 * Props:
 * - onFileAccepted: (file: File) => void
 * - accept: string (default: 'application/pdf')
 * - maxSize: number (bytes, default: 10MB)
 * - disabled: boolean
 * - helperText: string
 */
const DropzoneUpload = ({ onFileAccepted, accept = 'application/pdf', maxSize = 10 * 1024 * 1024, disabled = false, helperText }) => {
  const inputRef = React.useRef();
  const [dragActive, setDragActive] = React.useState(false);
  const [error, setError] = React.useState('');

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    validateAndSend(file);
  };

  const handleChange = (e) => {
    const file = e.target.files[0];
    validateAndSend(file);
  };

  const validateAndSend = (file) => {
    if (!file) return;
    if (accept && file.type !== accept) {
      setError('Nur PDF-Dateien sind erlaubt.');
      return;
    }
    if (file.size > maxSize) {
      setError('Datei überschreitet die maximale Größe von 10MB.');
      return;
    }
    setError('');
    onFileAccepted && onFileAccepted(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  return (
    <Box
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      sx={{
        border: dragActive ? '2px solid #1976d2' : '2px dashed #aaa',
        borderRadius: 2,
        p: 3,
        textAlign: 'center',
        bgcolor: dragActive ? '#e3f2fd' : '#fafafa',
        cursor: disabled ? 'not-allowed' : 'pointer',
        transition: 'border 0.2s, background 0.2s',
        outline: 'none',
        position: 'relative',
      }}
      tabIndex={0}
      aria-disabled={disabled}
      onClick={() => !disabled && inputRef.current && inputRef.current.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={handleChange}
        disabled={disabled}
        tabIndex={-1}
      />
      <Typography variant="body1" color={disabled ? 'text.disabled' : 'text.primary'}>
        PDF hierher ziehen und ablegen oder <Button variant="text" disabled={disabled}>klicken zum Auswählen</Button>
      </Typography>
      {helperText && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
          {helperText}
        </Typography>
      )}
      {error && (
        <Typography variant="caption" color="error" sx={{ mt: 1 }}>
          {error}
        </Typography>
      )}
    </Box>
  );
};

DropzoneUpload.propTypes = {
  onFileAccepted: PropTypes.func.isRequired,
  accept: PropTypes.string,
  maxSize: PropTypes.number,
  disabled: PropTypes.bool,
  helperText: PropTypes.string,
};

export default DropzoneUpload;
