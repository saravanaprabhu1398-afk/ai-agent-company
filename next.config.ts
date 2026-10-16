import type { NextConfig } from "next";

// Security headers are added by the auth/hardening issue (architecture section 8).
const nextConfig: NextConfig = {
  // Stop `next dev` from writing agent rules into CLAUDE.md.
  agentRules: false,
};

export default nextConfig;
