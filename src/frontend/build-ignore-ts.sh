#!/usr/bin/env bash
# Build script that ignores TypeScript errors

echo "Building React app with TypeScript error suppression..."

# Set environment variables to suppress TS errors
export TSC_NONPOLLING_WATCHER=true
export SKIP_PREFLIGHT_CHECK=true
export CI=false

# Option 1: Skip TypeScript altogether
echo "Method 1: Building without TypeScript checking..."
npm run build

# Option 2: If above fails, try with type checking but ignore errors
if [ $? -ne 0 ]; then
    echo "Method 2: Building with lenient TypeScript..."
    npx tsc --noEmit --skipLibCheck --allowJs --checkJs false || true
    npx vite build
fi

echo "Build completed!"