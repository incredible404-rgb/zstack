---
name: windows-shell
description: 'Windows 跑命令避坑：按宿主壳选 bash 或 pwsh、中文乱码（含旧 GBK）、Git Bash 改写路径参数、CRLF、pwsh 引号/退出码/表格截断。在 Windows 上执行 shell 命令或写 .ps1/.sh/.bat 时先读；遇到乱码（锟斤拷、涓枃）、表格截断、"is not recognized"、"找不到与参数名称匹配的参数"、参数变成 C:/Program Files/Git/...、git diff 整文件变、同一命令第二次失败时必须先读再重试。'
---

# Windows Shell 避坑

现代 Windows 11 推荐基线：开启系统"Beta: 使用 Unicode UTF-8 提供全球语言支持"（ANSI/OEM 代码页均为 **65001 (UTF-8)**），设置 `PYTHONUTF8=1`，安装 PowerShell 7（`pwsh`，7.3+ `PSNativeCommandArgumentPassing=Windows`）与 Git Bash（MSYS2）。

环境不确定时先跑：`pwsh -NoProfile -File <本技能目录>/scripts/doctor.ps1`，它会只读列出当前机器实际的代码页、编码环境变量、Git 换行配置与常用工具路径。**若显示 ACP=936**（未开系统 UTF-8 的中文 Windows），按 `references/gbk-legacy.md` 处理编码。

## 1. 先认宿主壳

命令一律按宿主工具**实际执行的壳**写，不按工具名猜（有的客户端工具名叫 `bash`，底层可能配成了 `pwsh`）。不确定时先跑 `echo $PSVersionTable`：有输出是 `pwsh`，空的是 `bash`。

| 客户端常见配置 | 宿主壳 | 怎么写 |
|---|---|---|
| Claude Code、pi（配 Git Bash 时） | Git Bash | 日常命令（git、rg、文本处理、构建）用 bash。注册表、服务、计划任务、进程/CIM、ACL 等 Windows 系统操作写成 `.ps1`，用 `pwsh -NoProfile -File ./job.ps1` 执行 |
| Codex（Windows 原生固定 PowerShell） | PowerShell 7 | 按 pwsh 7 写，bash 习惯对照见 `references/bash-to-pwsh.md`。POSIX 脚本写成 `.sh`，用 `& 'C:\Program Files\Git\bin\bash.exe' ./job.sh` 执行 |
| 其他客户端 | 未定 | 先跑 `echo $PSVersionTable` 探测再写 |

超过约 3 行的逻辑、解析 JSON/CSV、批量改文件直接写 Python 脚本。禁用旧版 `powershell.exe`（5.1）。一条命令要穿过两层壳时见 §2 铁律 1。

## 2. 五条铁律

1. **跨 shell 不内联**。命令要穿过两层 shell（bash 里 `pwsh -Command`、pwsh 里 `bash -c`、任何 `cmd /c`），又含 `$`、引号、管道或中文时，写成脚本文件再用 `-File` / `bash file.sh` 跑。
2. **同一条命令失败两次就换路子**：改成脚本文件，或改用 Python。不要第三次微调转义，也不要硬套另一种壳的语法。
3. **要读结果就要结构化输出**。pwsh 用 `ConvertTo-Json -Depth 5 -Compress`、`Format-List` 或 `Out-String -Width 4096`，不读默认表格；bash 用 `--format`/`--porcelain`/`-z` 这类机器格式。
4. **改文件用宿主编辑工具**（Edit / Write / apply_patch），不用 `sed -i`、`Set-Content` 或临时内联 Python 重写整个文件——它们会悄悄把 LF 改成 CRLF 或吞反斜杠转义（见 §4、§5）。若必须用 Python 写文本文件，显式传 `encoding='utf-8', newline=''`（或 `newline='\n'`），路径用原始字符串 `r'...'` 或正斜杠。
5. **路径统一写成 `C:/Users/<you>/...`**（正斜杠 + 盘符）。pwsh、bash、Python、Node、git 都认，既不会被 MSYS 误改写，也不用转义反斜杠。只有交给 `cmd.exe` 内建命令时才改回反斜杠。

## 3. pwsh 7 的坑（均已实测）

