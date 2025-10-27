#!/bin/bash
# CLI to ingest new documents

echo "Starting document ingestion pipeline..."

python pipelines/ingestion_pipeline.py \
  --input-dir "./data/docs" \
  --output-dir "./data/processed"

echo "Document ingestion completed!"
