FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Set environment variable for build time (Client side components need this)
# Since the user accesses via browser, localhost:8001 is correct
ENV NEXT_PUBLIC_API_URL=http://localhost:8001

# Build the application
RUN npm run build

# Production image
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/.next/standalone ./

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
