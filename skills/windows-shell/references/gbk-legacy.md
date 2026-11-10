# 系统代码页仍是 936 (GBK) 时的编码规则

只在 `doctor.ps1` 显示 `ANSI codepage (ACP) 936` 时读本文件（未开启系统全局 UTF-8 的中文 Windows）。以下均为 ACP=936 环境下的实测行为与处理方式。

| 现象 | 处理 |
|---|---|
| Git Bash 里 `ipconfig`、`schtasks`、`net`、`tasklist`、`sc`、`cmd //c` 输出 `` | 改到 pwsh 里跑，或接 `\| iconv -f GBK -t UTF-8` |
| 从 bash 调 `pwsh -Command/-File`，中文输出乱码（pwsh 跟随控制台代码页 936） | 接 `\| iconv -f GBK -t UTF-8`，或 pwsh 脚本开头设 `[Console]::OutputEncoding=[Text.UTF8Encoding]::new()` |
| Python 未设 `PYTHONUTF8=1` 时 stdout 和 `open()` 默认走 GBK | 设用户环境变量 `PYTHONUTF8=1`；代码里一律显式 `encoding='utf-8'` |
| `cmd //c "chcp 65001 & ..."` 不能稳定修复 bash 管道里的乱码 | 不要用 `chcp` 绕，直接用 `iconv` 或换到 pwsh |
| `.bat`、`.cmd`、`.vbs`、`.wsf`、wscript 驱动的 `.js`、给 5.1 用的 `.ps1` 按 ANSI 读取 | 脚本只写 ASCII；要写中文就改成 pwsh 7 脚本，或存为 UTF-16 LE BOM |
| Windows PowerShell 5.1 读无 BOM 的 UTF-8 脚本 | 中文乱码并可能造成语法误判；一律改用 `pwsh` (PowerShell 7) |
| 隐藏窗口、计划任务、服务里的 pwsh 捕获子进程输出 | 先设 `[Console]::OutputEncoding=[Text.UTF8Encoding]::new()` |

根治办法：控制面板 `intl.cpl` → 管理 → 更改系统区域设置 → 勾选"Beta 版：使用 Unicode UTF-8 提供全球语言支持" → 重启系统。
