# Database Population Scripts

This directory contains scripts to populate the database with sample data for testing and development.

## Market Data Population

### Script: `populate_market_data.py`

Populates the database with realistic market intelligence data including:
- 8 different crops (Wheat, Rice, Cotton, Sugarcane, Maize, Soybean, Potato, Onion)
- 8 mandis across Delhi, Haryana, and Punjab
- 90 days of historical price data
- Realistic price trends (rising, falling, stable, volatile)
- Price change percentages
- Location coordinates for each mandi

### Usage

```bash
# From the project root directory
python scripts/populate_market_data.py
```

### Data Schema

The script creates `MarketPrice` records with the following fields:

- `mandi_name`: Name of the mandi/market
- `crop_name`: Name of the crop
- `price_per_quintal`: Price per quintal in INR
- `date`: Date of the price record
- `location_lat`: Latitude of the mandi
- `location_lng`: Longitude of the mandi
- `location_address`: Full address of the mandi
- `district`: District name
- `state`: State name
- `quality_grade`: Quality grade (A, B, C, or None)
- `source`: Data source identifier
- `previous_price`: Price from 7 days ago
- `price_change_percentage`: Percentage change from previous price

### Sample Mandis

1. **Delhi**
   - Azadpur Mandi (North Delhi)
   - Narela Mandi (North West Delhi)
   - Ghazipur Mandi (East Delhi)

2. **Haryana**
   - Anaj Mandi Karnal
   - Kisan Mandi Rohtak

3. **Punjab**
   - Mandi Gobindgarh
   - Ludhiana Grain Market
   - Amritsar Mandi

### Price Trends

- **Wheat**: Rising trend (+0.2% per day)
- **Rice**: Stable with minimal variation
- **Cotton**: Falling trend (-0.2% per day)
- **Sugarcane**: Stable
- **Maize**: Rising trend
- **Soybean**: Volatile (±5% random)
- **Potato**: Volatile
- **Onion**: Volatile

### Notes

- The script will clear existing market data before populating
- Prices include realistic daily variations (±3%)
- Regional variations (±10%) are applied to simulate different market conditions
- Data is committed in batches to optimize performance
- Sample output is displayed after population for verification

## Requirements

Ensure you have the following environment variables set in your `.env` file:
- `DATABASE_URL`: PostgreSQL connection string

## Troubleshooting

If you encounter errors:

1. **Database connection issues**: Verify your `DATABASE_URL` is correct
2. **Permission errors**: Ensure the database user has CREATE/INSERT permissions
3. **Import errors**: Run from the project root directory

## Future Scripts

Additional population scripts can be added here for:
- User data
- Session data
- Notification data
- Scheme data
