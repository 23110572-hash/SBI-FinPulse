/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Tree-shake heavy icon / animation libraries by importing only the
  // symbols actually used. Massive win for first-paint and dev compile.
  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion"],
  },
  async rewrites() {
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [{ source: "/proxy/:path*", destination: `${api}/:path*` }];
  },
};

module.exports = nextConfig;
