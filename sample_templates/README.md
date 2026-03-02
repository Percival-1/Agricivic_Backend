# Knowledge Base Document Templates

This directory contains sample templates for ingesting documents into the Knowledge Base.

## Available Templates

### 1. Agricultural Knowledge Template
**File:** `agricultural_knowledge_template.csv`

Use this template for:
- Crop cultivation practices
- Farming techniques
- Agricultural best practices
- Seasonal guidelines

**Key Fields:**
- `content` (required)
- `crop`, `category`, `season`, `region`
- `language`, `document_type`

---

### 2. Disease Information Template
**File:** `disease_information_template.csv`

Use this template for:
- Crop disease identification
- Disease symptoms
- Treatment recommendations
- Pest management

**Key Fields:**
- `content` (required)
- `crop`, `disease_name`, `severity`
- `treatment_type`, `category`

---

### 3. Government Schemes Template
**File:** `government_schemes_template.csv`

Use this template for:
- Government scheme details
- Eligibility criteria
- Benefits and subsidies
- Application procedures

**Key Fields:**
- `content` (required)
- `scheme_name`, `scheme_type`
- `eligibility`, `benefit_amount`

---

### 4. Market Intelligence Template
**File:** `market_intelligence_template.csv`

Use this template for:
- Market prices
- Mandi information
- Price trends
- Supply and demand data

**Key Fields:**
- `content` (required)
- `crop`, `region`, `mandi_name`
- `price_range`, `date`

---

### 5. Sample JSON Document
**File:** `sample_documents.json`

Complete JSON example with all document types. Use this as a reference for JSON format ingestion.

---

## How to Use Templates

### Step 1: Choose Template
Select the template that matches your document type.

### Step 2: Fill in Data
1. Open the CSV file in Excel, Google Sheets, or any text editor
2. Keep the header row unchanged
3. Replace the sample data with your actual content
4. Add as many rows as needed

### Step 3: Save File
- Save as CSV (UTF-8 encoding)
- Or convert to JSON format if preferred

### Step 4: Upload
1. Go to Admin Dashboard → Knowledge Base
2. Click "Ingest Documents" tab
3. Select your collection (optional)
4. Choose your file
5. Click "Ingest Documents"

---

## Important Notes

### Required Fields
- **CSV:** Must have `content`, `text`, or `document` column
- **JSON:** Must have `content` field in each document

### File Limits
- Maximum file size: 50 MB
- Recommended: 100-500 words per document
- Batch size: Up to 1000 documents per file

### Encoding
Always use **UTF-8 encoding** to support multiple languages.

### Content Guidelines
- Keep content focused on one topic
- Use clear, concise language
- Include relevant context
- Avoid very long paragraphs

---

## Quick Start Example

### CSV Example
```csv
content,source,crop,category,language,document_type
"Your content here",your_source,wheat,cultivation,en,agricultural_knowledge
```

### JSON Example
```json
{
  "content": "Your content here",
  "metadata": {
    "source": "your_source",
    "crop": "wheat",
    "category": "cultivation",
    "language": "en",
    "document_type": "agricultural_knowledge"
  }
}
```

---

## Need Help?

Refer to the complete **KNOWLEDGE_BASE_INGESTION_GUIDE.md** in the root directory for:
- Detailed field descriptions
- Advanced examples
- Troubleshooting guide
- Best practices

---

## Template Versions

- **v1.0** - Initial templates (2024-01-15)
  - Agricultural Knowledge
  - Disease Information
  - Government Schemes
  - Market Intelligence
  - Sample JSON

---

**Last Updated:** January 15, 2024
