# Installing `videocaptioner` — step by step

This is Phase 0 of the tutorial (see `../PLAN.md` § 3): "toolchain installed,
translator configured" is the exit criterion. Windows 11 is the primary,
fully-detailed path — it's what this tutorial was piloted on. macOS and Linux
are covered as secondary paths; the tool itself is cross-platform, only the
install mechanics differ.

**Upstream project:** [WEIFENG2333/VideoCaptioner](https://github.com/WEIFENG2333/VideoCaptioner)
(GPL-3.0). This tutorial uses its CLI entry point, `videocaptioner`, installed
via `pip`.

**Verified against:** `videocaptioner` 1.4.2, Python 3.12.1, Windows 11.

---

## Prerequisites (all platforms)

| Requirement | Why |
|---|---|
| Python **>= 3.10, < 3.13** | Pinned by the package itself. Python 3.13 is **not yet supported** — check your version before installing. |
| FFmpeg (`ffmpeg` + `ffprobe` on PATH) | Required for transcription audio extraction, synthesis (burning captions in), and every verification gate in this tutorial (Gate T4). Not bundled with the pip package — install separately. |
| An LLM API key (for translation) | This tutorial pins `--translator llm` and forbids silent fallback to Bing/Google (see `PLAN.md` § 4, Gate T2). Any OpenAI-compatible provider works (the pilot run used DeepSeek); bring your own key. |

---

## Windows 11 — step by step

### 1. Check for an existing Python install

```powershell
python --version
```

If this prints `Python 3.10.x` through `3.12.x`, skip to step 2. If it prints
`3.13+`, prints nothing, or errors "not recognized":

**Install Python 3.12** (recommended target version):
1. Download the Windows installer from <https://www.python.org/downloads/> —
   pick a **3.12.x** release, not the latest 3.13+.
2. Run the installer. **Check "Add python.exe to PATH"** on the first screen —
   this is the single most common install failure if skipped.
3. Open a **new** PowerShell window (PATH changes don't apply to already-open
   windows) and re-run `python --version` to confirm.

### 2. Install FFmpeg

FFmpeg is not on Windows by default and is not installed by `pip`. Two options:

**Option A — winget (recommended, fewer manual PATH edits):**
```powershell
winget install --id Gyan.FFmpeg -e
```
Open a **new** PowerShell window afterward, then verify:
```powershell
ffmpeg -version
ffprobe -version
```

**Option B — manual download:**
1. Download a build from <https://www.gyan.dev/ffmpeg/builds/> (the
   "full_build" zip is fine).
2. Extract it somewhere permanent, e.g. `C:\ffmpeg`.
3. Add `C:\ffmpeg\bin` to your PATH: Windows Settings → search "environment
   variables" → "Edit the system environment variables" → Environment
   Variables → under **User variables**, select `Path` → Edit → New →
   paste `C:\ffmpeg\bin`.
4. Open a **new** PowerShell window and verify as in Option A.

### 3. Install `videocaptioner`

```powershell
pip install videocaptioner
```

This pulls in several dependencies including a Qt GUI toolkit (`pyqt5`) even
though this tutorial only uses the CLI — that's how the upstream package is
packaged; there is no CLI-only extra as of 1.4.2.

Verify the CLI is on PATH and check the version:
```powershell
videocaptioner --version
```
If PowerShell reports `videocaptioner: command not found` despite `pip`
reporting a successful install, the Python Scripts directory isn't on PATH.
Find it with:
```powershell
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```
and add that path the same way you added FFmpeg's `bin` directory in step 2.

### 4. Run the built-in doctor

```powershell
videocaptioner doctor
```
This checks Python, `ffmpeg`, `ffprobe`, `yt-dlp`, the config file location,
and your ASR/translation/dubbing settings in one shot. Example healthy output:
```
OK    python: Python 3.12.1
OK    ffmpeg: C:\...\ffmpeg.EXE (ffmpeg version ...)
OK    ffprobe: C:\...\ffprobe.EXE (ffprobe version ...)
OK    config.file: C:\Users\<you>\AppData\Local\videocaptioner\videocaptioner\config.toml
```
A `WARN` on `dubbing.api_key` is expected and harmless if you aren't using
`videocaptioner dub` (out of scope for this tutorial — see `PLAN.md` § 1).

### 5. Configure the LLM translator

