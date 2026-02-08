#!/usr/bin/env python
"""
SympGAN Dataset Import Script

This script imports the SympGAN dataset (diseases, symptoms, and associations)
from TSV files into the SQLite database.

Usage:
    python scripts/import_sympgan_data.py

Data files:
    - ./data/sympgan/diseases.tsv
    - ./data/sympgan/symptoms.tsv
    - ./data/sympgan/symptom_disease_associations.tsv
"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from app.models.sqlite_db import SQLiteClientWrapper
from app.models.sqlite_db import SympganDisease, SympganSymptom, SympganDiseaseSymptomAssociation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tqdm import tqdm


# Data file paths
DATA_DIR = Path("./data/sympgan")
DISEASES_FILE = DATA_DIR / "diseases.tsv"
SYMPTOMS_FILE = DATA_DIR / "symptoms.tsv"
ASSOCIATIONS_FILE = DATA_DIR / "symptom_disease_associations.tsv"

# Batch size for bulk inserts
BATCH_SIZE = 1000


def read_tsv(file_path: Path) -> list[dict]:
    """Read TSV file and return list of dictionaries

    Args:
        file_path: Path to TSV file

    Returns:
        List of dictionaries with column names as keys
    """
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        # Read header
        header = f.readline().strip().split("\t")

        # Read data rows
        for line in f:
            values = line.strip().split("\t")
            if len(values) == len(header):
                row = dict(zip(header, values))
                data.append(row)

    return data


async def import_diseases(session: AsyncSession) -> dict[str, int]:
    """Import diseases from TSV file

    Args:
        session: Database session

    Returns:
        Dictionary with CUI to ID mapping
    """
    print(f"\n[1/3] Importing diseases from {DISEASES_FILE}...")

    # Read TSV file
    rows = read_tsv(DISEASES_FILE)
    print(f"  Found {len(rows)} disease records")

    # Build CUI to ID mapping (for associations)
    cui_to_id = {}

    # Process in batches
    imported = 0
    skipped = 0

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]

        for row in batch:
            # Check if already exists
            existing = await session.execute(
                select(SympganDisease).where(SympganDisease.cui == row["Disease_CUI"])
            )
            if existing.scalars().first():
                # Get existing ID
                existing = await session.execute(
                    select(SympganDisease.id).where(SympganDisease.cui == row["Disease_CUI"])
                )
                cui_to_id[row["Disease_CUI"]] = existing.scalar()
                skipped += 1
                continue

            # Create new disease
            disease = SympganDisease(
                cui=row["Disease_CUI"],
                name=row["Disease_Name"],
                alias=row["Alias"] if row["Alias"] else None,
                definition=row["Definition"] if row["Definition"] else None,
                external_ids=row["External_Ids"] if row["External_Ids"] else None,
            )
            session.add(disease)
            imported += 1

        # Commit batch
        await session.commit()

        # Build CUI to ID mapping for this batch
        for row in batch:
            if row["Disease_CUI"] not in cui_to_id:
                result = await session.execute(
                    select(SympganDisease.id).where(SympganDisease.cui == row["Disease_CUI"])
                )
                cui_to_id[row["Disease_CUI"]] = result.scalar()

    print(f"  Imported: {imported}, Skipped (existing): {skipped}")
    return cui_to_id


async def import_symptoms(session: AsyncSession) -> dict[str, int]:
    """Import symptoms from TSV file

    Args:
        session: Database session

    Returns:
        Dictionary with CUI to ID mapping
    """
    print(f"\n[2/3] Importing symptoms from {SYMPTOMS_FILE}...")

    # Read TSV file
    rows = read_tsv(SYMPTOMS_FILE)
    print(f"  Found {len(rows)} symptom records")

    # Build CUI to ID mapping (for associations)
    cui_to_id = {}

    # Process in batches
    imported = 0
    skipped = 0

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]

        for row in batch:
            # Check if already exists
            existing = await session.execute(
                select(SympganSymptom).where(SympganSymptom.cui == row["Symptom_CUI"])
            )
            if existing.scalars().first():
                # Get existing ID
                existing = await session.execute(
                    select(SympganSymptom.id).where(SympganSymptom.cui == row["Symptom_CUI"])
                )
                cui_to_id[row["Symptom_CUI"]] = existing.scalar()
                skipped += 1
                continue

            # Create new symptom
            symptom = SympganSymptom(
                cui=row["Symptom_CUI"],
                name=row["Symptom_Name"],
                alias=row["Alias"] if row["Alias"] else None,
                definition=row["Definition"] if row["Definition"] else None,
                external_ids=row["External_Ids"] if row["External_Ids"] else None,
            )
            session.add(symptom)
            imported += 1

        # Commit batch
        await session.commit()

        # Build CUI to ID mapping for this batch
        for row in batch:
            if row["Symptom_CUI"] not in cui_to_id:
                result = await session.execute(
                    select(SympganSymptom.id).where(SympganSymptom.cui == row["Symptom_CUI"])
                )
                cui_to_id[row["Symptom_CUI"]] = result.scalar()

    print(f"  Imported: {imported}, Skipped (existing): {skipped}")
    return cui_to_id


async def import_associations(
    session: AsyncSession, disease_cui_to_id: dict[str, int], symptom_cui_to_id: dict[str, int]
) -> None:
    """Import disease-symptom associations from TSV file

    Args:
        session: Database session
        disease_cui_to_id: Mapping from disease CUI to database ID
        symptom_cui_to_id: Mapping from symptom CUI to database ID
    """
    print(f"\n[3/3] Importing associations from {ASSOCIATIONS_FILE}...")

    # Read TSV file
    rows = read_tsv(ASSOCIATIONS_FILE)
    print(f"  Found {len(rows)} association records")

    # Process in batches
    imported = 0
    skipped_disease = 0
    skipped_symptom = 0
    skipped_existing = 0

    for i in tqdm(range(0, len(rows), BATCH_SIZE), desc="  Progress"):
        batch = rows[i : i + BATCH_SIZE]

        for row in batch:
            disease_cui = row["Disease_CUI"]
            symptom_cui = row["Symptom_CUI"]

            # Get IDs from CUI mappings
            disease_id = disease_cui_to_id.get(disease_cui)
            symptom_id = symptom_cui_to_id.get(symptom_cui)

            if not disease_id:
                skipped_disease += 1
                continue
            if not symptom_id:
                skipped_symptom += 1
                continue

            # Check if association already exists
            existing = await session.execute(
                select(SympganDiseaseSymptomAssociation).where(
                    SympganDiseaseSymptomAssociation.disease_id == disease_id,
                    SympganDiseaseSymptomAssociation.symptom_id == symptom_id,
                )
            )
            if existing.scalars().first():
                skipped_existing += 1
                continue

            # Create new association
            association = SympganDiseaseSymptomAssociation(
                disease_id=disease_id,
                symptom_id=symptom_id,
                source=row["Source"] if row["Source"] else None,
            )
            session.add(association)
            imported += 1

        # Commit batch
        await session.commit()

    print(f"\n  Imported: {imported}")
    print(f"  Skipped - disease not found: {skipped_disease}")
    print(f"  Skipped - symptom not found: {skipped_symptom}")
    print(f"  Skipped - existing association: {skipped_existing}")


async def main():
    """Main import function"""
    print("=" * 60)
    print("SympGAN Dataset Import")
    print("=" * 60)

    # Verify data files exist
    for file_path in [DISEASES_FILE, SYMPTOMS_FILE, ASSOCIATIONS_FILE]:
        if not file_path.exists():
            print(f"\nError: Data file not found: {file_path}")
            print("Please ensure the SympGAN dataset is in ./data/sympgan/")
            return

    # Get database session
    async with await SQLiteClientWrapper.get_session() as session:
        # Import diseases and get CUI to ID mapping
        disease_cui_to_id = await import_diseases(session)

        # Import symptoms and get CUI to ID mapping
        symptom_cui_to_id = await import_symptoms(session)

        # Import associations using the mappings
        await import_associations(session, disease_cui_to_id, symptom_cui_to_id)

    print("\n" + "=" * 60)
    print("Import completed successfully!")
    print("=" * 60)

    # Show statistics
    async with await SQLiteClientWrapper.get_session() as session:
        from sqlalchemy import func

        # Count diseases
        disease_count = await session.execute(select(func.count()).select_from(SympganDisease))
        print(f"\nTotal diseases in database: {disease_count.scalar()}")

        # Count symptoms
        symptom_count = await session.execute(select(func.count()).select_from(SympganSymptom))
        print(f"Total symptoms in database: {symptom_count.scalar()}")

        # Count associations
        assoc_count = await session.execute(
            select(func.count()).select_from(SympganDiseaseSymptomAssociation)
        )
        print(f"Total disease-symptom associations: {assoc_count.scalar()}")


if __name__ == "__main__":
    asyncio.run(main())
