const nextConfig = {

  reactStrictMode: true,

  swcMinify: true,

  images: {

    domains: [],

    unoptimized: false,
  },

  env: {
    CUSTOM_KEY: 'my-value',
  },

  experimental: {

    appDir: true,
  },

  async redirects() {
    return [

    ]
  },

  async rewrites() {
    return [

    ]
  },

  async headers() {
    return [
      {

        source: '/(.*)',
        headers: [

          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },

          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },

          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },

          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
