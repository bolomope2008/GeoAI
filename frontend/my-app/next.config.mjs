/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  assetPrefix: './',
  distDir: 'out',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  // Disable ESLint during builds for production
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  }
};

export default nextConfig;