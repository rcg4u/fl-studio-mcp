Param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$args
)

function Show-Help {
    Write-Output "gh mcp - simple GitHub CLI extension to talk to local FL Studio MCP server"
    Write-Output "Usage: gh-mcp <tool> [json|file]
"
    Write-Output "Tools: get_piano_roll_state, send_notes, delete_notes, clear_queue, clear_piano_roll"
    Write-Output "Examples:
  # Get state
  gh-mcp get_piano_roll_state

  # Send notes (read JSON from stdin)
  cat notes.json | gh-mcp send_notes

  # Delete notes from file
  gh-mcp delete_notes '{\"notes\":[{\"midi\":67,\"time\":0}]}'
"
}

if (-not $args -or $args.Count -eq 0) {
    Show-Help
    exit 0
}

$tool = $args[0]
$body = $null

if ($tool -eq 'help' -or $tool -eq '--help' -or $tool -eq '-h') {
    Show-Help
    exit 0
}

# If there's piped stdin, read it
$stdin = [Console]::In.ReadToEnd()
if ($stdin -and $stdin.Trim().Length -gt 0) {
    $body = $stdin
} elseif ($args.Count -gt 1) {
    # Second argument may be a JSON string or file path
    $candidate = $args[1]
    if (Test-Path $candidate) {
        $body = Get-Content -Raw -Path $candidate
    } else {
        $body = $candidate
    }
} else {
    $body = '{}'
}

$uri = "http://127.0.0.1:8765/tool/$tool"

try {
    $resp = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType 'application/json' -ErrorAction Stop
    # The MCP fallback returns { result: ... }
    if ($resp -is [System.Collections.IDictionary] -and $resp.ContainsKey('result')) {
        $out = $resp['result']
        if ($out -is [string]) { Write-Output $out } else { $out | ConvertTo-Json -Depth 10 }
    } else {
        $resp | ConvertTo-Json -Depth 10
    }
} catch {
    Write-Error "Request to $uri failed: $($_.Exception.Message)"
    exit 1
}
