# 🚗 Mileage Tracker

A comprehensive web application for tracking business mileage, managing frequent locations, and organizing receipts for tax deduction purposes. Built with Streamlit and Supabase.

**🌐 Live App:** [https://taxexpensetracker.streamlit.app/](https://taxexpensetracker.streamlit.app/)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://taxexpensetracker.streamlit.app)

## 📋 Overview

Mileage Tracker helps you maintain accurate records of your business travel for tax deductions. The app automatically calculates distances between locations, stores your trip history, and provides receipt management with OCR capabilities.

### Key Features

- 📍 **Location Management** - Save frequently visited locations with Google Maps integration
- 🛣️ **Mileage Logging** - Track trips with automatic distance calculation
- 🧾 **Receipt Tracker** - Upload and OCR-process receipts for expense tracking
- 🔐 **Secure Authentication** - User accounts with Supabase authentication
- 📊 **Trip Statistics** - View total miles, estimated deductions, and trip history
- 📥 **Data Export** - Download your mileage log as CSV for tax filing
- 🔄 **Smart Caching** - Reuses distances for repeat routes to save API calls

## 🎯 Purpose

This application was designed for:
- **Self-employed professionals** tracking business miles for tax deductions
- **Contractors** who need to log travel between job sites
- **Sales representatives** with frequent client visits
- **Anyone** who needs accurate mileage records for reimbursement or taxes

The IRS requires detailed mileage logs including dates, destinations, and business purposes. This app simplifies that process.

## ✨ Functionality

### 1. Dashboard (Home)
- Quick overview of saved locations, total trips, and receipts
- Summary statistics at a glance
- Easy navigation to all features

### 2. Mileage Dictionary 📍
**Manage Your Frequent Locations**
- Add new locations using Google Maps address search
- Store location names and addresses
- Edit existing locations
- Delete locations you no longer need
- View all saved locations in a clean table format

**Features:**
- Google Maps address validation
- Prevents duplicate location names
- CRUD operations (Create, Read, Update, Delete)

### 3. Mileage Log 🛣️
**Track Your Business Trips**
- Log trips between saved locations
- Automatic distance calculation using Google Distance Matrix API
- Date tracking for each trip
- Swap button to easily reverse route direction
- Filter trips by date range
- Search through trip history
- View estimated tax deductions (based on IRS mileage rate)

**Features:**
- Smart distance caching (reuses distances for repeat routes in both directions)
- Date filters: Last 7/30 days, This Month, Custom Range
- Trip statistics: Total trips, total miles, estimated deduction
- Edit trip details (date, locations, distance)
- Delete trips with confirmation
- Export to CSV for tax filing
- No annoying warnings when logging the same route on different days

### 4. Receipt Tracker 🧾
**Organize Business Expenses**
- Upload receipt images (PNG, JPG, JPEG, PDF)
- Automatic OCR text extraction using Tesseract
- Parse store name, date, and total amount
- Manual entry option for failed OCR
- Filter and sort receipts
- View receipt history with timestamps

**Features:**
- Auto-rotation for sideways images
- Smart date parsing (handles multiple formats)
- Image enhancement for better OCR accuracy
- Upload timestamp tracking
- Filter by store name or amount

## 🛠️ Technology Stack

### Frontend
- **Streamlit** - Web application framework
- **Pandas** - Data manipulation and display

### Backend
- **Supabase** - PostgreSQL database with authentication
- **Google Maps API** - Address lookup and distance calculation
  - Places API for address search
  - Distance Matrix API for mileage calculation

### OCR & Image Processing
- **Tesseract OCR** - Receipt text extraction
- **Pillow (PIL)** - Image processing and enhancement

### Architecture
- Multi-page Streamlit application
- Modular code structure with separated utilities and components
- Session state management for user experience
- Row Level Security (RLS) for data isolation

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Supabase account
- Google Cloud account with Maps API enabled

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/steiner-kenton/mileage_tracker.git
   cd mileage_tracker
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR:**
   - **macOS:** `brew install tesseract`
   - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
   - **Windows:** Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

5. **Configure secrets:**
   Create `.streamlit/secrets.toml`:
   ```toml
   [google]
   api_key = "YOUR_GOOGLE_MAPS_API_KEY"

   [supabase]
   SUPABASE_URL = "YOUR_SUPABASE_URL"
   SUPABASE_API = "YOUR_SUPABASE_ANON_KEY"
   SUPABASE_SERVICE_ROLE_KEY = "YOUR_SERVICE_ROLE_KEY"
   ```

6. **Set up Supabase database:**
   Run the SQL schema in your Supabase project (see `MIGRATION_GUIDE.md`)

7. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## 📊 Database Schema

### Tables

**mileage_dictionary**
- `id` (Primary Key)
- `user_id` (Foreign Key to auth.users)
- `location_name` (Text)
- `location_address` (Text)
- `created_at` (Timestamp)

**mileage_log**
- `id` (Primary Key)
- `user_id` (Foreign Key to auth.users)
- `date` (Date)
- `start_location` (Text)
- `start_address` (Text)
- `end_location` (Text)
- `end_address` (Text)
- `distance` (Numeric)
- `created_at` (Timestamp)

**receipts**
- `id` (Primary Key)
- `user_id` (Foreign Key to auth.users)
- `date` (Date)
- `store_name` (Text)
- `total` (Numeric)
- `upload_timestamp` (Timestamp)
- `ocr_raw_text` (Text, optional)
- `created_at` (Timestamp)

All tables include Row Level Security (RLS) policies to ensure users can only access their own data.

## 🔐 Security

- **Authentication:** Supabase Auth with email/password
- **Authorization:** Row Level Security (RLS) policies
- **Data Isolation:** Each user can only access their own records
- **Secrets Management:** API keys stored securely in Streamlit secrets
- **HTTPS:** Encrypted connections in production

## 📈 API Usage & Costs

### Google Maps API
- **Places API:** ~$17 per 1,000 requests (address search)
- **Distance Matrix API:** ~$5 per 1,000 requests (distance calculation)
- **Optimization:** App caches distances for repeat routes to minimize costs
- **Free Tier:** $200 monthly credit from Google Cloud

### Supabase
- **Free Tier:** 500MB database, 50,000 monthly active users
- **API Calls:** Unlimited in free tier
- **Authentication:** Included

## 🚢 Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions to Streamlit Community Cloud.

**Quick Deploy:**
1. Push to GitHub
2. Connect to Streamlit Community Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Deploy!

## 📁 Project Structure

```
mileage_tracker/
├── app.py                          # Main application (Dashboard)
├── pages/
│   ├── 1_📍_Mileage_Dictionary.py  # Location management
│   ├── 2_🛣️_Mileage_Log.py         # Trip logging
│   └── 3_🧾_Receipt_Tracker.py     # Receipt management
├── src/
│   ├── components/
│   │   └── ui_components.py        # Reusable UI components
│   └── utils/
│       ├── auth.py                 # Authentication utilities
│       ├── supabase_utils.py       # Database operations
│       ├── google_api.py           # Google Maps integration
│       └── ocr_utils.py            # Receipt OCR processing
├── config/
│   └── config.py                   # Configuration settings
├── .streamlit/
│   ├── config.toml                 # Streamlit configuration
│   └── secrets.toml                # API keys (not in Git)
├── requirements.txt                # Python dependencies
├── packages.txt                    # System dependencies
└── README.md                       # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Maps API for location and distance services
- Supabase for backend infrastructure
- Tesseract OCR for receipt processing
- Streamlit for the web framework

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check the [Deployment Guide](DEPLOYMENT.md)
- Review the [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)

## 🎯 Future Enhancements

- [ ] Mobile app version
- [ ] Automatic trip detection via GPS
- [ ] Calendar integration
- [ ] Multi-vehicle tracking
- [ ] Custom mileage rates
- [ ] Bulk receipt upload
- [ ] Tax report generation
- [ ] Integration with accounting software
- [ ] Expense categorization
- [ ] Mileage maps visualization

---

**Built with ❤️ for better mileage tracking**

*Note: Always consult with a tax professional regarding deduction eligibility and record-keeping requirements for your specific situation.*