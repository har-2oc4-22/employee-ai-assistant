"""
scripts/ingest_documents.py
-----------------------------
CLI script to ingest company documents into ChromaDB.

Usage (from the backend/ directory):
    python scripts/ingest_documents.py
    python scripts/ingest_documents.py --force

The --force flag re-embeds all documents even if they are already stored.
"""

import argparse
import sys
import os
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add the backend directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.rag.ingestion import ingest_documents

# Simple console logging for the CLI
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Ingest company documents into ChromaDB for RAG."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion: clear existing ChromaDB data and re-embed all documents.",
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=settings.DOCUMENTS_DIR,
        help=f"Path to the documents directory (default: {settings.DOCUMENTS_DIR})",
    )
    args = parser.parse_args()

    # Validate API key
    if not settings.GEMINI_API_KEY:
        logger.critical("❌ GEMINI_API_KEY is not set in your .env file. Aborting.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  Employee AI Assistant — Document Ingestion Pipeline")
    print("=" * 60)
    print(f"  Documents directory : {args.docs_dir}")
    print(f"  ChromaDB path       : {settings.CHROMA_PERSIST_DIRECTORY}")
    print(f"  Collection name     : {settings.CHROMA_COLLECTION_NAME}")
    print(f"  Embedding model     : {settings.GEMINI_EMBEDDING_MODEL}")
    print(f"  Chunk size          : {settings.CHUNK_SIZE}")
    print(f"  Chunk overlap       : {settings.CHUNK_OVERLAP}")
    print(f"  Force re-ingest     : {args.force}")
    print("=" * 60 + "\n")

    try:
        result = ingest_documents(
            documents_dir=args.docs_dir,
            force_reingest=args.force,
        )

        print("\n" + "=" * 60)
        if result["status"] == "success":
            print("✅ Ingestion completed successfully!")
            print(f"   Documents processed : {result.get('documents_loaded', 'N/A')}")
            print(f"   Chunks created      : {result.get('chunks_created', 'N/A')}")
            print(f"   Total chunks in DB  : {result.get('total_chunks_in_db', 'N/A')}")
        elif result["status"] == "skipped":
            print("ℹ️  Ingestion skipped.")
            print(f"   Reason              : {result.get('reason')}")
            print(f"   Existing chunks     : {result.get('existing_chunks')}")
            print("   Use --force to re-embed all documents.")
        else:
            print("❌ Ingestion failed.")
            print(f"   Reason: {result.get('reason')}")
            sys.exit(1)
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error("Ingestion failed with exception: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
