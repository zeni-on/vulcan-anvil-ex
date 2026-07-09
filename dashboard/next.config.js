/** @type {import('next').NextConfig} */
const nextConfig = {
  // Keep Next's file tracing inside the dashboard app. Without this, a parent
  // package-lock.json can make Next scan sample project cache folders.
  outputFileTracingRoot: process.cwd(),

  // ESM-only packages used by the markdown document viewer.
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

module.exports = nextConfig
