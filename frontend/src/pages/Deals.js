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
  Paper,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  AlertTitle,
} from '@mui/material';
import { OpenInNew, Search, FilterList, ExpandMore } from '@mui/icons-material';
import axios from 'axios';

function Deals() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liveSearchMode, setLiveSearchMode] = useState(false);
  const [dealSource, setDealSource] = useState('database');
  const [filters, setFilters] = useState({
    searchQuery: '',
    origin: '',
    region: '',
    dealType: '',
    maxPrice: '',
    maxPoints: '',
    airline: '',
    travelClass: '',
  });
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  useEffect(() => {
    fetchDeals();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const fetchDeals = async (useLiveSearch = false) => {
    setLoading(true);
    setError(null);
    setLiveSearchMode(useLiveSearch);

    try {
      const params = new URLSearchParams();
      if (filters.origin) params.append('origin', filters.origin);
      if (filters.region) params.append('region', filters.region);
      if (filters.maxPrice) params.append('max_price', filters.maxPrice);
      if (filters.maxPoints) params.append('max_points', filters.maxPoints);
      if (filters.dealType) params.append('deal_type', filters.dealType);

      let response;
      let filteredDeals;

      if (useLiveSearch) {
        // Live web search
        response = await axios.get(`/api/deals/live-search?${params.toString()}`);
        filteredDeals = response.data.deals || [];
        setDealSource('live_web_search');
      } else {
        // Database search
        response = await axios.get(`/api/deals/?${params.toString()}`);
        filteredDeals = response.data;
        setDealSource('database');
      }

      // Client-side filtering for fields not supported by API
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        filteredDeals = filteredDeals.filter(deal =>
          deal.title?.toLowerCase().includes(query) ||
          deal.description?.toLowerCase().includes(query) ||
          deal.destination_city?.toLowerCase().includes(query) ||
          deal.destination_country?.toLowerCase().includes(query)
        );
      }

      if (filters.airline) {
        filteredDeals = filteredDeals.filter(deal =>
          deal.airline?.toLowerCase().includes(filters.airline.toLowerCase())
        );
      }

      if (filters.travelClass) {
        filteredDeals = filteredDeals.filter(deal =>
          deal.travel_class === filters.travelClass
        );
      }

      setDeals(filteredDeals);
    } catch (error) {
      console.error('Error fetching deals:', error);
      setError(error.response?.data?.detail || 'Failed to load deals. Please check your backend connection.');
    }
    setLoading(false);
  };

  const handleLiveSearch = () => {
    fetchDeals(true);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleClearFilters = () => {
    setFilters({
      searchQuery: '',
      origin: '',
      region: '',
      dealType: '',
      maxPrice: '',
      maxPoints: '',
      airline: '',
      travelClass: '',
    });
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h4">
            Travel Deals
          </Typography>
          <Button
            variant="contained"
            color="secondary"
            onClick={handleLiveSearch}
            disabled={loading}
            sx={{ minWidth: 150 }}
          >
            {loading && liveSearchMode ? 'Searching Web...' : '🔍 Live Web Search'}
          </Button>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            {dealSource === 'live_web_search'
              ? '🌐 Showing live results from travel websites (The Points Guy, Thrifty Traveler, Secret Flying, Going, Fly4Free)'
              : 'Showing deals from database. Click "Live Web Search" to fetch the latest deals from travel websites in real-time.'}
          </Typography>
        </Box>
      </Box>

      {/* Search and Quick Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Search deals by destination, title, or description..."
            value={filters.searchQuery}
            onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="Origin Airport"
              value={filters.origin}
              onChange={(e) => handleFilterChange('origin', e.target.value)}
            >
              <MenuItem value="">Any Origin</MenuItem>
              <MenuItem value="MSP">MSP - Minneapolis</MenuItem>
              <MenuItem value="JFK">JFK - New York</MenuItem>
              <MenuItem value="LAX">LAX - Los Angeles</MenuItem>
              <MenuItem value="ORD">ORD - Chicago</MenuItem>
              <MenuItem value="ATL">ATL - Atlanta</MenuItem>
              <MenuItem value="DFW">DFW - Dallas</MenuItem>
              <MenuItem value="SFO">SFO - San Francisco</MenuItem>
              <MenuItem value="MIA">MIA - Miami</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="Destination Region"
              value={filters.region}
              onChange={(e) => handleFilterChange('region', e.target.value)}
            >
              <MenuItem value="">All Regions</MenuItem>
              <MenuItem value="Europe">Europe</MenuItem>
              <MenuItem value="Asia">Asia</MenuItem>
              <MenuItem value="South America">South America</MenuItem>
              <MenuItem value="Africa">Africa</MenuItem>
              <MenuItem value="Caribbean">Caribbean</MenuItem>
              <MenuItem value="North America">North America</MenuItem>
              <MenuItem value="Oceania">Oceania</MenuItem>
              <MenuItem value="Middle East">Middle East</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              select
              label="Deal Type"
              value={filters.dealType}
              onChange={(e) => handleFilterChange('dealType', e.target.value)}
            >
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value="flight">Flights</MenuItem>
              <MenuItem value="hotel">Hotels</MenuItem>
              <MenuItem value="cruise">Cruises</MenuItem>
              <MenuItem value="package">Packages</MenuItem>
              <MenuItem value="award">Award Travel</MenuItem>
            </TextField>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Max Cash Price ($)"
              type="number"
              value={filters.maxPrice}
              onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
              placeholder="e.g., 1000"
            />
          </Grid>
        </Grid>

        {/* Advanced Filters */}
        <Accordion
          expanded={showAdvancedFilters}
          onChange={() => setShowAdvancedFilters(!showAdvancedFilters)}
          sx={{ mt: 2, boxShadow: 'none', '&:before': { display: 'none' } }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FilterList />
              <Typography>Advanced Filters</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  label="Max Points/Miles"
                  type="number"
                  value={filters.maxPoints}
                  onChange={(e) => handleFilterChange('maxPoints', e.target.value)}
                  placeholder="e.g., 60000"
                />
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  label="Airline"
                  value={filters.airline}
                  onChange={(e) => handleFilterChange('airline', e.target.value)}
                  placeholder="e.g., Delta, United"
                />
              </Grid>

              <Grid item xs={12} sm={6} md={4}>
                <TextField
                  fullWidth
                  select
                  label="Travel Class"
                  value={filters.travelClass}
                  onChange={(e) => handleFilterChange('travelClass', e.target.value)}
                >
                  <MenuItem value="">All Classes</MenuItem>
                  <MenuItem value="economy">Economy</MenuItem>
                  <MenuItem value="premium_economy">Premium Economy</MenuItem>
                  <MenuItem value="business">Business Class</MenuItem>
                  <MenuItem value="first">First Class</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            {liveSearchMode && (
              <Chip
                label="🌐 Live Web Results"
                color="success"
                size="small"
                variant="outlined"
              />
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button variant="outlined" onClick={handleClearFilters}>
              Clear All Filters
            </Button>
            <Button variant="contained" onClick={() => fetchDeals(false)}>
              Search Database
            </Button>
            <Button variant="contained" color="secondary" onClick={handleLiveSearch}>
              🔍 Live Search
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>Error Loading Deals</AlertTitle>
          {error}
        </Alert>
      )}

      {/* Results */}
      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" p={8}>
          <CircularProgress size={60} />
        </Box>
      ) : (
        <>
          {/* Results Count */}
          <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              {deals.length === 0 ? 'No deals found' : `Showing ${deals.length} deal${deals.length !== 1 ? 's' : ''}`}
            </Typography>
            {deals.length > 0 && (
              <Chip
                label={`${deals.length} Results`}
                color="primary"
                size="small"
              />
            )}
          </Box>

          <Grid container spacing={3}>
            {deals.length === 0 ? (
              <Grid item xs={12}>
                <Paper sx={{ p: 6, textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom>
                    No Deals Found
                  </Typography>
                  <Typography color="textSecondary" paragraph>
                    {filters.searchQuery || filters.origin || filters.region || filters.dealType || filters.maxPrice || filters.maxPoints || filters.airline || filters.travelClass
                      ? 'Try adjusting your filters to see more results.'
                      : 'No deals are currently available. The system scans for new deals every 12 hours.'}
                  </Typography>
                  {(filters.searchQuery || filters.origin || filters.region || filters.dealType || filters.maxPrice || filters.maxPoints || filters.airline || filters.travelClass) && (
                    <Button variant="outlined" onClick={handleClearFilters} sx={{ mt: 2 }}>
                      Clear All Filters
                    </Button>
                  )}
                </Paper>
              </Grid>
            ) : (
              deals.map((deal) => (
                <Grid item xs={12} md={6} key={deal.id}>
                  <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                        <Typography variant="h6" component="div" sx={{ flexGrow: 1, pr: 1 }}>
                          {deal.title}
                        </Typography>
                        <Chip
                          label={deal.deal_type}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Box>

                      <Typography color="textSecondary" gutterBottom sx={{ fontWeight: 500 }}>
                        {deal.origin_airport || 'Various'} → {deal.destination_airport || deal.destination_city || deal.destination_region}
                      </Typography>

                      {deal.description && (
                        <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                          {deal.description.length > 150
                            ? `${deal.description.substring(0, 150)}...`
                            : deal.description}
                        </Typography>
                      )}

                      <Box display="flex" gap={1} flexWrap="wrap" sx={{ mb: 1 }}>
                        {deal.deal_price && (
                          <Chip
                            label={`$${parseFloat(deal.deal_price).toLocaleString()}`}
                            color="success"
                            size="small"
                          />
                        )}
                        {deal.points_required && (
                          <Chip
                            label={`${parseInt(deal.points_required).toLocaleString()} pts`}
                            color="secondary"
                            size="small"
                          />
                        )}
                        {deal.airline && (
                          <Chip
                            label={deal.airline}
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {deal.travel_class && (
                          <Chip
                            label={deal.travel_class.replace('_', ' ')}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>

                      {(deal.destination_country || deal.source) && (
                        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {deal.destination_country && (
                            <Chip
                              label={deal.destination_country}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          )}
                          {deal.source && (
                            <Chip
                              label={deal.source}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          )}
                        </Box>
                      )}
                    </CardContent>

                    <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                      {deal.quality_score && (
                        <Chip
                          label={`Score: ${parseFloat(deal.quality_score).toFixed(1)}/10`}
                          size="small"
                          color={deal.quality_score >= 8 ? 'success' : 'default'}
                        />
                      )}
                      <Button
                        size="small"
                        variant="contained"
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
        </>
      )}
    </Container>
  );
}

export default Deals;
