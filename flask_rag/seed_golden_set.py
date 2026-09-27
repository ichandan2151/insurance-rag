"""Load golden Q&A set from JSON into the database."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from models import SessionLocal, GoldenQA, init_db


def seed(json_path: str):
    init_db()
    session = SessionLocal()
    try:
        with open(json_path) as f:
            golden_set = json.load(f)

        # Clear existing entries
        session.query(GoldenQA).delete()

        for item in golden_set:
            qa = GoldenQA(
                question=item["question"],
                expected_answer=item["expected_answer"],
                source_document=item.get("source_document"),
                source_page=item.get("source_page"),
            )
            session.add(qa)

        session.commit()
        print(f"Seeded {len(golden_set)} golden Q&A pairs.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    json_path = os.path.join(
        os.path.dirname(__file__), "..", "sample_data", "golden_set.json"
    )
    seed(json_path)
