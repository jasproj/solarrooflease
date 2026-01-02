# Chicken Price Ticker Automation

Automatically fetches weekly wholesale chicken prices from USDA MARS API and updates your site's market ticker.

## Setup Instructions

### 1. Add files to your GitHub repo

Copy these files to your repo root:
```
your-repo/
├── fetch_prices.py
├── prices.json
└── .github/
    └── workflows/
        └── update-prices.yml
```

### 2. Add your API key as a GitHub Secret

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `USDA_API_KEY`
4. Value: `oK/SXE39wQgZKk7FoIP/9kNV+1ZZZ7SB`
5. Click **Add secret**

### 3. Update your site's ticker JavaScript

Replace the hardcoded ticker items in your HTML with this dynamic loader:

```javascript
// Load prices from JSON file
async function loadPrices() {
    try {
        const response = await fetch('prices.json');
        const data = await response.json();
        
        const tickerContent = document.getElementById('ticker-content');
        
        // Build ticker HTML from prices
        let html = '';
        data.items.forEach(item => {
            const changeClass = item.change?.startsWith('+') ? 'positive' : 
                               item.change?.startsWith('-') ? 'negative' : '';
            html += `
                <span class="ticker-item">
                    <span class="ticker-label">${item.name}:</span>
                    <span class="ticker-value">${item.price}</span>
                    ${item.change ? `<span class="ticker-change ${changeClass}">${item.change}</span>` : ''}
                </span>
            `;
        });
        
        // Duplicate for seamless scroll
        tickerContent.innerHTML = html + html;
        
        // Update timestamp
        const updated = new Date(data.updated).toLocaleDateString();
        console.log(`Prices updated: ${updated}`);
        
    } catch (error) {
        console.error('Failed to load prices:', error);
    }
}

// Load on page ready
document.addEventListener('DOMContentLoaded', loadPrices);
```

### 4. Test manually

Run the workflow manually to verify it works:
1. Go to repo → **Actions** → **Update Chicken Prices**
2. Click **Run workflow**
3. Check that `prices.json` gets updated

### Schedule

The workflow runs automatically every **Friday at 5:00 PM ET** (after USDA publishes weekly report).

## Data Source

- **API**: USDA MARS (Market News API)
- **Report**: Weekly National Chicken Report
- **Endpoint**: `https://marsapi.ams.usda.gov/services/v1.2/reports/2469`

## Troubleshooting

**Prices not updating?**
- Check Actions tab for workflow errors
- Verify API key is set correctly in Secrets
- USDA API may be down - check https://mymarketnews.ams.usda.gov

**Wrong prices showing?**
- Report ID may have changed - search USDA for current chicken report slug
- Run `python fetch_prices.py` locally to debug
