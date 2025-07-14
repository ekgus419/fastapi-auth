#!/bin/bash

echo "🧪 Running mock-based unit tests only... 🧪"

pytest tests \
  -k "_with_mock" \
  --asyncio-mode=auto \
  -v --tb=short
