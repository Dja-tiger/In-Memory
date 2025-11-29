FROM tarantool/tarantool:latest

# Install HTTP server module and dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    make \
    cmake \
    libssl-dev \
    && tt rocks install http \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY app.lua /opt/tarantool/app.lua

# Expose ports
EXPOSE 3301 8080

# Run Tarantool with the application
CMD ["tarantool", "/opt/tarantool/app.lua"]