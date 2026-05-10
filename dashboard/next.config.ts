import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Keep Next's file tracing inside the dashboard app. Without this, a parent
  // package-lock.json can make Next scan sample project cache folders.
  outputFileTracingRoot: process.cwd(),

  // ESM-only 패키지 트랜스파일 (react-markdown, remark-gfm, rehype-sanitize)
  transpilePackages: [
    'react-markdown',
    'remark-gfm',
    'rehype-sanitize',
    'remark-parse',
    'remark-rehype',
    'unified',
    'vfile',
    'unist-util-visit',
    'hast-util-sanitize',
    'mdast-util-gfm',
  ],
}

export default nextConfig
