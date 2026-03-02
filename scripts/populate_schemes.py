"""
Script to populate government schemes (Central and State-specific) into the vector database.

This script adds comprehensive scheme data including:
- Central Government schemes
- State-specific schemes (Telangana, Punjab, Haryana, etc.)
- Eligibility criteria, benefits, and application details

Usage:
    python scripts/populate_schemes.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_db_factory import get_vector_db


# Central Government Schemes
CENTRAL_SCHEMES = [
    {
        "id": "pmkisan_001",
        "content": """PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) Scheme
        
Description: Income support scheme providing ₹6,000 per year to small and marginal farmers.

Benefits:
- ₹6,000 per year in three equal installments of ₹2,000 each
- Direct Benefit Transfer (DBT) to bank accounts
- No application fee

Eligibility:
- Small and marginal farmers with cultivable land up to 2 hectares
- Must have valid Aadhaar card
- Must have active bank account
- Land ownership documents required

Application Process:
1. Visit PM-KISAN portal or nearest CSC
2. Register with Aadhaar and land details
3. Bank account will be verified
4. Amount credited directly to account

Type: Central Government Scheme
Category: Income Support, Direct Benefit Transfer
States: All India (including Telangana, Punjab, Haryana, Delhi)""",
        "metadata": {
            "scheme_name": "PM-KISAN",
            "scheme_type": "Central",
            "category": "Income Support",
            "state": "All India",
            "eligibility": "small_marginal_farmers",
            "benefit_amount": "6000",
            "language": "en",
        },
    },
    {
        "id": "pmfby_001",
        "content": """Pradhan Mantri Fasal Bima Yojana (PMFBY)
        
Description: Comprehensive crop insurance scheme protecting farmers against crop loss.

Benefits:
- Coverage for pre-sowing to post-harvest losses
- Protection against natural calamities, pests, and diseases
- Low premium rates: 2% for Kharif, 1.5% for Rabi crops
- Quick claim settlement

Eligibility:
- All farmers including sharecroppers and tenant farmers
- Applicable for notified crops in notified areas
- Must have insurable interest in the crop

Application Process:
1. Apply through bank, CSC, or insurance company
2. Submit land records and crop details
3. Pay premium amount
4. Receive insurance certificate

Type: Central Government Scheme
Category: Crop Insurance
States: All India (including Telangana, Punjab, Haryana)""",
        "metadata": {
            "scheme_name": "PMFBY",
            "scheme_type": "Central",
            "category": "Insurance",
            "state": "All India",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
    {
        "id": "kcc_001",
        "content": """Kisan Credit Card (KCC) Scheme
        
Description: Credit facility for farmers to meet agricultural expenses.

Benefits:
- Credit limit based on land holding and crop pattern
- Interest rate: 7% per annum
- Additional 3% interest subvention for timely repayment
- Flexible repayment terms
- Insurance coverage included

Eligibility:
- All farmers - individual/joint borrowers
- Tenant farmers, oral lessees, and sharecroppers
- Self Help Groups or Joint Liability Groups

Application Process:
1. Visit nearest bank branch
2. Submit land documents and identity proof
3. Bank will assess credit limit
4. KCC issued within 2 weeks

Type: Central Government Scheme
Category: Agricultural Credit, Loan
States: All India""",
        "metadata": {
            "scheme_name": "Kisan Credit Card",
            "scheme_type": "Central",
            "category": "Loan",
            "state": "All India",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
    {
        "id": "shc_001",
        "content": """Soil Health Card Scheme
        
Description: Provides soil health information to farmers for optimal nutrient management.

Benefits:
- Free soil testing
- Detailed soil health report
- Nutrient recommendations
- Crop-specific fertilizer advice
- Issued every 2 years

Eligibility:
- All farmers
- No land size restriction

Application Process:
1. Contact local agriculture department
2. Soil samples collected from your field
3. Laboratory testing conducted
4. Soil Health Card issued with recommendations

Type: Central Government Scheme
Category: Soil Health, Advisory
States: All India""",
        "metadata": {
            "scheme_name": "Soil Health Card",
            "scheme_type": "Central",
            "category": "Advisory",
            "state": "All India",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
    {
        "id": "enam_001",
        "content": """e-NAM (National Agriculture Market)
        
Description: Online trading platform for agricultural commodities.

