# Frontend Integration Guide

## 🚨 **Issue Found**: Missing `prompt` field

Based on the debug logs, your frontend is sending:

```json
{
  "size": "1024x1024"
}
```

But the API requires:

```json
{
  "prompt": "Your image description here",
  "size": "1024x1024"
}
```

## ✅ **Frontend Code Examples**

### JavaScript/Fetch:

```javascript
// ❌ WRONG - Missing prompt
const wrongData = {
  size: "1024x1024",
};

// ✅ CORRECT - With prompt
const correctData = {
  prompt: "A beautiful sunset over mountains",
  size: "1024x1024",
};

fetch("http://127.0.0.1:8000/api/generate-image", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(correctData),
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

### Axios:

```javascript
// ✅ CORRECT - With prompt
axios
  .post("http://127.0.0.1:8000/api/generate-image", {
    prompt: "A beautiful sunset over mountains",
    size: "1024x1024",
  })
  .then((response) => console.log(response.data))
  .catch((error) => console.error(error.response.data));
```

### cURL:

```bash
# ✅ CORRECT - With prompt
curl -X POST http://127.0.0.1:8000/api/generate-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "size": "1024x1024"
  }'
```

## 📋 **Required Fields**

### `/api/generate-image`:

- ✅ **Required:** `prompt` (string) - Description of the image to generate
- 🔧 **Optional:** `size` (string) - Image dimensions (default: "1024x1024")

### `/api/prompt`:

- ✅ **Required:** `topic` (string) - Topic for the prompt
- 🔧 **Optional:** `style` (string) - Style description (default: "clean product shot")

## 🎯 **Your API is Working Perfectly!**

The 400 error is **correct validation** - just add the missing `prompt` field to your frontend request.