| 写法 | 实际结果 | 正确写法 |
|---|---|---|
| `ls -la`、`rm -rf x`、`export A=1`、`A=1 cmd`、`[ -f x ]`、`2>/dev/null` | 参数错误或语法错误 | `Get-ChildItem -Force`、`Remove-Item -Recurse -Force -LiteralPath x`、`$env:A='1'`、`Test-Path x`、`2>$null` |
| `where python` | `where` 是 `Where-Object` 的别名，没有输出 | `where.exe python` 或 `Get-Command python` |
| 读默认表格输出 | 默认宽度有限，**放不下的列整列截断消失**且不报错 | `Format-List`、`ConvertTo-Json`，或 `\| Out-String -Width 4096` |
| `Test-Path 'a[1].txt'` | 返回 False：`[]` 被当成通配符 | 凡是路径参数都用 `-LiteralPath` |
| `$ErrorActionPreference='Stop'` 之后调 `git` 等原生程序 | 原生程序返回非 0 **不抛异常**，脚本照常往下跑 | 关键原生调用后检查 `if ($LASTEXITCODE) { throw "git failed: $LASTEXITCODE" }` |
| 最后一条原生命令返回非 0 | 宿主会把整次调用判为失败（哪怕前面都成功） | 预期可能返回非 0 的探测命令不要放最后，或显式 `exit 0` |
| `git x 2>&1` 赋给变量 | stderr 行变成 `ErrorRecord` 对象 | `git x 2>&1 \| ForEach-Object { "$_" }` |
| 给 `.cmd/.bat` 包装器（npm、npx、pnpm、yarn、code 等）传含 `& \| < > ^ %` 的参数 | `cmd.exe` 会二次解析，`'a&b'` 会把 `b` 当成命令执行；`--%` 也救不了 | 改为直接调用底层 `node <cli.js>` 或 `.exe`；或把值写进文件再传路径 |
| 给普通 `.exe` 传 JSON、带引号的参数或空串 | pwsh 7.3+ 已经原生传对，**不需要**再手工双重转义 | `node -e '...' '{"a":"b c"}'` 原样写 |
| `Get-Content` 读旧的 GBK 文件 | 乱码（7+ 默认按 UTF-8 读） | `Get-Content x -Encoding 936` |
| `Set-Content`、`Out-File`、`>` | 写出 UTF-8（无 BOM）+ **CRLF** | 需要固定 LF 时用 `[IO.File]::WriteAllText($p, $text)`，`$text` 里用 `` "`n" `` 换行 |
| here-string `@' ... '@` | 结尾的 `'@` 前面有缩进就会报解析错误 | 结尾的 `'@` 必须顶格写在第 1 列 |
| 在 pwsh 里写 `pwsh -Command "... $x ..."` | 外层 shell 先把 `$x` 展开了 | 直接写命令体，或写成 `.ps1` 再用 `-File` 运行 |
| 双引号字符串里有中文弯引号 `“”` | PowerShell 会把弯引号当成字符串定界符，报 ParserError | 含中文弯引号的文本用 ASCII 单引号或单引号 here-string |
| 自定义函数名与内置别名同名（`h`、`r`、`cat`、`ls` 等） | 内置别名优先于函数，调用落到 `Get-History` 之类 | 函数名用 `Verb-Noun` 全名，如 `Invoke-Probe` |
| `foreach` 或管道产出的数组被逗号运算符包成多维 | 外层单元素数组易被管道展平 | 每行输出 `[pscustomobject]@{...}`，再 `@( ... ) \| ConvertTo-Json` |

## 4. Git Bash 的坑（均已实测）

| 写法 | 实际结果 | 正确写法 |
|---|---|---|
| `schtasks /query`、`node x.js /api/v1`、`--opt=/tmp/x` | MSYS 把形似 POSIX 路径的参数改写成 `C:/Program Files/Git/query` 之类 | `MSYS_NO_PATHCONV=1 schtasks /query`，或写成双斜杠 `schtasks //query //fo csv` |
| Windows 原生工具（`ipconfig`、`schtasks`、`cmd //c`）中文输出 | 开启系统 UTF-8 后正常；ACP=936 机器会出 `` | 乱码时先跑 `scripts/doctor.ps1` 看 ACP，936 见 `references/gbk-legacy.md` |
| `sed -i 's/a/b/' f` | **把整个文件的 CRLF 悄悄改成 LF**，`git diff` 整文件变红 | 用编辑工具；必须用命令时写 `sed -b -i` 或 `perl -pi -e` |
| `grep -c $'\r' f` | MSYS 下对 CRLF 文件也可能返回 0（`\r` 被剥掉） | 检查换行符用 `grep -U` 或 `python -c "print(repr(open('f','rb').read()[:80]))"` |
| `cygpath` | 路径互转可用 | `cygpath -w /c/x` → `C:\x`；`cygpath -u 'C:\x'` → `/c/x` |
| `jq` 未安装时 | 报 `command not found` | 用 `python -c "import json,sys; ..."` 或 pwsh `ConvertFrom-Json` |
| `python3 - <<EOF` 或 `python3 x.py` | 易命中 `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe` 商店垫片，非交互下挂死 | Windows 上统一写 `python` 或 `py -3` |
| 写进配置文件的 `/c/Users/...` | 原生 Windows 程序不认 MSYS 挂载路径 | 写成 `C:/Users/...` |

## 5. 编码规则

- 新写的文件一律 UTF-8 无 BOM。系统开启 UTF-8 后，`.bat`、`.cmd`、`.ps1` 均可直接写中文。
- **Python**：即使设了 `PYTHONUTF8=1`，跨机器脚本仍应显式写 `encoding='utf-8'`。`Path.write_text()` 默认把 `\n` 转成系统换行（Windows 下为 CRLF），需要保持原换行时传 `newline=''` 或 `newline='\n'`。普通字符串里的 Windows 反斜杠路径会被转义吃掉（如 `'_admin\tools'` 里的 `\t` 变成制表符），路径一律写 `r'...'` 或正斜杠。
- **旧 GBK 文件**：UTF-8 环境下默认读会乱码。读取时显式指定编码：pwsh `Get-Content x -Encoding 936`、Python `encoding='gb18030'`、bash `iconv -f GBK -t UTF-8 x`。除非用户要求，不要把原文件转码覆盖。
- **个别老程序仍输出 GBK**：pwsh 里临时设 `[Console]::OutputEncoding=[Text.Encoding]::GetEncoding(936)`，读完还原；bash 里接 `| iconv -f GBK -t UTF-8`。
- **看到乱码先判断哪一层错**：先看原始字节（`Format-Hex` 或 `od -An -tx1`）。`e4 b8 ad` 是 UTF-8 的「中」，`d6 d0` 是 GBK 的「中」。文件本身字节正确、只是终端解码错，就不要改文件。

## 6. 卡住时

1. 跑 `scripts/doctor.ps1` 看实际环境，不凭印象猜。
2. 对照 §3 / §4 的表定位属于哪一类坑。
3. 两次失败后按铁律 2 换脚本文件或 Python，并在回复里一句话说明换了什么。
