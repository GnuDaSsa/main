/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: "/",
        destination: "/mvp.html",
        permanent: false
      }
    ];
  }
};

export default nextConfig;
