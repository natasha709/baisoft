# ============================================
# BAISoft Product Marketplace - Frontend Dockerfile
# ============================================

# Use official Node.js runtime as base image
FROM node:18-alpine as base

# Set environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Set work directory
WORKDIR /app


# ============================================
# Dependencies Stage
# ============================================
FROM base as deps

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci


# ============================================
# Development Stage
# ============================================
FROM base as development

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy project files
COPY . .

# Expose port
EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev"]


# ============================================
# Builder Stage
# ============================================
FROM base as builder

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy project files
COPY . .

# Build the application
RUN npm run build


# ============================================
# Production Stage
# ============================================
FROM base as production

# Install production dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Expose port
EXPOSE 3000

# Set environment variables
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Run the application
CMD ["node", "server.js"]
