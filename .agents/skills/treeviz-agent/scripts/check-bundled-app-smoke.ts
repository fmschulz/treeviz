#!/usr/bin/env bun

import { spawn } from 'node:child_process'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from '@playwright/test'

interface Options {
  timeoutMs: number
  session?: string
}

function parseArgs(argv: string[]): Options {
  let timeoutMs = 30_000
  let session: string | undefined
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--timeout-ms') timeoutMs = Number(argv[++i] ?? timeoutMs)
    if (argv[i] === '--session') session = argv[++i]
  }
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error('--timeout-ms must be a positive number')
  }
  return session === undefined ? { timeoutMs } : { timeoutMs, session }
}

function waitForListening(child: ReturnType<typeof spawn>, timeoutMs: number): Promise<string> {
  return new Promise((resolve, reject) => {
    let output = ''
    const timeout = setTimeout(() => {
      reject(new Error(`launcher did not print Listening within ${timeoutMs}ms\n${output}`))
    }, timeoutMs)
    child.stdout?.on('data', (chunk: Buffer) => {
      output += chunk.toString()
      const match = output.match(/Listening:\s+(http:\/\/127\.0\.0\.1:\d+\/\?\S+)/)
      if (match?.[1]) {
        clearTimeout(timeout)
        resolve(match[1])
      }
    })
    child.stderr?.on('data', (chunk: Buffer) => {
      output += chunk.toString()
    })
    child.on('exit', (code) => {
      clearTimeout(timeout)
      reject(new Error(`launcher exited with ${code}\n${output}`))
    })
  })
}

async function main(): Promise<void> {
  const options = parseArgs(process.argv.slice(2))
  const scriptDir = dirname(fileURLToPath(import.meta.url))
  const launcher = resolve(scriptDir, 'launch-treeviz-app.ts')
  const launcherArgs = [launcher, '--port', '0', '--headless', '--no-open']
  if (options.session) launcherArgs.push('--session', options.session)
  const child = spawn('bun', launcherArgs, {
    stdio: ['ignore', 'pipe', 'pipe']
  })

  let browser: Awaited<ReturnType<typeof chromium.launch>> | null = null
  try {
    const url = await waitForListening(child, options.timeoutMs)
    browser = await chromium.launch({ headless: true })
    const page = await browser.newPage()
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: options.timeoutMs })
    await page.waitForFunction(() => Boolean((window as { __treeviz?: unknown }).__treeviz), {
      timeout: options.timeoutMs
    })
    if (options.session) {
      await page.waitForFunction(
        () => Boolean((window as { __treeviz?: { getSession: () => unknown } }).__treeviz?.getSession()),
        { timeout: options.timeoutMs }
      )
    }
    const result = await page.evaluate(async () => {
      type API = {
        commands: () => Array<{ id: string }>
        execute: (id: string, args: unknown) => Promise<{ ok: boolean }>
        getDiagnostics: () => Array<{ level: string; code: string }>
        getSession: () => unknown | null
        exportSvg: () => string
        onReady: (cb: () => void) => () => void
      }
      const api = (window as { __treeviz: API }).__treeviz
      let imported: { ok: boolean } = { ok: true }
      if (!api.getSession()) {
        const ready = new Promise<void>((resolve) => api.onReady(resolve))
        imported = await api.execute('session.import-tree', {
          source: '(A,B,(C,D));',
          name: 'bundled-smoke.nwk'
        })
        await ready
      }
      return {
        imported,
        commandCount: api.commands().length,
        diagnostics: api.getDiagnostics(),
        svgBytes: api.exportSvg().length
      }
    })
    const errors = result.diagnostics.filter((diagnostic) => diagnostic.level === 'error')
    if (!result.imported.ok) throw new Error('bundled app tree import failed')
    if (errors.length > 0) throw new Error(`bundled app diagnostics failed: ${JSON.stringify(errors)}`)
    if (result.svgBytes <= 0) throw new Error('bundled app exportSvg returned empty output')
    console.log(
      `Bundled TreeViz app smoke passed (${result.commandCount} commands, ${result.svgBytes} SVG bytes)`
    )
  } finally {
    if (browser) await browser.close()
    child.kill('SIGINT')
  }
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err))
  process.exit(1)
})
