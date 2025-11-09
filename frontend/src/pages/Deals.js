import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  MenuItem,
  Box,
  CircularProgress,
} from '@mui/material';
import { OpenInNew } from '@mui/icons-material';
import axios from 'axios';

function Deals() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    region: '',
    maxPrice: '',
    dealType: '',
  });

  useEffect(() => {
    fetchDeals();
  }, [filters]);

  const fetchDeals = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.region) params.append('region', filters.region);
      if (filters.maxPrice) params.append('max_price', filters.maxPrice);
      if (filters.dealType) params.append('deal_type', filters.dealType);

      const response = await axios.get(`/api/deals/?${params.toString()}`);
      setDeals(response.data);
    } catch (error) {
      console.error('Error fetching deals:', error);
    }
    setLoading(false);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Travel Deals
      </Typography>

      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <TextField
          select
          label="Region"
          value={filters.region}
          onChange={(e) => handleFilterChange('region', e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="">All Regions</MenuItem>
          <MenuItem value="Europe">Europe</MenuItem>
          <MenuItem value="Asia">Asia</MenuItem>
          <MenuItem value="South America">South America</MenuItem>
          <MenuItem value="Africa">Africa</MenuItem>
        </TextField>

        <TextField
          select
          label="Deal Type"
          value={filters.dealType}
          onChange={(e) => handleFilterChange('dealType', e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="">All Types</MenuItem>
          <MenuItem value="flight">Flights</MenuItem>
          <MenuItem value="hotel">Hotels</MenuItem>
          <MenuItem value="cruise">Cruises</MenuItem>
          <MenuItem value="package">Packages</MenuItem>
        </TextField>

        <TextField
          label="Max Price"
          type="number"
          value={filters.maxPrice}
          onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
          sx={{ minWidth: 150 }}
        />

        <Button variant="outlined" onClick={fetchDeals}>
          Refresh
        </Button>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {deals.length === 0 ? (
            <Grid item xs={12}>
              <Typography color="textSecondary" align="center">
                No deals found. Check back soon - the system scans for new deals every 12 hours.
              </Typography>
            </Grid>
          ) : (
            deals.map((deal) => (
              <Grid item xs={12} md={6} key={deal.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                      <Typography variant="h6" component="div">
                        {deal.title}
                      </Typography>
                      <Chip
                        label={deal.deal_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>

                    <Typography color="textSecondary" gutterBottom>
                      {deal.origin_airport} → {deal.destination_airport || deal.destination_region}
                    </Typography>

                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {deal.description?.substring(0, 150)}...
                    </Typography>

                    <Box display="flex" gap={2} flexWrap="wrap">
                      {deal.deal_price && (
                        <Chip
                          label={`$${deal.deal_price}`}
                          color="success"
                          variant="filled"
                        />
                      )}
                      {deal.points_required && (
                        <Chip
                          label={`${deal.points_required.toLocaleString()} pts`}
                          color="secondary"
                          variant="filled"
                        />
                      )}
                      {deal.airline && (
                        <Chip
                          label={deal.airline}
                          variant="outlined"
                        />
                      )}
                      {deal.travel_class && (
                        <Chip
                          label={deal.travel_class}
                          variant="outlined"
                        />
                      )}
                    </Box>
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      endIcon={<OpenInNew />}
                      href={deal.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Deal
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}
    </Container>
  );
}

export default Deals;
