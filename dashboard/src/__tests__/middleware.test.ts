import { NextRequest } from 'next/server'
import { middleware } from '@/middleware'

function request(url: string, init: ConstructorParameters<typeof NextRequest>[1] = {}) {
  return new NextRequest(url, init)
}

describe('Dashboard local access middleware', () => {
  const originalToken = process.env.VULCAN_DASHBOARD_TOKEN
  const originalRemote = process.env.VULCAN_DASHBOARD_ALLOW_REMOTE

  afterEach(() => {
    if (originalToken === undefined) delete process.env.VULCAN_DASHBOARD_TOKEN
    else process.env.VULCAN_DASHBOARD_TOKEN = originalToken
    if (originalRemote === undefined) delete process.env.VULCAN_DASHBOARD_ALLOW_REMOTE
    else process.env.VULCAN_DASHBOARD_ALLOW_REMOTE = originalRemote
  })

  it('rejects non-loopback hosts by default', () => {
    const response = middleware(request('http://192.168.0.5:3001/api/projects'))
    expect(response.status).toBe(403)
  })

  it('allows loopback requests', () => {
    const response = middleware(request('http://127.0.0.1:3001/api/projects'))
    expect(response.status).toBe(200)
  })

  it('rejects cross-origin write requests', () => {
    const response = middleware(request('http://127.0.0.1:3001/api/projects', {
      method: 'POST',
      headers: { origin: 'https://example.com' },
    }))
    expect(response.status).toBe(403)
  })

  it('requires the configured token and accepts the token header', () => {
    process.env.VULCAN_DASHBOARD_TOKEN = 'test-secret'
    const denied = middleware(request('http://127.0.0.1:3001/api/projects'))
    const allowed = middleware(request('http://127.0.0.1:3001/api/projects', {
      headers: { 'x-vulcan-dashboard-token': 'test-secret' },
    }))
    expect(denied.status).toBe(401)
    expect(allowed.status).toBe(200)
  })
})
