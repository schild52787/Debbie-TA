import React from 'react';
import {
  Container,
  Typography,
  Paper,
  Box,
  TextField,
  Button,
  Grid,
} from '@mui/material';

function Settings() {
  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Alert Thresholds
        </Typography>
        <Typography variant="body2" color="textSecondary" paragraph>
          Configure price and miles thresholds for automatic deal alerts
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Asia Deals
            </Typography>
            <TextField
              fullWidth
              label="Max Miles"
              type="number"
              defaultValue="60000"
              margin="normal"
            />
            <TextField
              fullWidth
              label="Max Cash Price ($)"
              type="number"
              defaultValue="1000"
              margin="normal"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" gutterBottom>
              Europe Deals
            </Typography>
            <TextField
              fullWidth
              label="Max Miles"
              type="number"
              defaultValue="30000"
              margin="normal"
            />
            <TextField
              fullWidth
              label="Max Cash Price ($)"
              type="number"
              defaultValue="700"
              margin="normal"
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 3 }}>
          <Button variant="contained">Save Thresholds</Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Notification Settings
        </Typography>

        <TextField
          fullWidth
          label="Alert Email"
          type="email"
          margin="normal"
          helperText="Email address for deal and dispute alerts"
        />

        <TextField
          fullWidth
          label="Alert Phone (SMS)"
          type="tel"
          margin="normal"
          helperText="Phone number for SMS alerts (format: +15551234567)"
        />

        <Box sx={{ mt: 3 }}>
          <Button variant="contained">Save Notifications</Button>
        </Box>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Preferences
        </Typography>

        <TextField
          fullWidth
          label="Preferred Airlines"
          margin="normal"
          helperText="Comma-separated list (e.g., Delta, United, Air France)"
        />

        <TextField
          fullWidth
          label="Preferred Hotel Chains"
          margin="normal"
          helperText="Comma-separated list (e.g., Marriott, Hyatt, Hilton)"
        />

        <TextField
          fullWidth
          label="Default Airport"
          defaultValue="MSP"
          margin="normal"
        />

        <Box sx={{ mt: 3 }}>
          <Button variant="contained">Save Preferences</Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default Settings;
