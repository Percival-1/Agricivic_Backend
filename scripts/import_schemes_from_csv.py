"""
Script to import government schemes from CSV file into the vector database.

CSV Format:
- scheme_id: Unique identifier (e.g., bihar_kisan_001)
- scheme_name: Official name of the scheme
- scheme_type: State or Central
- state: State name (e.g., Bihar, Punjab) or "All India" for central schemes
- category: Category (e.g., Income Support, Insurance, Loan, Subsidy)
- description: Brief description of the scheme
- benefits: Pipe-separated list of benefits (e.g., "Benefit 1|Benefit 2|Benefit 3")
- eligibility: Pipe-separated list of eligibility criteria
- application_process: Pipe-separated list of application steps
- required_documents: Pipe-separated list of required documents
- benefit_amount: Numeric amount if applicable (optional)
- language: Language code (e.g., en, hi, te)

Usage:
    python scripts/import_schemes_from_csv.py <csv_file_path>

Example:
    python scripts/import_schemes_from_csv.py schemes_data.csv
"""

import asyncio
import sys
import csv
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_db_factory import get_vector_db


def format_scheme_content(row):
    """Format scheme data into structured content."""

    # Parse pipe-separated lists
    benefits = row["benefits"].split("|") if row["benefits"] else []
    eligibility = row["eligibility"].split("|") if row["eligibility"] else []
    application_steps = (
        row["application_process"].split("|") if row["application_process"] else []
    )
    documents = (
        row["required_documents"].split("|") if row["required_documents"] else []
    )

    # Build structured content
    content = f"""{row['scheme_name']}
        
Description: {row['description']}

Benefits:
"""

    for benefit in benefits:
        content += f"- {benefit.strip()}\n"

    content += "\nEligibility:\n"
    for criteria in eligibility:
        content += f"- {criteria.strip()}\n"

    content += "\nApplication Process:\n"
    for i, step in enumerate(application_steps, 1):
        content += f"{i}. {step.strip()}\n"

    content += f"\nType: {row['scheme_type']} Government Scheme"
    if row["scheme_type"] == "State":
        content += f" ({row['state']})"
    content += f"\nCategory: {row['category']}"
    content += f"\nState: {row['state']}"

    return content.strip()


def create_metadata(row):
    """Create metadata dictionary from CSV row."""
    metadata = {
        "scheme_name": row["scheme_name"],
        "scheme_type": row["scheme_type"],
        "category": row["category"],
        "state": row["state"],
        "language": row["language"],
    }

    if row.get("benefit_amount"):
        metadata["benefit_amount"] = row["benefit_amount"]

    return metadata


async def import_schemes_from_csv(csv_file_path):
    """Import schemes from CSV file into vector database."""

    print("=" * 80)
    print("GOVERNMENT SCHEMES CSV IMPORT")
    print("=" * 80)
    print()

    # Check if file exists
    if not Path(csv_file_path).exists():
        print(f"✗ Error: File not found: {csv_file_path}")
        return False

    try:
        # Read CSV file
        schemes = []
        with open(csv_file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Validate required columns
            required_columns = [
                "scheme_id",
                "scheme_name",
                "scheme_type",
                "state",
                "category",
                "description",
                "benefits",
                "eligibility",
                "application_process",
                "required_documents",
                "language",
            ]

            if not all(col in reader.fieldnames for col in required_columns):
                missing = [
                    col for col in required_columns if col not in reader.fieldnames
                ]
                print(f"✗ Error: Missing required columns: {', '.join(missing)}")
                print(f"  Required columns: {', '.join(required_columns)}")
                return False

            # Read all rows
            for row in reader:
                if not row["scheme_id"].strip():
                    continue  # Skip empty rows

                scheme = {
                    "id": row["scheme_id"].strip(),
                    "content": format_scheme_content(row),
                    "metadata": create_metadata(row),
                }
                schemes.append(scheme)

        if not schemes:
            print("✗ Error: No valid schemes found in CSV file")
            return False

        print(f"Found {len(schemes)} schemes in CSV file")
        print()

        # Get vector database instance
        vector_db = get_vector_db()

        # Ensure collection exists
        try:
            vector_db.create_collection("government_schemes")
            print("✓ Created government_schemes collection")
        except Exception as e:
            print(f"Collection already exists: {e}")

        # Add schemes to vector database
        documents = [scheme["content"] for scheme in schemes]
        metadatas = [scheme["metadata"] for scheme in schemes]
        ids = [scheme["id"] for scheme in schemes]

        vector_db.add_documents("government_schemes", documents, metadatas, ids)

        print(f"\n✓ Successfully imported {len(schemes)} schemes to vector database")
        print()

        # Show summary
        print("=" * 80)
        print("IMPORT SUMMARY")
        print("=" * 80)

        # Group by state
        by_state = {}
        for scheme in schemes:
            state = scheme["metadata"]["state"]
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(scheme["metadata"]["scheme_name"])

        for state, scheme_names in sorted(by_state.items()):
            print(f"\n{state}:")
            for name in scheme_names:
                print(f"  - {name}")

        print()
        print("=" * 80)
        print("IMPORT COMPLETED SUCCESSFULLY!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_schemes_from_csv.py <csv_file_path>")
        print("\nExample:")
        print("  python scripts/import_schemes_from_csv.py schemes_data.csv")
        print("\nSee schemes_template.csv for the required CSV format")
        sys.exit(1)

    csv_file = sys.argv[1]
    success = asyncio.run(import_schemes_from_csv(csv_file))
    sys.exit(0 if success else 1)
