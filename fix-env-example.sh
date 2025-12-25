#!/bin/bash
# Script to replace API keys in .env.example with placeholders

if [ -f .env.example ]; then
    # Replace OpenAI API key
    sed -i 's/sk-proj-[a-zA-Z0-9\-]*/your-openai-api-key-here/g' .env.example
    # Replace OpenRouter API key  
    sed -i 's/sk-or-v1-[a-zA-Z0-9]*/your-openrouter-api-key-here/g' .env.example
    # Replace Facebook access token
    sed -i 's/EAAG[^"]*/your-facebook-page-access-token/g' .env.example
    git add .env.example
fi


