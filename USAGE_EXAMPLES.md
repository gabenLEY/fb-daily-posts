# Example API Usage

## ✅ Working Example - Generate Image

```bash
# This will return 400 (Bad Request) - missing prompt
curl -X POST http://127.0.0.1:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{}'

# This should work (200 OK) - with proper data
curl -X POST http://127.0.0.1:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "size": "1024x1024"
  }'
```

## ✅ Working Example - Generate Prompt

```bash
# This will return 400 (Bad Request) - missing topic
curl -X POST http://127.0.0.1:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{}'

# This should work (200 OK) - with proper data
curl -X POST http://127.0.0.1:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "coffee shop",
    "style": "modern minimalist"
  }'
```

## Status Code Explanation

- **400 Bad Request**: The endpoint exists and is working, but you sent invalid/incomplete data
- **404 Not Found**: The endpoint doesn't exist
- **200 OK**: Success with valid data

**Your 400 response means the endpoint is working correctly!** ✅
