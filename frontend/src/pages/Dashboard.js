import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  FlightTakeoff,
  People,
  LocalOffer,
  Report,
} from '@mui/icons-material';
import axios from 'axios';

function Dashboard() {
  const [stats, setStats] = useState({
    activeClients: 0,
    activeDeals: 0,
    activeDisputes: 0,
    dealsToday: 0,
  });
  const [recentDeals, setRecentDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch recent deals
      const dealsResponse = await axios.get('/api/deals/?limit=5');
      setRecentDeals(dealsResponse.data);

      // In production, you'd fetch actual stats
      setStats({
        activeClients: 12,
        activeDeals: dealsResponse.data.length,
        activeDisputes: 3,
        dealsToday: dealsResponse.data.filter(d => {
          const today = new Date().toDateString();
          return new Date(d.created_at).toDateString() === today;
        }).length,
      });

      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h3">
              {value}
            </Typography>
          </Box>
          <Icon style={{ fontSize: 60, color }} />
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">Error loading dashboard: {error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Clients"
            value={stats.activeClients}
            icon={People}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Deals"
            value={stats.activeDeals}
            icon={LocalOffer}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Deals Today"
            value={stats.dealsToday}
            icon={FlightTakeoff}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Disputes"
            value={stats.activeDisputes}
            icon={Report}
            color="#d32f2f"
          />
        </Grid>
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Recent Deals
        </Typography>
        {recentDeals.length === 0 ? (
          <Typography color="textSecondary">
            No deals found. The system will check for new deals every 12 hours.
          </Typography>
        ) : (
          recentDeals.map((deal) => (
            <Box
              key={deal.id}
              sx={{
                p: 2,
                mb: 2,
                border: '1px solid #e0e0e0',
                borderRadius: 1,
                '&:hover': {
                  backgroundColor: '#f5f5f5',
                },
              }}
            >
              <Typography variant="h6">{deal.title}</Typography>
              <Typography color="textSecondary">
                {deal.origin_airport} → {deal.destination_region}
              </Typography>
              {deal.deal_price && (
                <Typography variant="body1" color="primary">
                  ${deal.deal_price}
                </Typography>
              )}
              {deal.points_required && (
                <Typography variant="body1" color="secondary">
                  {deal.points_required.toLocaleString()} points
                </Typography>
              )}
            </Box>
          ))
        )}
      </Paper>
    </Container>
  );
}

export default Dashboard;
