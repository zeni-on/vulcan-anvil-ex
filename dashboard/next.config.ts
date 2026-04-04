import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
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
