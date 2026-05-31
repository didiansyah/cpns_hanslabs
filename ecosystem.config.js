module.exports = {
  apps: [
    {
      name: "cpns-backend",
      cwd: "/root/cpns/backend",
      script: "venv/bin/python",
      args: "-m uvicorn main:app --host 127.0.0.1 --port 3051",
      env: { PYTHONUNBUFFERED: "1" },
      max_memory_restart: "300M",
      autorestart: true,
    },
    {
      name: "cpns-frontend",
      cwd: "/root/cpns/frontend",
      script: "/root/.hermes/node/bin/npm",
      args: "start -- -p 3050",
      interpreter: "/root/.hermes/node/bin/node",
      env: { NODE_ENV: "production", PORT: "3050" },
      max_memory_restart: "300M",
      autorestart: true,
    },
  ],
};