Benefits:
- Better price discovery
- Transparent auction process
- Direct payment to farmers
- Reduced transaction costs
- Access to nationwide markets

Eligibility:
- All farmers
- Must register on e-NAM portal
- Bank account required

Application Process:
1. Visit e-NAM portal
2. Register with Aadhaar and bank details
3. Upload produce details
4. Participate in online auctions

Type: Central Government Scheme
Category: Marketing, Digital Platform
States: All India""",
        "metadata": {
            "scheme_name": "e-NAM",
            "scheme_type": "Central",
            "category": "Marketing",
            "state": "All India",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
]


# Telangana State Schemes
TELANGANA_SCHEMES = [
    {
        "id": "rythu_bandhu_001",
        "content": """Rythu Bandhu Scheme (Telangana)
        
Description: Investment support scheme for farmers in Telangana providing financial assistance per acre.

Benefits:
- ₹5,000 per acre per season (₹10,000 per year)
- Two installments: Kharif and Rabi seasons
- Direct cash transfer to farmer's account
- No application required for existing beneficiaries

Eligibility:
- All farmers in Telangana with agricultural land
- Land ownership documents required
- Aadhaar linked bank account mandatory

Application Process:
1. Land records automatically verified
2. Amount credited directly to bank account
3. For new farmers: Update land records at MeeSeva center

Type: State Government Scheme (Telangana)
Category: Investment Support, Direct Benefit Transfer
State: Telangana
Districts: All districts in Telangana""",
        "metadata": {
            "scheme_name": "Rythu Bandhu",
            "scheme_type": "State",
            "category": "Investment Support",
            "state": "Telangana",
            "eligibility": "all_farmers",
            "benefit_amount": "10000",
            "language": "en",
        },
    },
    {
        "id": "rythu_bima_001",
        "content": """Rythu Bima Scheme (Telangana)
        
Description: Life insurance scheme for farmers in Telangana.

Benefits:
- ₹5 lakh insurance coverage
- No premium payment required (government pays)
- Coverage for accidental death
- Quick claim settlement

Eligibility:
- Farmers aged 18-59 years
- Must be enrolled in Rythu Bandhu scheme
- Telangana resident

Application Process:
- Automatic enrollment for Rythu Bandhu beneficiaries
- No separate application needed

Type: State Government Scheme (Telangana)
Category: Life Insurance
State: Telangana""",
        "metadata": {
            "scheme_name": "Rythu Bima",
            "scheme_type": "State",
            "category": "Insurance",
            "state": "Telangana",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
    {
        "id": "nethanna_ku_bima_001",
        "content": """Nethanna Ku Bima Scheme (Telangana)
        
Description: Crop insurance scheme for tenant farmers and agricultural laborers in Telangana.

Benefits:
- ₹5 lakh insurance coverage
- Zero premium for beneficiaries
- Coverage for natural and accidental death

Eligibility:
- Agricultural laborers and tenant farmers
- Age: 18-59 years
- Telangana resident

Type: State Government Scheme (Telangana)
Category: Life Insurance
State: Telangana""",
        "metadata": {
            "scheme_name": "Nethanna Ku Bima",
            "scheme_type": "State",
            "category": "Insurance",
            "state": "Telangana",
            "eligibility": "tenant_farmers_laborers",
            "language": "en",
        },
    },
]


# Punjab State Schemes
PUNJAB_SCHEMES = [
    {
        "id": "punjab_msp_001",
        "content": """Punjab Minimum Support Price (MSP) Procurement
        
Description: Government procurement of crops at MSP in Punjab.

Benefits:
- Guaranteed purchase at MSP
- Direct payment to farmers
- Extensive procurement infrastructure
- Covers wheat, paddy, and other crops

Eligibility:
- All farmers in Punjab
- Must register on Punjab Mandi Board portal

Type: State Government Scheme (Punjab)
Category: Marketing, Price Support
State: Punjab""",
        "metadata": {
            "scheme_name": "Punjab MSP Procurement",
            "scheme_type": "State",
            "category": "Marketing",
            "state": "Punjab",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
    {
        "id": "punjab_subsidy_001",
        "content": """Punjab Agricultural Machinery Subsidy
        
Description: Subsidy on purchase of agricultural machinery and equipment.

Benefits:
- 40-50% subsidy on machinery cost
- Covers tractors, harvesters, seeders, etc.
- Priority to small and marginal farmers

