/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    AGENT_API_URL: process.env.AGENT_API_URL || "http://localhost:8080",
  },
};

module.exports = nextConfig;
