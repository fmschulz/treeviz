#!/usr/bin/env bun

import { chromium } from '@playwright/test'

interface Options {
  url: string
  timeoutMs: number
}

function parseArgs(argv: string[]): Options {
  let url = 'https://treeviz.newlineages.com/'
  let timeoutMs = 30_000
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]
    if (arg === '--url') {
      url = argv[++i] ?? url
      continue
    }
    if (arg === '--timeout-ms') {
      timeoutMs = Number(argv[++i] ?? timeoutMs)
      continue
    }
  }
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error('--timeout-ms must be a positive number')
  }
  return { url, timeoutMs }
}

function withParams(base: string, params: Record<string, string>): string {
  const url = new URL(base)
  for (const [key, value] of Object.entries(params)) url.searchParams.set(key, value)
  return url.toString()
}

async function main(): Promise<void> {
  const options = parseArgs(process.argv.slice(2))
  const base = new URL(options.url)
  const commandSchemaUrl = new URL('/treeviz-command-schema.json', base).toString()
  const schemaResponse = await fetch(commandSchemaUrl)
  if (!schemaResponse.ok) {
    throw new Error(`${commandSchemaUrl} returned HTTP ${schemaResponse.status}`)
  }
  const commandSchema = (await schemaResponse.json()) as {
    commands?: Array<{ id?: string }>
  }
  const schemaIds = (commandSchema.commands ?? []).map((command) => command.id).sort()
  if (schemaIds.length === 0) throw new Error('published command schema has no commands')

  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()
  const consoleErrors: string[] = []
  const pageErrors: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })
  page.on('pageerror', (error) => pageErrors.push(error.message))

  try {
    await page.goto(withParams(base.toString(), { api: '1' }), {
      waitUntil: 'domcontentloaded',
      timeout: options.timeoutMs
    })
    await page.waitForFunction(() => Boolean((window as { __treeviz?: unknown }).__treeviz), {
      timeout: options.timeoutMs
    })

    const result = await page.evaluate(async () => {
      type API = {
        commands: () => Array<{ id: string }>
        execute: (id: string, args: unknown) => Promise<{ ok: boolean; error?: unknown }>
        getDiagnostics: () => Array<{ level: string; code: string; message: string }>
        planMetadataImport: (
          source: string,
          format: 'tsv',
          prompt?: string
        ) => {
          suggestedBinding: {
            rowKeyColumn: string
            flags: unknown
            leafIdentifierSource: unknown
          }
          recommendedTracks: unknown[]
        } | null
        applyTrackRecommendations: (recommendations: unknown[]) => Promise<unknown>
        exportSvg: () => string
        getSession: () => { tracks: unknown[] } | null
        onReady: (cb: () => void) => () => void
      }
      const api = (window as { __treeviz: API }).__treeviz
      const ready = new Promise<void>((resolve) => api.onReady(resolve))
      const importResult = await api.execute('session.import-tree', {
        source: '(A,B,(C,D));',
        name: 'agent-smoke.nwk',
        format: 'newick'
      })
      await ready
      if (!importResult.ok) return { ok: false, reason: 'tree import failed', importResult }

      const metadata = [
        'id\tgroup\tvalue',
        'A\talpha\t1.2',
        'B\talpha\t0.8',
        'C\tbeta\t2.1',
        'D\tbeta\t1.6'
      ].join('\n')
      const plan = api.planMetadataImport(metadata, 'tsv', 'color by group and value')
      if (!plan) return { ok: false, reason: 'metadata planning failed' }
      const metadataResult = await api.execute('session.import-metadata', {
        source: metadata,
        format: 'tsv',
        rowKeyColumn: plan.suggestedBinding.rowKeyColumn,
        flags: plan.suggestedBinding.flags,
        leafIdentifierSource: plan.suggestedBinding.leafIdentifierSource
      })
      if (!metadataResult.ok) return { ok: false, reason: 'metadata import failed', metadataResult }
      await api.applyTrackRecommendations(plan.recommendedTracks)
      const trackResult = await api.execute('track.add', { kind: 'gradient', columnKey: 'value' })
      if (!trackResult.ok) return { ok: false, reason: 'track add failed', trackResult }

      const diagnostics = api.getDiagnostics()
      const errors = diagnostics.filter((diagnostic) => diagnostic.level === 'error')
      const svg = api.exportSvg()
      const commandIds = api.commands().map((command) => command.id).sort()
      return {
        ok: true,
        commandIds,
        diagnostics,
        errors,
        svgBytes: svg.length,
        trackCount: api.getSession()?.tracks.length ?? 0
      }
    })

    if (!result.ok) throw new Error(`browser API smoke failed: ${JSON.stringify(result)}`)
    const missing = schemaIds.filter((id) => !result.commandIds.includes(id))
    const extra = result.commandIds.filter((id) => !schemaIds.includes(id))
    if (missing.length > 0 || extra.length > 0) {
      throw new Error(`command ids differ from schema: missing=${missing} extra=${extra}`)
    }
    if (result.errors.length > 0) {
      throw new Error(`TreeViz diagnostics contain errors: ${JSON.stringify(result.errors)}`)
    }
    if (result.svgBytes <= 0) throw new Error('exportSvg returned an empty string')
    if (result.trackCount <= 0) throw new Error('agent workflow did not create tracks')
    if (consoleErrors.length > 0) throw new Error(`console errors: ${consoleErrors.join('\n')}`)
    if (pageErrors.length > 0) throw new Error(`page errors: ${pageErrors.join('\n')}`)

    console.log(
      `TreeViz API smoke passed at ${base.toString()} (${schemaIds.length} commands, ${result.svgBytes} SVG bytes)`
    )
  } finally {
    await browser.close()
  }
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : String(err))
  process.exit(1)
})
