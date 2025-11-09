import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  LocalOffer as DealsIcon,
  Report as DisputeIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

function Navigation() {
  return (
    <AppBar position="fixed">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Debbie's Travel Agent Assistant
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            color="inherit"
            component={RouterLink}
            to="/"
            startIcon={<DashboardIcon />}
          >
            Dashboard
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/clients"
            startIcon={<PeopleIcon />}
          >
            Clients
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/deals"
            startIcon={<DealsIcon />}
          >
            Deals
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/disputes"
            startIcon={<DisputeIcon />}
          >
            Disputes
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/settings"
            startIcon={<SettingsIcon />}
          >
            Settings
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navigation;