Set your provider's credentials (dotted-key config, one value per call):
```powershell
videocaptioner config set llm.api_key "sk-..."
videocaptioner config set llm.api_base "https://api.deepseek.com"
videocaptioner config set llm.model "deepseek-chat"
```
Substitute any OpenAI-compatible provider's `api_base`/`model` — the pilot
run for this tutorial used DeepSeek, but the tool is not tied to one vendor.

Confirm what's actually configured before you trust it:
```powershell
videocaptioner config show
```
Look for the `llm:` block showing your `api_base`/`model`, and (once you run
a real translate command with `--translator llm`) the `translate:` block
showing `service = llm` — **this is Gate T2 from `PLAN.md`**: never assume
the translator you asked for is the one that ran.

### 6. The PowerShell JSON-quoting gotcha (read this before using `--style-override`)

If you later use `videocaptioner synthesize ... --style-override '{"font_size":56}'`
to tweak caption styling, **PowerShell will silently strip the double quotes**
before the argument reaches the `.exe` — this is standard Windows CRT argv
parsing (an unescaped `"` toggles quote mode and is dropped; doubling `""`
does **not** fix it). You'll see:
```
✗ Error: Invalid --style-override JSON: Expecting property name enclosed in double quotes
```
even though the command looks correct on screen. **Fix:** backslash-escape
every `"` inside a single-quoted PowerShell string:
```powershell
--style-override '{\"font_size\":56}'
```
Verify the fix works in isolation before debugging anything else:
```powershell
python -c "import sys; print(sys.argv)" '{\"font_size\":56}'
# should print: ['{"font_size":56}']
```
This cost real debugging time piloting this tutorial — it's listed again in
the troubleshooting section of the full manual, but it belongs here too,
because it strikes during install verification just as often as mid-project.

---

## macOS

```bash
# Python (Homebrew ships a recent 3.x; confirm it's < 3.13)
brew install python@3.12
python3.12 --version

# FFmpeg
brew install ffmpeg
ffmpeg -version

# videocaptioner
python3.12 -m pip install videocaptioner
videocaptioner --version
videocaptioner doctor
```
If `videocaptioner` isn't found after install, it's in your user site-packages
`bin`/`Scripts` directory — check with
`python3.12 -m site --user-base` and add `<that path>/bin` to your shell's
`PATH` (`~/.zshrc` or `~/.bash_profile`).

Configure the translator the same way as Windows (step 5 above) — the
`config set`/`config show` commands are identical across platforms.

---

## Linux

```bash
# Python — most distros ship a recent 3.x; check first
python3 --version   # need 3.10-3.12

# Debian/Ubuntu
sudo apt install python3-pip ffmpeg

# Fedora
sudo dnf install python3-pip ffmpeg

# videocaptioner (use --user or a venv to avoid system-package conflicts)
python3 -m pip install --user videocaptioner
videocaptioner --version
videocaptioner doctor
```
If your distro's default Python is 3.13+, install 3.12 via `pyenv` or your
distro's alternate-version package (e.g. `deadsnakes` PPA on Ubuntu) rather
than fighting the system interpreter.

Configuration commands are identical to Windows/macOS (step 5 above).

---

## Verify before you go further

Same spirit as tutorial #2's own pre-flight check — don't start Phase 1 until
all of these are clean:

```powershell
videocaptioner --version
videocaptioner doctor
videocaptioner config show
```

You're ready for Phase 1 when:
1. `doctor` shows `OK` on `python`, `ffmpeg`, `ffprobe`
2. `config show` shows your intended `llm.api_base`/`model` under the `llm:` block
3. No PATH errors on any of the three commands above, from a **freshly opened** terminal

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `python: command not found` after install | PATH not updated, or old terminal window | Reopen terminal; re-check "Add to PATH" was ticked during install |
| `videocaptioner: command not found`, `pip install` reported success | Python Scripts/bin dir not on PATH | See Windows step 3 / macOS·Linux notes above for how to find and add it |
| `doctor` shows FFmpeg missing despite installing it | Installed to a path not on PATH, or terminal not reopened | Reopen terminal; run `ffmpeg -version` directly to isolate PATH vs install problem |
| Translation runs but silently used a different translator than requested | Didn't check provenance | Always run `videocaptioner config show` after translating — see Gate T2, `PLAN.md` § 4 |
| `--style-override` JSON errors even though it "looks right" | PowerShell stripped the quotes | Backslash-escape every `"` — see step 6 above |
| `pip install videocaptioner` fails to build a dependency | Python version outside `>=3.10,<3.13` | Install a supported Python version (step 1); do not fight a 3.13 interpreter |
