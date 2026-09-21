"""
scripts/ingest_documents.py
-----------------------------
CLI script to ingest company documents into ChromaDB.
Yeh script company ke policy documents (PDF, MD, TXT) ko read karti hai,
unhe chote chote chunks me divide karti hai, Gemini se embeddings generate karti hai,
aur ChromaDB vector database me save karti hai.

Usage (backend directory se run karein):
    python scripts/ingest_documents.py
    python scripts/ingest_documents.py --force

Note: --force flag purane data ko clear karke sab documents ko firse re-embed karta hai.
"""

import argparse
import sys
import os
import logging

# Windows terminal me special characters properly display ho iske liye UTF-8 enable karte hain
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Backend directory ko Python path me add kar rahe hain taaki app modules import ho sakein
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.rag.ingestion import ingest_documents

# Terminal output ke liye clean logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main():
    # Command line arguments parse karte hain (jaise --force ya custom docs folder)
    parser = argparse.ArgumentParser(
        description="Ingest company documents into ChromaDB for RAG."
    )
    # --force flag: agar collection me pehle se data hai toh bhi dobara fresh ingest karega
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion: clear existing ChromaDB data and re-embed all documents.",
    )
    # Documents kis folder me hain uska path (default: data/documents)
    parser.add_argument(
        "--docs-dir",
        type=str,
        default=settings.DOCUMENTS_DIR,
        help=f"Path to the documents directory (default: {settings.DOCUMENTS_DIR})",
    )
    args = parser.parse_args()

    # Pehle verify karte hain ki Gemini API key set hai ya nahi
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
        # Asli ingestion function ko call karte hain (load -> chunk -> embed -> store)
        result = ingest_documents(
            documents_dir=args.docs_dir,
            force_reingest=args.force,
        )

        print("\n" + "=" * 60)
        # Agar documents successfully ChromaDB me save ho gaye
        if result["status"] == "success":
            print("✅ Ingestion completed successfully!")
            print(f"   Documents processed : {result.get('documents_loaded', 'N/A')}")
            print(f"   Chunks created      : {result.get('chunks_created', 'N/A')}")
            print(f"   Total chunks in DB  : {result.get('total_chunks_in_db', 'N/A')}")
        # Agar pehle se data maujood hai aur --force pass nahi kiya gaya
        elif result["status"] == "skipped":
            print("ℹ️  Ingestion skipped.")
            print(f"   Reason              : {result.get('reason')}")
            print(f"   Existing chunks     : {result.get('existing_chunks')}")
            print("   Use --force to re-embed all documents.")
        # Agar koi issue aaya ho
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
