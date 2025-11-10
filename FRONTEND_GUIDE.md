# Debbie TA Frontend User Guide

## Overview
The Debbie TA frontend is a modern, user-friendly React application built with Material-UI that provides a complete interface for managing travel clients, viewing deals, handling disputes, and configuring settings.

## Features

### 1. Dashboard
- Overview of key metrics (active clients, deals, disputes)
- Quick view of recent travel deals
- Real-time statistics

### 2. Client Management
- **Add New Clients**: Click "Add Client" button to create new client profiles
- **Edit Clients**: Click the edit icon to modify client information
- **Delete Clients**: Remove clients with confirmation dialog
- **Client Information**:
  - Name, email, and phone contact details
  - Preferred airlines, hotels, and destinations
  - Loyalty program information
  - Active/Inactive status tracking

### 3. Travel Deals
- Browse all available travel deals
- Filter by:
  - Region (Europe, Asia, South America, Africa)
  - Deal type (flights, hotels, cruises, packages)
  - Maximum price
- View deal details including:
  - Origin and destination
  - Price in cash or points
  - Airline and travel class
  - Direct links to booking

### 4. Disputes
- Track and manage travel disputes
- Coming soon: Full dispute management system

### 5. Settings
- Configure alert thresholds for different regions
- Set up notification preferences (email and SMS)
- Manage preferred airlines and hotels
- Set default airport

## Technology Stack
- **React 18**: Modern React with hooks
- **Material-UI (MUI) 5**: Professional UI components
- **React Router**: Client-side routing
- **Axios**: API communication
- **Custom Theme**: Consistent branding and styling

## Deployed Services
- **Backend API**: https://debbie-ta-web-27459188081.us-central1.run.app
- **API Documentation**: https://debbie-ta-web-27459188081.us-central1.run.app/docs

## Local Development

### Prerequisites
- Node.js 18 or higher
- npm or yarn

### Getting Started
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will open at http://localhost:3000

### Environment Configuration
- **Development**: Uses proxy to localhost:8000 (configured in package.json)
- **Production**: Uses environment variable REACT_APP_API_URL

## Deployment to Netlify

### Option 1: Netlify CLI (Recommended)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy (from project root)
netlify deploy --prod
```

### Option 2: GitHub Integration
1. Push your code to GitHub
2. Go to https://app.netlify.com
3. Click "Add new site" → "Import an existing project"
4. Connect your GitHub repository
5. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`
6. Click "Deploy site"

### Option 3: Drag and Drop
```bash
# Build the app
cd frontend
npm run build

# Drag the `build` folder to Netlify's deploy interface
# Visit https://app.netlify.com/drop
```

## Configuration Files

### netlify.toml
Already configured with:
- Build settings
- API redirects to your backend
- SPA fallback routing
- Security headers

### .env.production
Contains the production API URL:
```
REACT_APP_API_URL=https://debbie-ta-web-27459188081.us-central1.run.app
```

## User Guide for Non-Technical Users

### Getting Started
1. **Access the Application**: Open your web browser and navigate to your Netlify URL
2. **Navigate**: Use the top navigation bar to switch between sections:
   - Dashboard: See overview and recent deals
   - Clients: Manage your client database
   - Deals: Browse and filter travel deals
   - Disputes: Track disputes (coming soon)
   - Settings: Configure your preferences

### Managing Clients
1. Click "Clients" in the top navigation
2. Click the "Add Client" button
3. Fill in the client information:
   - Name and email (required)
   - Phone number (optional)
   - Preferred airlines (e.g., "Delta, United, Air France")
   - Preferred hotels (e.g., "Marriott, Hyatt")
   - Preferred destinations (e.g., "Europe, Asia")
4. Click "Add Client" to save
5. To edit: Click the pencil icon next to any client
6. To delete: Click the trash icon (confirmation required)

### Browsing Deals
1. Click "Deals" in the top navigation
2. Use the filter dropdowns to narrow results:
   - **Region**: Choose a specific region or see all
   - **Deal Type**: Filter by flights, hotels, cruises, or packages
   - **Max Price**: Set a maximum price threshold
3. Click "Refresh" to reload deals
4. Click "View Deal" to open the booking link in a new tab

### Configuring Settings
1. Click "Settings" in the top navigation
2. **Alert Thresholds**: Set maximum miles/cash for different regions
3. **Notifications**: Add email and phone for alerts
4. **Preferences**: Set your preferred airlines, hotels, and default airport
5. Click "Save" buttons to apply changes

## Tips for Best Experience
- The system automatically checks for new deals every 12 hours
- Client preferences help filter relevant deals
- Set alert thresholds to match your clients' budgets
- Use the dashboard for a quick overview of system activity
- All API calls are automatically routed to your backend

## Troubleshooting

### Deals Not Showing
- The backend checks for deals every 12 hours
- Check the backend is running at https://debbie-ta-web-27459188081.us-central1.run.app/health
- Verify API redirects in netlify.toml

### Client Data Not Saving
- Check browser console for errors (F12)
- Verify backend API is accessible
- Check that email format is valid

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install

# Clear build cache
rm -rf build
npm run build
```

## Support
For issues or questions:
- Check API documentation at /docs endpoint
- Review browser console for errors
- Verify backend health endpoint

## Future Enhancements
- Dispute management system
- Email integration for automated alerts
- SMS notifications via Twilio
- Advanced analytics dashboard
- Client booking history
- Itinerary management
