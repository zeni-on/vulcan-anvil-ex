import { NextRequest, NextResponse } from 'next/server'

const TOKEN_COOKIE = 'vulcan_dashboard_token'
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS'])
const LOOPBACK_HOSTS = new Set(['localhost', '127.0.0.1', '::1'])

function requestHostname(req: NextRequest): string {
  const host = req.headers.get('host') || req.nextUrl.host
  try {
    return new URL(`http://${host}`).hostname.replace(/^\[|\]$/g, '').toLowerCase()
  } catch {
    return ''
  }
}

function isLoopbackUrl(value: string): boolean {
  try {
    return LOOPBACK_HOSTS.has(new URL(value).hostname.toLowerCase())
  } catch {
    return false
  }
}

function denied(message: string, status = 403): NextResponse {
  return NextResponse.json({ error: message }, { status })
}

export function middleware(req: NextRequest) {
  const allowRemote = process.env.VULCAN_DASHBOARD_ALLOW_REMOTE === '1'
  if (!allowRemote && !LOOPBACK_HOSTS.has(requestHostname(req))) {
    return denied('Dashboard accepts loopback access only')
  }

  const expectedToken = process.env.VULCAN_DASHBOARD_TOKEN?.trim()
  const suppliedQueryToken = req.nextUrl.searchParams.get('token')
  if (expectedToken && suppliedQueryToken === expectedToken && !req.nextUrl.pathname.startsWith('/api/')) {
    const redirectUrl = req.nextUrl.clone()
    redirectUrl.searchParams.delete('token')
    const response = NextResponse.redirect(redirectUrl)
    response.cookies.set(TOKEN_COOKIE, expectedToken, {
      httpOnly: true,
      sameSite: 'strict',
      secure: req.nextUrl.protocol === 'https:',
      path: '/',
    })
    return response
  }

  if (expectedToken) {
    const cookieToken = req.cookies.get(TOKEN_COOKIE)?.value
    const headerToken = req.headers.get('x-vulcan-dashboard-token')
    if (cookieToken !== expectedToken && headerToken !== expectedToken) {
      return denied('Dashboard token required', 401)
    }
  }

  if (req.nextUrl.pathname.startsWith('/api/') && !SAFE_METHODS.has(req.method)) {
    const origin = req.headers.get('origin')
    if (origin && !allowRemote && !isLoopbackUrl(origin)) {
      return denied('Cross-origin write request denied')
    }
  }

  const response = NextResponse.next()
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'no-referrer')
  response.headers.set('X-Frame-Options', 'DENY')
  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
