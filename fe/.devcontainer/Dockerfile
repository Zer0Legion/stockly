FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Install required tools using apk (for Alpine)
RUN apk update && apk add --no-cache make git

RUN git config --global user.name "Ang Leng Khai"
RUN git config --global user.email "lengkhai@gmail.com"

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 3000

# Start the application
CMD ["npm", "run", "dev"]