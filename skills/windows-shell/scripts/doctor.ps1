# windows-shell doctor: print the facts an agent needs before fighting the shell.
# Read-only. ASCII-only on purpose so any host can parse it.
# Usage: pwsh -NoProfile -File doctor.ps1   (from Git Bash: append | iconv -f GBK -t UTF-8 if output looks garbled)

$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()

function Row($k, $v) { '{0,-22} {1}' -f $k, $v }

'== shell'
Row 'pwsh' $PSVersionTable.PSVersion
Row 'edition' $PSVersionTable.PSEdition
if ($PSVersionTable.PSVersion.Major -lt 7) { Row 'WARNING' 'running under Windows PowerShell 5.1 - use pwsh 7' }
Row 'NativeArgPassing' $PSNativeCommandArgumentPassing
$bash = 'C:\Program Files\Git\bin\bash.exe'
Row 'git-bash' $(if (Test-Path $bash) { $bash } else { 'NOT FOUND' })
Row 'parent process' (Get-Process -Id (Get-CimInstance Win32_Process -Filter "ProcessId=$PID").ParentProcessId).Name

'== encoding'
$cp = Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage'
Row 'ANSI codepage (ACP)' $cp.ACP
Row 'OEM codepage' $cp.OEMCP
Row 'console out' ([Console]::OutputEncoding.WebName + ' (forced by doctor)')
Row 'PYTHONUTF8 (process)' $(if ($env:PYTHONUTF8) { $env:PYTHONUTF8 } else { '<unset>' })
Row 'PYTHONUTF8 (user)' $(if ($u = [Environment]::GetEnvironmentVariable('PYTHONUTF8','User')) { $u } else { '<unset>' })
Row 'PYTHONIOENCODING' $(if ($env:PYTHONIOENCODING) { $env:PYTHONIOENCODING } else { '<unset>' })
if ($cp.ACP -ne '65001') { Row 'NOTE' "ACP is not UTF-8: native tools emit ANSI ($($cp.ACP)); read references/gbk-legacy.md" }

'== git'
Row 'version' ((git --version) -replace 'git version ','')
Row 'core.autocrlf' $(if ($a = git config --show-origin --get core.autocrlf) { $o, $v = $a -split "`t"; "$v  ($o)" } else { '<unset>' })
Row 'core.quotepath' $(if ($q = git config --get core.quotepath) { $q } else { '<unset> (Chinese filenames shown as \ooo escapes)' })

'== tools'
foreach ($t in 'python','node','rg','jq','uv','gh','iconv') {
    $c = Get-Command $t -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    Row $t $(if ($c) { $c.Source } else { 'not on PATH' })
}
if (-not (Get-Command iconv -ErrorAction SilentlyContinue)) { Row 'iconv (git bash)' $(if (Test-Path 'C:\Program Files\Git\usr\bin\iconv.exe') { 'available inside Git Bash' } else { 'missing' }) }

'== system'
Row 'LongPathsEnabled' (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem').LongPathsEnabled
Row 'DeveloperMode' (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock').AllowDevelopmentWithoutDevLicense
Row 'ExecutionPolicy' (Get-ExecutionPolicy)
exit 0
