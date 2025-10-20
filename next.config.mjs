/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [`${process.env.NEXT_PUBLIC_AWS_S3_BUCKET}.s3.${process.env.NEXT_PUBLIC_AWS_REGION}.amazonaws.com`],
  },
};

export default nextConfig;
