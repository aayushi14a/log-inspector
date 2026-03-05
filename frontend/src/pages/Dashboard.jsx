import { useState, useRef, useEffect } from 'react'
import {
  Shield, Upload, Play, Download, FileText, BookOpen,
  LogOut, X, CheckCircle, AlertTriangle, Loader2, Brain,
  Clock, Zap, BarChart3, ChevronDown, ChevronUp
} from 'lucide-react'
import API_BASE from '../api'

// ─── Navbar ─────────────────────────────────────────────
function Navbar({ user, onLogout }) {
  return (
    <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brand-600/20 border border-brand-500/30 flex items-center justify-center">
            <Shield className="w-5 h-5 text-brand-400" />
          </div>
          <div>
            <span className="font-bold text-lg text-white">Log Inspector</span>
            <span className="hidden sm:inline text-gray-500 text-xs ml-2">A log triaging AI Agent</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400 hidden sm:block">
            {user.name || user.email}
          </span>
          <button
            onClick={onLogout}
            className="flex items-center gap-1.5 text-gray-400 hover:text-red-400 transition text-sm"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </nav>
  )
}

// ─── File Upload Component ──────────────────────────────
function FileUpload({ label, icon: Icon, accept, file, onFileChange, onClear, required, hint }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) onFileChange(dropped)
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-2">
        {label} {required && <span className="text-red-400">*</span>}
        {!required && <span className="text-gray-600 text-xs ml-1">(optional)</span>}
      </label>
      {!file ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
            dragOver
              ? 'border-brand-500 bg-brand-500/10'
              : 'border-gray-700 hover:border-gray-600 hover:bg-gray-800/30'
          }`}
        >
          <Icon className={`w-10 h-10 mx-auto mb-3 ${dragOver ? 'text-brand-400' : 'text-gray-500'}`} />
          <p className="text-sm text-gray-400">
            <span className="text-brand-400 font-medium">Click to upload</span> or drag and drop
          </p>
          {hint && <p className="text-xs text-gray-600 mt-1">{hint}</p>}
          <input
            ref={inputRef}
            type="file"
            accept={accept}
            onChange={(e) => e.target.files[0] && onFileChange(e.target.files[0])}
            className="hidden"
          />
        </div>
      ) : (
        <div className="flex items-center justify-between bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-brand-600/20 flex items-center justify-center">
              <Icon className="w-5 h-5 text-brand-400" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-200">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
          <button onClick={onClear} className="text-gray-500 hover:text-red-400 transition">
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  )
}

// ─── Agent Progress Panel ───────────────────────────────
function AgentProgress({ steps, isRunning }) {
  const scrollRef = useRef(null)
  const [expanded, setExpanded] = useState(true)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [steps])

  const getStepIcon = (type) => {
    switch (type) {
      case 'thinking': return <Brain className="w-4 h-4 text-purple-400" />
      case 'step': return <Zap className="w-4 h-4 text-brand-400" />
      case 'status': return <Clock className="w-4 h-4 text-yellow-400" />
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-400" />
      case 'complete': return <CheckCircle className="w-4 h-4 text-green-400" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className="card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full"
      >
        <div className="flex items-center gap-3">
          <Brain className="w-5 h-5 text-purple-400" />
          <h3 className="font-semibold text-gray-100">Agent Activity</h3>
          {isRunning && (
            <span className="flex items-center gap-1.5 text-xs text-brand-400 bg-brand-400/10 px-2 py-0.5 rounded-full">
              <span className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-pulse" />
              Processing
            </span>
          )}
        </div>
        {expanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>

      {expanded && (
        <div ref={scrollRef} className="mt-4 max-h-80 overflow-y-auto space-y-2 pr-1">
          {steps.length === 0 && !isRunning && (
            <p className="text-gray-600 text-sm text-center py-8">
              Agent activity will appear here when analysis starts
            </p>
          )}
          {steps.map((step, i) => (
            <div
              key={i}
              className={`flex gap-3 p-3 rounded-lg animate-slide-up ${
                step.type === 'error'
                  ? 'bg-red-500/5 border border-red-500/20'
                  : step.type === 'complete'
                  ? 'bg-green-500/5 border border-green-500/20'
                  : 'bg-gray-800/40'
              }`}
            >
              <div className="mt-0.5 flex-shrink-0">{getStepIcon(step.type)}</div>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-gray-500 mb-0.5">
                  {step.timestamp} — Step {i + 1}
                </p>
                <p className="text-sm text-gray-300 whitespace-pre-wrap break-words">
                  {step.message}
                </p>
              </div>
            </div>
          ))}
          {isRunning && (
            <div className="flex items-center gap-2 px-3 py-3 text-gray-400 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              Agent is working
              <span className="flex gap-0.5">
                <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full" />
                <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full" />
                <span className="typing-dot w-1 h-1 bg-gray-400 rounded-full" />
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── Report Rendering Helpers ────────────────────────────

function SeverityChip({ text }) {
  if (!text) return <span className="text-gray-500">—</span>
  const t = text.toString()
  const u = t.toUpperCase()
  if (u.includes('CRITICAL') || u.includes('P0') || u.includes('P1'))
    return <span className="inline-block text-xs font-semibold px-2 py-0.5 rounded bg-red-500/20 text-red-400">{t}</span>
  if (u.includes('ERROR') || u.includes('FAIL') || u.includes('P2'))
    return <span className="inline-block text-xs font-semibold px-2 py-0.5 rounded bg-orange-500/20 text-orange-400">{t}</span>
  if (u.includes('WARN') || u.includes('SLOW') || u.includes('TIMEOUT'))
    return <span className="inline-block text-xs font-semibold px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400">{t}</span>
  if (u.includes('OK') || u.includes('RESOLV') || u.includes('ACCEPT') || u.includes('SUCCESS'))
    return <span className="inline-block text-xs font-semibold px-2 py-0.5 rounded bg-green-500/20 text-green-400">{t}</span>
  return <span className="font-mono text-xs text-blue-300">{t}</span>
}

function ReportTable({ headers, rows, colStyles }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-gray-700/60 mb-5">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-800/80">
            {headers.map((h, i) => (
              <th key={i} className="text-left text-xs font-semibold text-gray-400 uppercase tracking-wide px-4 py-2.5 border-b border-gray-700/60">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri} className="border-b border-gray-800/60 hover:bg-gray-800/30 transition-colors">
              {row.map((cell, ci) => (
                <td key={ci} className={`px-4 py-2.5 text-gray-300 align-top ${colStyles?.[ci] || ''}`}>
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function SectionHeader({ title }) {
  const t = title.toLowerCase()
  let accent = 'text-blue-400'
  if (t.includes('timeline')) accent = 'text-purple-400'
  else if (t.includes('critical') || t.includes('root') || t.includes('top')) accent = 'text-red-400'
  else if (t.includes('slow') || t.includes('request')) accent = 'text-orange-400'
  else if (t.includes('service')) accent = 'text-yellow-400'
  else if (t.includes('immediate') || t.includes('action')) accent = 'text-yellow-400'
  else if (t.includes('long')) accent = 'text-green-400'
  else if (t.includes('security')) accent = 'text-red-400'
  return (
    <h4 className={`text-sm font-semibold uppercase tracking-wide mb-2 ${accent}`}>
      {title}
    </h4>
  )
}

// Parses "- Key: val, Key2: val2" bullet lines into {Key: val, ...}
function parseBulletKV(line) {
  const body = line.replace(/^[-•*]\s*/, '')
  const result = {}
  const parts = body.split(/,\s*(?=[A-Z][a-zA-Z ]+:)/)
  parts.forEach(p => {
    const idx = p.indexOf(':')
    if (idx !== -1) {
      const key = p.slice(0, idx).trim()
      const val = p.slice(idx + 1).trim()
      result[key] = val
    }
  })
  return Object.keys(result).length >= 2 ? result : null
}

function renderSection(title, body) {
  const tl = title.toLowerCase()
  const lines = body.split('\n').map(l => l.trim()).filter(Boolean)

  // ── Timeline: "timestamp, service, error_code" lines ──
  if (tl.includes('timeline')) {
    const rows = lines
      .filter(l => /^\d{4}-\d{2}-\d{2}/.test(l))
      .map(l => {
        const parts = l.split(',').map(s => s.trim())
        return [
          <span className="font-mono text-xs text-gray-400">{parts[0] || ''}</span>,
          <span className="text-gray-200">{parts[1] || ''}</span>,
          <SeverityChip text={parts[2] || ''} />,
        ]
      })
    return rows.length > 0
      ? <ReportTable headers={['Timestamp', 'Service', 'Error Code']} rows={rows} />
      : <p className="text-sm text-gray-400">{body}</p>
  }

  // ── Top 5 / Critical Issues: "- Service: X, Error Code: Y, …" ──
  if (tl.includes('critical') || tl.includes('top 5') || tl.includes('top five')) {
    const kvLines = lines.filter(l => /^[-•*]/.test(l))
    const parsed = kvLines.map(l => parseBulletKV(l)).filter(Boolean)
    if (parsed.length > 0) {
      const allKeys = [...new Set(parsed.flatMap(o => Object.keys(o)))]
      const rows = parsed.map(obj =>
        allKeys.map(k => {
          const val = obj[k] || '—'
          if (k.toLowerCase() === 'error code' || k.toLowerCase() === 'errorcode')
            return <SeverityChip text={val} />
          if (k.toLowerCase() === 'frequency' || k.toLowerCase() === 'root cause')
            return <span className="text-xs text-gray-400">{val}</span>
          return <span className="text-xs text-gray-200">{val}</span>
        })
      )
      return <ReportTable headers={allKeys} rows={rows} />
    }
  }

  // ── Slow Requests: "- At TIMESTAMP, Service: X, Error Code: Y, Root Cause: Z" ──
  if (tl.includes('slow') || tl.includes('request')) {
    const rows = lines
      .filter(l => /^[-•*]/.test(l))
      .map(l => {
        const body = l.replace(/^[-•*]\s*At\s*/i, '')
        const timeMatch = body.match(/^([\d\-T :\.]+),/)
        const ts = timeMatch ? timeMatch[1].trim() : ''
        const rest = timeMatch ? body.slice(timeMatch[0].length) : body
        const kv = {}
        rest.split(/,\s*(?=[A-Z][a-zA-Z ]+:)/).forEach(p => {
          const idx = p.indexOf(':')
          if (idx !== -1) kv[p.slice(0, idx).trim()] = p.slice(idx + 1).trim()
        })
        return [
          <span className="font-mono text-xs text-gray-400">{ts}</span>,
          <span className="text-gray-200 text-xs">{kv['Service'] || '—'}</span>,
          <SeverityChip text={kv['Error Code'] || kv['ErrorCode'] || '—'} />,
          <span className="text-xs text-gray-400">{kv['Root Cause'] || '—'}</span>,
        ]
      })
    return rows.length > 0
      ? <ReportTable headers={['Timestamp', 'Service', 'Error Code', 'Root Cause']} rows={rows} />
      : <p className="text-sm text-gray-400">{body}</p>
  }

  // ── Services Affected: comma-separated list ──
  if (tl.includes('service')) {
    const services = lines.join(' ').split(',').map(s => s.trim()).filter(Boolean)
    if (services.length > 1) {
      const rows = services.map((s, i) => [
        <span className="text-gray-500 text-xs">{i + 1}</span>,
        <span className="text-gray-200">{s}</span>,
      ])
      return <ReportTable headers={['#', 'Service']} rows={rows} colStyles={['w-8', '']} />
    }
  }

  // ── Actions / Fixes / Security: bullet lists → numbered table ──
  if (tl.includes('action') || tl.includes('fix') || tl.includes('security') || tl.includes('immediate') || tl.includes('long')) {
    const items = lines.filter(l => /^[-•*\d]/.test(l)).map(l => l.replace(/^[-•*\d.)\s]+/, '').trim())
    if (items.length > 0) {
      const rows = items.map((item, i) => [
        <span className="text-gray-500 text-xs font-mono">{i + 1}</span>,
        <span className="text-sm text-gray-300">{item}</span>,
      ])
      return <ReportTable headers={['#', 'Recommendation']} rows={rows} colStyles={['w-8', '']} />
    }
  }

  // ── Fallback: plain paragraph ──
  return <p className="text-sm text-gray-300 leading-relaxed mb-5">{lines.join(' ')}</p>
}

function parseAndRenderReport(content) {
  const sections = []
  let currentTitle = ''
  let currentBody = ''

  for (const line of content.split('\n')) {
    const isHeading =
      /^#{1,3}\s/.test(line) ||
      /^[A-Za-z][A-Za-z\s\d\-\/]+(:|:)\s*$/.test(line.trim()) ||
      (/^[A-Z][A-Z\s\d\-:]{4,}$/.test(line.trim()) && line.trim().length < 60)

    if (isHeading) {
      if (currentTitle && currentBody.trim()) sections.push({ title: currentTitle, body: currentBody })
      currentTitle = line.replace(/^#+\s*/, '').replace(/:$/, '').trim()
      currentBody = ''
    } else {
      currentBody += line + '\n'
    }
  }
  if (currentTitle && currentBody.trim()) sections.push({ title: currentTitle, body: currentBody })
  if (sections.length === 0) sections.push({ title: 'Incident Report', body: content })
  return sections
}

// ─── Executive Summary Panel ────────────────────────────
function ExecutiveSummary({ content, onDownload }) {
  const [raw, setRaw] = useState(false)
  if (!content) return null

  const sections = parseAndRenderReport(content)

  return (
    <div className="card animate-slide-up">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-5 h-5 text-green-400" />
          <h3 className="font-semibold text-gray-100">Incident Report</h3>
          <span className="text-xs text-green-400 bg-green-400/10 border border-green-400/20 px-2 py-0.5 rounded-full">
            {sections.length} sections
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setRaw(r => !r)}
            className="text-xs text-gray-500 hover:text-gray-300 border border-gray-700 hover:border-gray-600 px-3 py-1.5 rounded-lg transition"
          >
            {raw ? 'Formatted' : 'Raw'}
          </button>
          <button onClick={onDownload} className="btn-primary text-sm py-1.5 px-4 flex items-center gap-2">
            <Download className="w-4 h-4" />
            Download
          </button>
        </div>
      </div>

      <div className="max-h-[650px] overflow-y-auto pr-1">
        {raw ? (
          <pre className="text-xs text-gray-400 whitespace-pre-wrap font-mono leading-relaxed bg-gray-800/40 rounded-lg p-4">
            {content}
          </pre>
        ) : (
          <div>
            {sections.map((sec, i) => (
              <div key={i}>
                <SectionHeader title={sec.title} />
                {renderSection(sec.title, sec.body)}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ─── Dashboard Main ─────────────────────────────────────
export default function Dashboard({ user, onLogout }) {
  const [logFile, setLogFile] = useState(null)
  const [docFile, setDocFile] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [steps, setSteps] = useState([])
  const [summary, setSummary] = useState('')
  const [error, setError] = useState('')
  const eventSourceRef = useRef(null)

  const addStep = (type, message) => {
    const now = new Date().toLocaleTimeString()
    setSteps((prev) => [...prev, { type, message, timestamp: now }])
  }

  const handleAnalyze = async () => {
    if (!logFile) return
    setError('')
    setSteps([])
    setSummary('')
    setIsRunning(true)

    try {
      // 1. Upload log file
      addStep('status', `Uploading log file: ${logFile.name}`)
      const logForm = new FormData()
      logForm.append('file', logFile)
      const logRes = await fetch(`${API_BASE}/api/upload/logs`, { method: 'POST', body: logForm })
      if (!logRes.ok) throw new Error('Failed to upload log file')
      const logData = await logRes.json()
      addStep('status', `Log file uploaded successfully`)

      // 2. Upload docs (if provided)
      let docsPath = ''
      if (docFile) {
        addStep('status', `Uploading reference document: ${docFile.name}`)
        const docForm = new FormData()
        docForm.append('file', docFile)
        const docRes = await fetch(`${API_BASE}/api/upload/docs`, { method: 'POST', body: docForm })
        if (!docRes.ok) throw new Error('Failed to upload reference doc')
        const docData = await docRes.json()
        docsPath = docData.path
        addStep('status', `Reference document uploaded successfully`)
      }

      // 3. Start SSE analysis
      addStep('thinking', 'Starting AI agent analysis...')

      const params = new URLSearchParams({
        logs_path: logData.path,
        email: user.email,
      })
      if (docsPath) params.append('docs_path', docsPath)

      const eventSource = new EventSource(`${API_BASE}/api/analyze?${params}`)
      eventSourceRef.current = eventSource

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)

          switch (data.type) {
            case 'status':
              addStep('status', data.message)
              break
            case 'step':
              addStep('step', data.message)
              break
            case 'thinking':
              addStep('thinking', data.message)
              break
            case 'error':
              addStep('error', data.message)
              setIsRunning(false)
              eventSource.close()
              break
            case 'complete':
              addStep('complete', 'Analysis complete!')
              setSummary(data.report || data.message)
              setIsRunning(false)
              eventSource.close()
              break
            default:
              addStep('status', data.message)
          }
        } catch (e) {
          console.warn('SSE parse error:', e)
        }
      }

      eventSource.onerror = () => {
        addStep('error', 'Connection to agent lost. The analysis may still be running on the server.')
        setIsRunning(false)
        eventSource.close()
      }
    } catch (err) {
      addStep('error', err.message)
      setError(err.message)
      setIsRunning(false)
    }
  }

  const handleDownload = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/report/download`)
      if (!res.ok) throw new Error('Report not available')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'incident_report.txt'
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to download report')
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-950">
      <Navbar user={user} onLogout={onLogout} />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-1">Log Analysis Dashboard</h1>
          <p className="text-gray-500">Upload your production logs and let AI identify incidents, root causes, and remediation steps.</p>
        </div>

        {error && (
          <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm">
            <AlertTriangle className="w-4 h-4 flex-shrink-0" />
            {error}
            <button onClick={() => setError('')} className="ml-auto">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column — Upload & Controls */}
          <div className="space-y-6">
            {/* Upload Section */}
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-100 mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-brand-400" />
                Upload Files
              </h2>

              <div className="space-y-4">
                <FileUpload
                  label="Production Log File"
                  icon={FileText}
                  accept=".csv,.log,.txt,.json"
                  file={logFile}
                  onFileChange={setLogFile}
                  onClear={() => setLogFile(null)}
                  required
                  hint=".csv, .log, .txt, .json"
                />

                <FileUpload
                  label="Reference Document"
                  icon={BookOpen}
                  accept=".md,.txt,.docx,.pdf"
                  file={docFile}
                  onFileChange={setDocFile}
                  onClear={() => setDocFile(null)}
                  hint="Runbooks, SRE docs, best practices"
                />
              </div>

              <button
                onClick={handleAnalyze}
                disabled={!logFile || isRunning}
                className="btn-primary w-full mt-6 flex items-center justify-center gap-2 py-3 text-base"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Agent Analyzing...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Run Analysis
                  </>
                )}
              </button>
            </div>

            {/* Quick Stats */}
            <div className="card">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Session Info</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Agent Steps</span>
                  <span className="text-gray-300 font-mono">{steps.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Status</span>
                  <span className={`font-medium ${
                    isRunning ? 'text-brand-400' : summary ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    {isRunning ? 'Running' : summary ? 'Complete' : 'Idle'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Model</span>
                  <span className="text-gray-400 text-xs">Qwen2.5-Coder-32B</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column — Progress & Summary */}
          <div className="lg:col-span-2 space-y-6">
            <AgentProgress steps={steps} isRunning={isRunning} />
            <ExecutiveSummary content={summary} onDownload={handleDownload} />
          </div>
        </div>
      </main>
    </div>
  )
}