Eligibility:
- Farmers in Punjab
- Must not have availed subsidy in last 5 years

Type: State Government Scheme (Punjab)
Category: Subsidy, Equipment
State: Punjab""",
        "metadata": {
            "scheme_name": "Punjab Agricultural Machinery Subsidy",
            "scheme_type": "State",
            "category": "Subsidy",
            "state": "Punjab",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
]


# Haryana State Schemes
HARYANA_SCHEMES = [
    {
        "id": "haryana_bhavantar_001",
        "content": """Bhavantar Bharpayee Yojana (Haryana)
        
Description: Price deficiency payment scheme for horticulture crops in Haryana.

Benefits:
- Compensation for price difference between MSP and market price
- Covers vegetables and fruits
- Direct payment to farmers

Eligibility:
- Farmers growing notified horticulture crops
- Must register on Meri Fasal Mera Byora portal

Type: State Government Scheme (Haryana)
Category: Price Support
State: Haryana""",
        "metadata": {
            "scheme_name": "Bhavantar Bharpayee Yojana",
            "scheme_type": "State",
            "category": "Price Support",
            "state": "Haryana",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
    {
        "id": "haryana_solar_001",
        "content": """Haryana Solar Power Subsidy for Farmers
        
Description: Subsidy for installation of solar pumps and panels.

Benefits:
- 90% subsidy for small farmers
- 70% subsidy for other farmers
- Reduces electricity costs
- Environment friendly

Eligibility:
- Farmers in Haryana
- Must have agricultural land

Type: State Government Scheme (Haryana)
Category: Subsidy, Energy
State: Haryana""",
        "metadata": {
            "scheme_name": "Haryana Solar Power Subsidy",
            "scheme_type": "State",
            "category": "Subsidy",
            "state": "Haryana",
            "eligibility": "all_farmers",
            "language": "en",
        },
    },
]


async def populate_schemes():
    """Populate government schemes into vector database."""
    print("=" * 80)
    print("GOVERNMENT SCHEMES POPULATION SCRIPT")
    print("=" * 80)
    print()

    try:
        # Get vector database instance
        vector_db = get_vector_db()

        # Combine all schemes
        all_schemes = (
            CENTRAL_SCHEMES + TELANGANA_SCHEMES + PUNJAB_SCHEMES + HARYANA_SCHEMES
        )

        print(f"Total schemes to add: {len(all_schemes)}")
        print(f"  - Central schemes: {len(CENTRAL_SCHEMES)}")
        print(f"  - Telangana schemes: {len(TELANGANA_SCHEMES)}")
        print(f"  - Punjab schemes: {len(PUNJAB_SCHEMES)}")
        print(f"  - Haryana schemes: {len(HARYANA_SCHEMES)}")
        print()

        # Ensure collection exists
        try:
            vector_db.create_collection("government_schemes")
            print("✓ Created government_schemes collection")
        except Exception as e:
            print(f"Collection already exists or error: {e}")

        # Add schemes to vector database
        documents = [scheme["content"] for scheme in all_schemes]
        metadatas = [scheme["metadata"] for scheme in all_schemes]
        ids = [scheme["id"] for scheme in all_schemes]

        vector_db.add_documents("government_schemes", documents, metadatas, ids)

        print(f"\n✓ Successfully added {len(all_schemes)} schemes to vector database")
        print()

        # Test queries
        print("=" * 80)
        print("TESTING SCHEME SEARCH")
        print("=" * 80)
        print()

        test_queries = [
            "farmer schemes",
            "telangana farmers",
            "rythu bandhu",
            "crop insurance",
            "punjab schemes",
        ]

        for query in test_queries:
            print(f"Query: '{query}'")
            results = vector_db.query_documents(
                "government_schemes", query, n_results=3
            )

            if results and results.get("documents") and results["documents"][0]:
                print(f"  Found {len(results['documents'][0])} results")
                for i, doc in enumerate(results["documents"][0][:2], 1):
                    # Extract scheme name from content
                    first_line = doc.split("\n")[0]
                    print(f"    {i}. {first_line[:60]}...")
            else:
                print(f"  No results found")
            print()

        print("=" * 80)
        print("SCHEME POPULATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(populate_schemes())
    sys.exit(0 if success else 1)
