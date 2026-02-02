import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, Button } from '@mui/material';

/**
 * PDFPreview
 * Componente para exibir preview inline de um PDF (via <iframe>)
 *
 * Props:
 * - src: string (URL do PDF)
 * - height: string|number (altura do preview)
 * - loading: boolean
 * - error: string
 */
const PDFPreview = ({ src, height = 500, loading = false, error = '', ...rest }) => {
  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body2" color="text.secondary">Carregando PDF...</Typography>
      </Box>
    );
  }
  if (error) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body2" color="error">{error}</Typography>
      </Box>
    );
  }
  if (!src) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body2" color="text.secondary">Nenhum PDF selecionado.</Typography>
      </Box>
    );
  }
  return (
    <Box sx={{ border: '1px solid #eee', borderRadius: 2, overflow: 'hidden', my: 2 }}>
      <iframe
        src={src}
        title="Visualização do PDF"
        width="100%"
        height={height}
        style={{ border: 'none' }}
        {...rest}
      />
    </Box>
  );
};

PDFPreview.propTypes = {
  src: PropTypes.string,
  height: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  loading: PropTypes.bool,
  error: PropTypes.string,
};

export default PDFPreview;
