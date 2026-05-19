#!/usr/bin/env bun

import { copyFileSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { extname, join, resolve, sep } from 'node:path'
import { spawn, spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { dirname } from 'node:path'
import { homedir } from 'node:os'

interface Options {
  port: number
  session?: string
  open: boolean
  headless: boolean
}

const MIME: Record<string, string> = {
  '.css': 'text/css; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.txt': 'text/plain; charset=utf-8',
  '.woff2': 'font/woff2'
}

function parseArgs(argv: string[]): Options {
  let port = 5174
  let session: string | undefined
  let open = true
  let headless = false

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]
    if (arg === '--port') {
      port = Number(argv[++i] ?? port)
      continue
    }
    if (arg === '--session') {
      session = argv[++i]
      continue
    }
    if (arg === '--no-open') {
      open = false
      continue
    }
    if (arg === '--headless') {
      headless = true
      continue
    }
  }

  if (!Number.isInteger(port) || port < 0 || port > 65535) {
    throw new Error('--port must be an integer between 0 and 65535')
  }

  return session === undefined
    ? { port, open, headless }
    : { port, session, open, headless }
}

function cacheRoot(): string {
  const base = process.env.XDG_CACHE_HOME ?? join(homedir(), '.cache')
  return join(base, 'treeviz-agent')
}

function extractApp(archivePath: string, manifestText: string): string {
  const appDir = join(cacheRoot(), 'app')
  const marker = join(appDir, '.treeviz-app.manifest.json')
  const needsExtract =
    !existsSync(join(appDir, 'index.html')) ||
    !existsSync(marker) ||
    readFileSync(marker, 'utf8') !== manifestText

  if (!needsExtract) return appDir

  rmSync(appDir, { recursive: true, force: true })
  mkdirSync(appDir, { recursive: true })
  const result = spawnSync('tar', ['-xzf', archivePath, '-C', appDir], {
    stdio: 'inherit'
  })
  if (result.status !== 0) {
    throw new Error(`failed to extract ${archivePath}`)
  }
  writeFileSync(marker, manifestText)
  return appDir
}

function resolveRequestPath(root: string, pathname: string): string {
  const trimmed = decodeURIComponent(pathname).replace(/^\/+/, '')
  const requested = trimmed === '' ? 'index.html' : trimmed
  const resolved = resolve(root, requested)
  const allowedPrefix = `${root}${sep}`
  if (resolved !== root && !resolved.startsWith(allowedPrefix)) {
    return resolve(root, 'index.html')
  }
  return existsSync(resolved) ? resolved : resolve(root, 'index.html')
}

function openBrowser(url: string): void {
  const command =
    process.platform === 'darwin'
      ? { cmd: 'open', args: [url] }
      : process.platform === 'win32'
        ? { cmd: 'cmd', args: ['/c', 'start', '', url] }
        : { cmd: 'xdg-open', args: [url] }
  spawn(command.cmd, command.args, { detached: true, stdio: 'ignore' }).unref()
}

async function main(): Promise<void> {
  const options = parseArgs(process.argv.slice(2))
  const scriptDir = dirname(fileURLToPath(import.meta.url))
  const skillDir = resolve(scriptDir, '..')
  const archivePath = resolve(skillDir, 'assets/treeviz-app.tar.gz')
  const manifestPath = resolve(skillDir, 'assets/treeviz-app.manifest.json')

  if (!existsSync(archivePath) || !existsSync(manifestPath)) {
    throw new Error('precompiled TreeViz app asset is missing; run bun run package:app')
  }

  const manifestText = readFileSync(manifestPath, 'utf8')
  const appDir = extractApp(archivePath, manifestText)

  if (options.session) {
    copyFileSync(resolve(options.session), join(appDir, '__treeviz_compiled_session.json'))
  }

  const server = Bun.serve({
    hostname: '127.0.0.1',
    port: options.port,
    async fetch(request) {
      const url = new URL(request.url)
      const filePath = resolveRequestPath(appDir, url.pathname)
      const headers = new Headers()
      const type = MIME[extname(filePath)]
      if (type) headers.set('Content-Type', type)
      if (filePath.endsWith('__treeviz_compiled_session.json')) {
        headers.set('Cache-Control', 'private, no-store')
      }
      return new Response(Bun.file(filePath), { headers })
    }
  })

  const query = new URLSearchParams({ api: '1' })
  if (options.headless) query.set('mode', 'headless')
  if (options.session) query.set('session', '__treeviz_compiled_session.json')
  const url = `http://127.0.0.1:${server.port}/?${query.toString()}`

  console.log(`TreeViz app: ${appDir}`)
  console.log(`Listening: ${url}`)
  if (options.open) openBrowser(url)

  process.on('SIGINT', () => {
    server.stop()
    process.exit(0)
  })

  await new Promise(() => undefined)
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err))
  process.exit(1)
})
