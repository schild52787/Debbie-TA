import React from 'react';
import { Container, Typography, Paper, Box, Alert } from '@mui/material';

function Disputes() {
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Dispute Management
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        The system automatically scans your Gmail for dispute-related emails every hour.
      </Alert>

      <Paper sx={{ p: 3 }}>
        <Typography variant="body1" gutterBottom>
          Dispute management features:
        </Typography>
        <Box component="ul" sx={{ mt: 2 }}>
          <li>Automatic email scanning for cancellations, delays, and issues</li>
          <li>Legal research (DOT regulations, EU261, airline policies)</li>
          <li>Social media research for successful dispute strategies</li>
          <li>Auto-generated dispute claim letters</li>
          <li>Track dispute status and outcomes</li>
          <li>Support for airlines, hotels, and cruises</li>
        </Box>
      </Paper>
    </Container>
  );
}

export default Disputes;
