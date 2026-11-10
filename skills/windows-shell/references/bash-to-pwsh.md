# bash 习惯 → pwsh 7 对照

命令语言是 pwsh 7 时，把 bash 习惯翻成下表。超过约 3 行的逻辑直接写 Python。

| bash | pwsh 7 |
|---|---|
| `ls -la` | `Get-ChildItem -Force` |
| `find . -name '*.py'` | `Get-ChildItem -Recurse -Filter *.py -File`（或直接 `rg --files -g '*.py'`） |
| `grep -rn pat .` | `rg -n pat`（优先用 rg）；无 rg 时 `Get-ChildItem -Recurse -File \| Select-String pat` |
| `cat f` / `head -n 20 f` / `tail -n 20 f` | `Get-Content f` / `Get-Content f -TotalCount 20` / `Get-Content f -Tail 20` |
| `wc -l f` | `(Get-Content f).Count` |
| `mkdir -p a/b` | `New-Item -ItemType Directory -Force a/b` |
| `rm -rf d` | `Remove-Item -LiteralPath d -Recurse -Force` |
| `cp -r a b` / `mv a b` | `Copy-Item -LiteralPath a b -Recurse` / `Move-Item -LiteralPath a b` |
| `touch f` | `if (-not (Test-Path -LiteralPath f)) { New-Item -ItemType File f }`（勿用 `New-Item -Force`，会清空已有文件） |
| `which x` | `Get-Command x` / `where.exe x` |
| `export A=1` / `A=1 cmd` | `$env:A='1'` / `$env:A='1'; cmd; Remove-Item Env:A` |
| `echo $HOME` | `$HOME` 或 `$env:USERPROFILE` |
| `cmd1 && cmd2` / `cmd1 \|\| cmd2` | pwsh 7 原样可用 |
| `$(cmd)` | `$(cmd)` 可用；注意反引号 ` ` ` 在 pwsh 里是转义符，不是命令替换 |
| `cmd > /dev/null 2>&1` | `cmd *> $null` |
| `[ -f f ]` / `[ -d d ]` | `Test-Path -LiteralPath f -PathType Leaf` / `-PathType Container` |
| `for f in *.txt; do ...; done` | `foreach ($f in Get-ChildItem *.txt) { ... }` |
| `cat <<'EOF' > f ... EOF` | `@' ... '@ \| Set-Content -LiteralPath f`（结尾 `'@` 必须顶格） |
| `sed -i 's/a/b/' f` | `(Get-Content -Raw f) -replace 'a','b' \| Set-Content -NoNewline f`（更推荐直接用宿主编辑工具） |
| `jq '.a' f.json` | `(Get-Content -Raw f.json \| ConvertFrom-Json).a` |
| `curl -s url` | `curl.exe -s url`（7 版 `curl` 已去别名）或 `Invoke-RestMethod url` |
| `ps aux \| grep x` | `Get-Process *x*` |
| `kill PID` | `Stop-Process -Id PID` |
| `lsof -i :3000` | `Get-NetTCPConnection -LocalPort 3000 \| Select-Object OwningProcess` |
| `date +%F` | `Get-Date -Format yyyy-MM-dd` |
| `sleep 2` | `Start-Sleep 2` |
| `$?` (退出码) | 原生程序看 `$LASTEXITCODE`；`$?` 只表示上一条命令是否成功（布尔值） |
