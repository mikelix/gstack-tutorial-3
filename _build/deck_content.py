# -*- coding: utf-8 -*-
"""Slide content for gstack Tutorial No.3, both languages in one structure.

Tutorial #2 kept build_en.py and build_zh.py as two ~26KB files that "must
stay slide-for-slide identical" (PLAYBOOK.md section 3.1) — parity maintained
by hand, which is a standing drift risk. Here the deck is declared ONCE and
each string is a (en, zh) pair, so the two editions cannot diverge in
structure: they are generated from the same list.

Every content slide's title is an ACTION TITLE — a sentence carrying the
takeaway, not a topic label. Read the titles alone and you get the argument.
"""

# Each entry: (kind, payload). T(en, zh) marks a localized value.
#
# T returns a distinct type rather than a bare tuple on purpose: a bare
# 2-tuple is ambiguous once values nest (a T() holding two tuples looks
# exactly like a tuple holding two T()s), which silently resolved to the
# wrong strings. An explicit class removes the guesswork.
class L(tuple):
    __slots__ = ()

    def __new__(cls, en, zh):
        return super().__new__(cls, (en, zh))


T = L


def pick(v, lang):
    """Resolve L(en, zh) markers anywhere inside a nested structure."""
    i = 0 if lang == "en" else 1
    if isinstance(v, L):
        return pick(v[i], lang)
    if isinstance(v, dict):
        return {k: pick(x, lang) for k, x in v.items()}
    if isinstance(v, list):
        return [pick(x, lang) for x in v]
    if isinstance(v, tuple):
        return tuple(pick(x, lang) for x in v)
    return v


SLIDES = [
    # ------------------------------------------------------------ cover
    ("cover", dict(
        kicker=T("gstack Tutorial No. 3", "gstack 教程 第三部"),
        title=T("English → Chinese Video Captioning, Verified",
                "英译中视频字幕：可验证的工作流"),
        subtitle=T("Build a caption pipeline with videocaptioner — and prove the "
                   "output is right with a five-gate verification chain",
                   "用 videocaptioner 搭建字幕流水线 —— 并用五道关卡验证链证明输出正确"),
        meta=[T("gstack orchestration + one domain reviewer",
                "gstack 流程编排 + 一位领域审阅者"),
              T("Prof. Yi-Kuen Lee  ·  September 2026",
                "李奕锟 教授  ·  2026 年 9 月"),
              T("Prose CC BY 4.0 · Code Apache-2.0",
                "文字 CC BY 4.0 · 代码 Apache-2.0")],
    )),

    # ------------------------------------------------------------ exec summary
    ("bullets", dict(
        kicker=T("Executive summary", "执行摘要"),
        title=T("A working pipeline is easy; proving it worked is the actual skill",
                "搭出流水线不难，证明它确实成功才是真本事"),
        lead=T("The governing thought of this tutorial, in one line.",
               "本教程的核心论点，一句话说清。"),
        bullets=[
            T(("Four commands.", "Transcribe, translate, synthesize, verify. The "
               "mechanics take an afternoon to learn."),
              ("四条命令。", "转写、翻译、合成、验证。机械操作一个下午就能学会。")),
            T(("Every stage fails quietly.", "ASR mishears. Translators return your "
               "source text and call it a translation. Captions render off-frame."),
              ("每个阶段都会静默失败。", "ASR 会听错；翻译器会把原文当译文返回；字幕会渲染到画面外。")),
            T(("We hit this for real.", "A free translator returned untranslated "
               "English, exited 0, and defeated four of our five gates."),
              ("我们真的踩到了。", "一个免费翻译器返回了未翻译的英文、退出码为 0，并骗过了五道关卡中的四道。")),
            T(("So the subject is verification.", "Gates that check output rather "
               "than exit codes, and one gate we deliberately do not automate."),
              ("所以本教程的主题是验证。", "检查输出而非退出码的关卡，以及一道我们刻意不自动化的关卡。")),
        ],
        source=T("Source: reviews/04-qa-report.md, Finding 1 — reproduced 2026-09-15",
                 "来源：reviews/04-qa-report.md 发现 1 —— 2026-09-15 复现"),
    )),

    ("bignum", dict(
        kicker=T("What you get", "交付成果"),
        title=T("One sitting takes a raw clip to a captioned output you can defend",
                "一次专注投入，就能把原始片段变成经得起追问的成品"),
        stats=[
            (T("5", "5"), T("verification gates", "道验证关卡"),
             T("Four mechanical, one human — the split is deliberate",
               "四道机械执行，一道人工 —— 这个划分是刻意的")),
            (T("2-4h", "2-4 小时"), T("first run, no surprises", "首次运行，顺利情况"),
             T("2.5-7h honestly, once the top risk is priced in",
               "老实说是 2.5-7 小时，把首要风险计入之后")),
            (T("63", "63"), T("automated repo checks", "项自动化仓库检查"),
             T("Links, EN/ZH parity, gate contract, BOM safety",
               "链接、中英对照、关卡契约、BOM 安全")),
        ],
        note=T("The honest range is wider than the headline number because the "
               "single most likely failure lands mid-project, not during install.",
               "老实的区间比标题数字更宽，因为最可能发生的故障出现在项目中途，而不是安装阶段。"),
    )),

    # ------------------------------------------------------------ section 1
    ("divider", dict(
        num="01",
        title=T("Why verification is the subject", "为什么「验证」才是主题"),
        blurb=T("Three ways this pipeline lies to you, and the one that cost us a day",
                "这条流水线骗你的三种方式，以及让我们损失一天的那一种"),
    )),

    ("table", dict(
        kicker=T("Failure modes", "失效模式"),
        title=T("Each stage can report success while producing the wrong artifact",
                "每个阶段都可能一边报告成功，一边产出错误结果"),
        headers=[T("Stage", "阶段"), T("How it fails quietly", "它如何静默失败"),
                 T("What catches it", "由谁抓住")],
        widths=[2, 5.5, 3],
        rows=[
            [T("Transcribe", "转写"),
             T("ASR mishears a word and writes something plausible",
               "ASR 听错一个词，写出看似合理的内容"),
             T("A human reading the transcript", "人工通读转写稿")],
            [T("Translate", "翻译"),
             T("Service rate-limits, swallows the error, returns your ENGLISH as the translation",
               "服务触发限流、吞掉错误，把你的英文原文当作译文返回"),
             T("Gate T3b", "Gate T3b")],
            [T("Translate", "翻译"),
             T("A different translator runs than the one you asked for",
               "实际运行的翻译服务并非你指定的那个"),
             T("Gate T2", "Gate T2")],
            [T("Synthesize", "合成"),
             T("Captions render off-frame or overlap text burned into the source",
               "字幕渲染到画面外，或与源视频已烧录的文字重叠"),
             T("Gate T4 + your eyes", "Gate T4 + 你的眼睛")],
        ],
        emphasis_col=0,
    )),

    ("quote", dict(
        kicker=T("The one rule", "唯一的铁律"),
        quote=T("\"✓ Done\" is a string.\nThe output file is the evidence.",
                "「✓ Done」只是一个字符串。\n输出文件本身才是证据。"),
        attrib=T("The same lesson as gstack Tutorial #2's \"'PASS' is a string, the "
                 "log is the evidence\" — different domain, identical discipline",
                 "与 gstack 教程 #2 的「'PASS' 只是字符串，日志才是证据」同一条教训 —— 领域不同，纪律相同"),
    )),

    ("code", dict(
        kicker=T("The incident", "真实事故"),
        title=T("A free translator returned our English text and reported success",
                "一个免费翻译器返回了我们的英文原文，还报告成功"),
        lines=[
            "$ videocaptioner subtitle probe.srt --translator google \\",
            "      --target-language zh-Hans --layout target-only -o out.srt",
            "",
            "ERROR - Google translation failed (x2): 429 Too Many Requests",
            "OK Done -> out.srt (2 segments)   exit code: 0",
            "",
            "$ cat out.srt        # both lines still English:",
            "hello this is a short test",
            "of the translation pipeline",
        ],
        note=T("Logged, swallowed, exit 0, correct count, well-formed file — the only "
               "thing wrong was zero Chinese.",
               "错误被记录后吞掉，退出码 0，分段数正确，文件格式良好 —— 唯一的问题是零中文。"),
        source=T("Observed 2026-09-15, videocaptioner 1.4.2, Windows 11, Hong Kong network",
                 "观测于 2026-09-15，videocaptioner 1.4.2，Windows 11，香港网络"),
    )),

    ("table", dict(
        kicker=T("Why it mattered", "为何严重"),
        title=T("Four of our five gates passed on that file — the chain verified everything except translation",
                "那个文件通过了五道关卡中的四道 —— 验证链检查了一切，唯独没检查「翻译是否发生」"),
        headers=[T("Gate", "关卡"), T("Verdict", "结论"), T("Why it missed", "为何漏掉")],
        widths=[3.5, 1.6, 6.5],
        rows=[
            [T("T1 transcription", "T1 转写完整性"), T("PASS", "通过"),
             T("The source .srt was genuinely fine", "源 .srt 文件确实没问题")],
            [T("T2 translator provenance", "T2 翻译服务溯源"), T("PASS", "通过"),
             T("The service really was google — as requested", "实际运行的确实是 google —— 正如指定")],
            [T("T3 segment parity", "T3 分段一致性"), T("PASS", "通过"),
             T("2 segments in, 2 segments out", "输入 2 段，输出 2 段")],
            [T("T4 synthesis fidelity", "T4 合成保真度"), T("PASS", "通过"),
             T("Video structurally perfect, just with English on it", "视频结构完美，只是画面上是英文")],
            [T("T3b — did NOT exist yet", "T3b —— 当时尚不存在"), T("FAIL", "失败"),
             T("Added because of this incident. Now the only gate that catches it.",
               "因这次事故而新增。现在它是唯一能抓到此问题的关卡。")],
        ],
        emphasis_col=0,
        source=T("Source: reviews/04-qa-report.md Finding 1", "来源：reviews/04-qa-report.md 发现 1"),
    )),

    # ------------------------------------------------------------ section 2
    ("divider", dict(
        num="02",
        title=T("The pipeline and its gates", "流水线及其关卡"),
        blurb=T("Four commands, one human read-through, five gates",
                "四条命令、一次人工通读、五道关卡"),
    )),

    ("flow", dict(
        kicker=T("Pipeline", "流水线"),
        title=T("Four stages, with a mandatory human read between transcription and translation",
                "四个阶段，其中转写与翻译之间必须插入一次人工通读"),
        steps=[
            (T("1  Transcribe", "1  转写"),
             T("ASR to English .srt. Free bijian engine, no setup.",
               "ASR 生成英文 .srt。免费 bijian 引擎，无需配置。")),
            (T("2  Correct", "2  校正"),
             T("You read it. Fix ASR errors here or translate them later.",
               "你亲自通读。ASR 错误在这里改，否则会被翻译下去。")),
            (T("3  Translate", "3  翻译"),
             T("Chinese-only output. Translator chosen for YOUR access.",
               "仅输出中文。翻译服务按你自己的访问条件选择。")),
            (T("4  Synthesize", "4  合成"),
             T("Burn captions in. Style and position controlled.",
               "烧录字幕。样式与位置可控。")),
        ],
        note=T("Stage 2 is the step everyone skips. Our pilot caught three real ASR "
               "errors there — two minutes to fix in English, a translation-quality "
               "problem if allowed through.",
               "阶段 2 是所有人都想跳过的一步。我们的试点在这里抓到三处真实 ASR 错误 —— 在英文阶段改只要两分钟，放过去就变成翻译质量问题。"),
    )),

    ("table", dict(
        kicker=T("The gate chain", "关卡链"),
        title=T("Four gates run as code; the fifth needs a bilingual human and we say so",
                "四道关卡以代码运行；第五道需要双语人工，我们对此直言不讳"),
        headers=[T("Gate", "关卡"), T("Checks", "检查什么"), T("Mechanical?", "可机械执行？")],
        widths=[1.6, 7.4, 2],
        rows=[
            [T("T1", "T1"), T("Transcription produced segments", "转写确实产出了分段"), T("Yes", "是")],
            [T("T2", "T2"), T("The translator that ran is the one you asked for", "实际运行的翻译服务就是你指定的那个"), T("Yes", "是")],
            [T("T3", "T3"), T("No segments dropped or merged", "没有分段被丢弃或合并"), T("Yes", "是")],
            [T("T3b", "T3b"), T("Translation actually happened — not English passthrough", "翻译确实发生了 —— 而非英文透传"), T("Yes", "是")],
            [T("T4", "T4"), T("Output matches source resolution and duration exactly", "输出与源文件分辨率、时长完全一致"), T("Yes", "是")],
            [T("T5", "T5"), T("The Chinese is faithful and natural", "中文忠实且地道"), T("No — human", "否 —— 人工")],
        ],
        emphasis_col=0,
    )),

    ("two_col", dict(
        kicker=T("The circularity trap", "循环论证陷阱"),
        title=T("Never verify an artifact against something derived from itself",
                "绝不用源自产物自身的东西去验证该产物"),
        left=(T("Tempting, and worthless", "诱人，且毫无价值"),
              [T("OCR the burned-in captions from the finished video",
                 "用 OCR 识别成片中烧录的字幕"),
               T("Diff that text against the .srt you used to make it",
                 "把识别结果与你用来生成它的 .srt 比对"),
               T("It will match. It proves synthesis didn't corrupt the text.",
                 "它会吻合。这只能证明合成没有损坏文本。"),
               T("It says NOTHING about whether the Chinese is a correct translation.",
                 "它完全无法说明中文是否是正确的翻译。")],
              "BAD"),
        right=(T("What the script does instead", "脚本的实际做法"),
               [T("Pass --ocr-check and run_gates.py exits 2 — VOID",
                  "传入 --ocr-check，run_gates.py 以 2 退出 —— VOID"),
                T("Not 0 (pass), not 1 (fail). A third, distinct state.",
                  "不是 0（通过），也不是 1（失败）。而是第三种、独立的状态。"),
                T("VOID = the check ran but proved nothing",
                  "VOID = 检查跑了，但什么也没证明"),
                T("Compare English .srt to Chinese .srt directly. Never the video.",
                  "直接比对英文 .srt 与中文 .srt。绝不比对视频。")],
               "GOOD"),
        source=T("Same lesson as Tutorial #2's LVS circularity trap, transplanted",
                 "与教程 #2 的 LVS 循环论证陷阱是同一条教训的移植"),
    )),

    # ------------------------------------------------------------ section 3
    ("divider", dict(
        num="03",
        title=T("Setup, and the choice we got wrong first",
                "环境搭建，以及我们最初做错的那个选择"),
        blurb=T("Install is easy. Choosing a translator is where readers diverge.",
                "安装很简单。真正让读者产生分歧的，是翻译服务的选择。"),
    )),

    ("table", dict(
        kicker=T("Install", "安装"),
        title=T("Three components, one version constraint that actually bites",
                "三个组件，其中一条版本约束是真的会咬人"),
        headers=[T("Component", "组件"), T("Constraint", "约束"), T("Why", "用途")],
        widths=[2.6, 3, 5.4],
        rows=[
            [T("Python", "Python"), T("`>=3.10, <3.13`", "`>=3.10, <3.13`"),
             T("videocaptioner requirement. 3.13 is NOT supported — check first.",
               "videocaptioner 的硬性要求。3.13 尚不支持 —— 请先确认。")],
            [T("FFmpeg", "FFmpeg"), T("any recent build", "任意较新版本"),
             T("Audio extraction, caption burn-in, and every verification gate",
               "音频提取、字幕烧录，以及每一道验证关卡")],
            [T("videocaptioner", "videocaptioner"), T("`pip install videocaptioner`", "`pip install videocaptioner`"),
             T("The pipeline itself. Verify with `videocaptioner doctor`.",
               "流水线本体。用 `videocaptioner doctor` 验证。")],
        ],
        emphasis_col=0,
        lead=T("Full step-by-step for Windows 11, macOS and Linux: starter/INSTALL.md",
               "Windows 11、macOS、Linux 的完整分步说明见 starter/INSTALL.md"),
    )),

    ("table", dict(
        kicker=T("Translator choice", "翻译服务选择"),
        title=T("Do not copy our translator — your access is not our access",
                "不要照搬我们的翻译服务 —— 你的访问条件与我们不同"),
        headers=[T("Reality", "现实"), T("What that means for you", "对你意味着什么")],
        widths=[3.4, 6.6],
        rows=[
            [T("Default is bing, not llm", "默认值是 bing，不是 llm"),
             T("Omit the flag and you silently get Bing — every command here names the translator explicitly",
               "省略参数就会悄悄用上 Bing —— 本教程每条命令都显式写出翻译服务")],
            [T("Free still needs a key", "免费也仍需密钥"),
             T("Split/Optimize are LLM steps regardless of translator; keyless readers also need --no-optimize --no-split",
               "断句和优化无论选哪个都由 LLM 驱动；没有密钥的读者还需加 --no-optimize --no-split")],
            [T("Region beats budget", "地域比预算更关键"),
             T("Behind a restrictive firewall, Google/Bing are often unreachable; a domestic LLM endpoint usually isn't",
               "在严格防火墙之后，Google/Bing 常不可达，而境内 LLM 端点通常可达")],
            [T("Cost is rarely the barrier", "费用很少是障碍"),
             T("An hour of speech costs less than a coffee — obtaining a key and payment method is the real hurdle",
               "一小时语音成本不到一杯咖啡 —— 拿到密钥和支付方式才是真门槛")],
        ],
        emphasis_col=0,
        lead=T("The first draft told readers to use --translator llm and never fall back "
               "— our API setup restated as a universal rule.",
               "本教程初稿要求使用 --translator llm 且绝不回退 —— 那只是把我们的 API 配置当成了普适规则。"),
        source=T("Full decision guide: docs/choosing_a_translator.md",
                 "完整决策指南：docs/choosing_a_translator.md"),
    )),

    ("table", dict(
        kicker=T("Observed availability", "实测可用性"),
        title=T("Both free options failed for us — one loudly, one silently",
                "两个免费选项对我们都失败了 —— 一个吵闹，一个静默"),
        headers=[T("Option", "选项"), T("Cost", "费用"), T("Result on our test", "我们实测的结果")],
        widths=[2, 1.8, 7.2],
        rows=[
            [T("`llm` (DeepSeek)", "`llm`（DeepSeek）"), T("Paid", "付费"),
             T("Worked. Fluent across a 32-segment and a 1086-segment clip.",
               "可用。在 32 段和 1086 段的片子上都流畅自然。")],
            [T("`bing`", "`bing`"), T("Free", "免费"),
             T("FAIL — 404 on the auth endpoint. Loud, so no bad artifact shipped.",
               "失败 —— 认证端点 404。吵闹地失败，所以不会产出坏成品。")],
            [T("`google`", "`google`"), T("Free", "免费"),
             T("Silently emitted untranslated English and exited 0. The dangerous one.",
               "静默输出未翻译的英文并以 0 退出。危险的那一个。")],
        ],
        emphasis_col=0,
        lead=T("Tested 2026-09-15 from Hong Kong. YOUR results may differ — that is "
               "the whole point. Re-run the probe yourself.",
               "2026-09-15 于香港实测。你的结果可能不同 —— 这正是重点。请自行重跑探测。"),
        source=T("A service that degrades silently is more dangerous than one that fails loudly",
                 "静默降级的服务，比吵闹失败的服务更危险"),
    )),

    ("code", dict(
        kicker=T("Two-minute probe", "两分钟探测"),
        title=T("Probe your access on two segments before committing to a 41-minute clip",
                "在投入 41 分钟的片子之前，先用两段字幕探测你的访问条件"),
        lines=[
            "# 1. Make a 2-segment probe.srt, then:",
            "videocaptioner subtitle probe.srt --translator llm \\",
            "    --target-language zh-Hans --layout target-only -o probe_out.srt",
            "",
            "# 2. Then actually OPEN probe_out.srt and look at it.",
            "#    Chinese text          -> good, proceed",
            "#    A loud error          -> try another option",
            "#    English + 'OK Done'   -> silent passthrough, do NOT proceed",
        ],
        note=T("Outcome three is the one that costs people a day. Look at the file.",
               "第三种结果会让人损失一天。请亲自打开文件看一眼。"),
    )),

    # ------------------------------------------------------------ section 4
    ("divider", dict(
        num="04",
        title=T("Running the pipeline", "运行流水线"),
        blurb=T("Transcribe, read, translate, synthesize", "转写、通读、翻译、合成"),
    )),

    ("table", dict(
        kicker=T("Stage 2", "阶段 2"),
        title=T("Reading the transcript caught three real errors in an 89-second clip",
                "通读转写稿，在 89 秒的片子里抓到三处真实错误"),
        headers=[T("ASR wrote", "ASR 写成"), T("Should be", "应为"), T("Cost if missed", "漏掉的代价")],
        widths=[4, 4, 3],
        rows=[
            [T("`ai`", "`ai`"), T("`AI`", "`AI`"),
             T("Translated as a common noun", "被当作普通名词翻译")],
            [T("`home humanoid robots`", "`home humanoid robots`"),
             T("`humanoid robots`", "`humanoid robots`"),
             T("A word that was never said", "凭空多出一个没说过的词")],
            [T("`neural netells me`", "`neural netells me`"),
             T("`neural network tells me`", "`neural network tells me`"),
             T("Garbled input, garbled output", "输入混乱，输出必然混乱")],
        ],
        emphasis_col=0,
        lead=T("Two minutes to fix in English. A translation-quality problem forever "
               "if allowed through. Edit text lines only — never the indices or timestamps.",
               "在英文阶段改只要两分钟。放过去就永远变成翻译质量问题。只改文本行 —— 绝不动序号和时间轴。"),
    )),

    ("code", dict(
        kicker=T("Stages 3-4", "阶段 3-4"),
        title=T("Go straight to Chinese-only output, then check provenance immediately",
                "直接输出纯中文，然后立刻核查服务溯源"),
        lines=[
            "# Translate — target-only avoids a bilingual file you'd have to redo",
            "videocaptioner subtitle clip.srt --translator llm \\",
            "    --target-language zh-Hans --layout target-only -o clip_zh.srt",
            "",
            "# Gate T2 — run this IMMEDIATELY after the translate you care about",
            "videocaptioner config show        # confirm translate.service",
            "",
            "# Synthesize — version-suffix so attempts are comparable",
            "videocaptioner synthesize clip.mp4 -s clip_zh.srt \\",
            "    --subtitle-mode hard --style default -o clip_captioned_v1.mp4",
        ],
        note=T("config show reports CURRENT state, not per-invocation history. Batch "
               "several translations before checking and the gate is useless.",
               "config show 报告的是当前状态，而非逐次调用历史。连跑多次翻译再检查，这道关卡就失去意义。"),
    )),

    ("bullets", dict(
        kicker=T("Before you style anything", "在调整样式之前"),
        title=T("Check the source for burned-in captions first — they are pixels, not subtitles",
                "先检查源视频是否已烧录字幕 —— 那是像素，不是字幕"),
        lead=T("Grab 2-3 frames spread across the clip. A caption may only appear "
               "during certain moments.",
               "在片子不同位置抓 2-3 帧。字幕可能只在某些时段出现。"),
        bullets=[
            T(("If you find text:", "It is fused into the frames. To ffmpeg it is "
               "indistinguishable from someone's face. No subtitle tool can remove it."),
              ("如果发现文字：", "它已与画面融为一体。对 ffmpeg 而言它和人脸没有区别。任何字幕工具都无法移除。")),
            T(("Your options:", "A clean source export, AI inpainting (often blurry), "
               "crop the region, or position your Chinese captions clear of it."),
              ("你的选项：", "干净的源导出、AI 修复（常发糊）、裁掉该区域，或把中文字幕放到避开它的位置。")),
            T(("Raise margin_bottom", "to lift captions above the existing band. Our "
               "first pilot clip needed this; the second did not."),
              ("调大 margin_bottom", "把字幕抬到已有字幕带之上。我们第一段试点片需要这样做，第二段不需要。")),
            T(("Windows PowerShell warning:", "--style-override JSON needs backslash-"
               "escaped quotes: '{\\\"font_size\\\":56}'. Otherwise quotes are stripped "
               "before the program sees them."),
              ("Windows PowerShell 警告：", "--style-override 的 JSON 需要反斜杠转义引号："
               "'{\\\"font_size\\\":56}'。否则引号在程序看到之前就被剥掉了。")),
        ],
    )),

    # ------------------------------------------------------------ section 5
    ("divider", dict(
        num="05",
        title=T("Verification", "验证"),
        blurb=T("The actual point of the tutorial", "本教程真正的要点"),
    )),

    ("code", dict(
        kicker=T("Gates T1-T4", "关卡 T1-T4"),
        title=T("One command runs every mechanical gate against real artifacts",
                "一条命令，针对真实产物跑完所有机械关卡"),
        lines=[
            "$ python starter/scripts/run_gates.py \\",
            "      --source-video clip.mp4  --source-srt clip.srt \\",
            "      --target-srt clip_zh.srt --output-video clip_captioned_v2.mp4 \\",
            "      --translator llm --target-language zh-Hans",
            "",
            "T1 PASS - clip.srt: 32 segments",
            "T2 PASS - translate.service = llm",
            "T3 PASS - 32 segments in both source and target",
            "T3b PASS - target is genuinely translated, not source passthrough",
            "T4 PASS - 1080x596, 89.131s (source) vs 89.131s (output)",
            "T5 NOT AUTO-VERIFIED - run the procedure by hand",
        ],
        source=T("Verified against the pilot's own artifacts — reviews/03-eng-review.md",
                 "针对试点自身的产物验证通过 —— reviews/03-eng-review.md"),
    )),

    ("table", dict(
        kicker=T("Exit-code contract", "退出码契约"),
        title=T("VOID gets its own exit code so \"meaningless\" can never print as \"success\"",
                "VOID 拥有独立退出码，让「毫无意义」永远不会显示为「成功」"),
        headers=[T("Code", "码"), T("Meaning", "含义"), T("What you should do", "你该怎么做")],
        widths=[1.3, 3.5, 7.2],
        rows=[
            [T("`0`", "`0`"), T("T1-T4 PASS", "T1-T4 全部通过"),
             T("Proceed to Gate T5 by hand", "人工执行 Gate T5")],
            [T("`1`", "`1`"), T("FAIL — a gate caught a real defect", "失败 —— 某道关卡抓到真实缺陷"),
             T("Fix the artifact, never the gate", "修产物，绝不修关卡")],
            [T("`2`", "`2`"), T("VOID — the check was self-referential", "无效 —— 该检查属于自我指涉"),
             T("Alert separately. Not a retry — the check proved nothing.",
               "单独告警。不是重试 —— 这个检查什么也没证明。")],
            [T("`3`", "`3`"), T("Environment error", "环境错误"),
             T("Missing tool or file. Nothing was verified.", "工具或文件缺失。什么都没验证。")],
        ],
        emphasis_col=0,
        source=T("Mirrors Tutorial #2's run_all.sh contract — the single most important "
                 "design decision in either repo",
                 "沿用教程 #2 的 run_all.sh 契约 —— 两个仓库中最重要的单一设计决策"),
    )),

    ("bullets", dict(
        kicker=T("Gate T5", "关卡 T5"),
        title=T("The one gate we refuse to automate, with a procedure instead of a hope",
                "我们拒绝自动化的那道关卡 —— 用流程取代祈祷"),
        lead=T("gstack's process roles can count segments and diff durations. None of "
               "them can read Chinese and judge whether it carries the meaning.",
               "gstack 的流程角色能数分段、比对时长。但它们都无法读中文并判断其是否承载原意。"),
        bullets=[
            T(("Inputs:", "the English .srt and the Chinese .srt. NEVER the video — "
               "that is the circular check."),
              ("输入：", "英文 .srt 与中文 .srt。绝不是视频 —— 那是循环检查。")),
            T(("Sample:", "segments 1-5, a block at ~50%, and the last 5. Note the "
               "source's register first as calibration."),
              ("抽样：", "第 1-5 段、约 50% 处一段、最后 5 段。先记录原文语域作为校准基准。")),
            T(("Four questions per segment:", "Meaning preserved? Natural not literal? "
               "Nothing hallucinated or dropped? Proper nouns and idioms right?"),
              ("每段四个问题：", "原意是否保全？地道而非死译？有无凭空增补或遗漏？专有名词与习语是否正确？")),
            T(("Verdict:", "PASS, or PASS-WITH-FLAG naming the segment. A flagged run "
               "is not done until a human resolves each flag in writing."),
              ("结论：", "PASS，或 PASS-WITH-FLAG 并注明段落。带标记的运行在每处标记被书面处理之前都不算完成。")),
        ],
        source=T("Full contract, RACI and defer clause: docs/expertise_division.md",
                 "完整契约、RACI 与转交条款见：docs/expertise_division.md"),
    )),

    # ------------------------------------------------------------ section 6
    ("divider", dict(
        num="06",
        title=T("What transfers to your next project", "可迁移到你下一个项目的东西"),
        blurb=T("Five disciplines that outlive this particular tool",
                "五条比这个工具本身活得更久的纪律"),
    )),

    ("table", dict(
        kicker=T("Pitfall ledger", "坑位清单"),
        title=T("Every one of these reported success at least once before being caught",
                "以下每一个问题，在被抓到之前都至少报告过一次成功"),
        headers=[T("Symptom", "现象"), T("Cause", "原因"), T("Fix", "处理")],
        widths=[4.2, 3.4, 4.4],
        rows=[
            [T("Translation \"succeeded\", output is English", "翻译「成功」，但输出是英文"),
             T("Free translator swallowed a 429", "免费翻译器吞掉了 429"),
             T("Gate T3b; switch translators", "Gate T3b；更换翻译服务")],
            [T("JSON error on a correct-looking command", "命令看起来正确却报 JSON 错误"),
             T("PowerShell stripped the quotes", "PowerShell 剥掉了引号"),
             T("Backslash-escape: `'{\\\"k\\\":1}'`", "反斜杠转义：`'{\\\"k\\\":1}'`")],
            [T("Gate T1 counts one segment short", "Gate T1 少数一个分段"),
             T("UTF-8 BOM on the first line", "首行有 UTF-8 BOM"),
             T("Read with `utf-8-sig`", "用 `utf-8-sig` 读取")],
            [T("Chinese captions overlap on-screen text", "中文字幕与画面文字重叠"),
             T("Source has burned-in captions", "源视频有已烧录字幕"),
             T("Raise `margin_bottom`", "调大 `margin_bottom`")],
            [T("`command not found` after a good install", "安装成功后仍提示 `command not found`"),
             T("Scripts dir not on PATH", "Scripts 目录不在 PATH 中"),
             T("Add it, reopen the terminal", "加入 PATH，重开终端")],
        ],
        source=T("The BOM bug was ours — found only because a test file came from "
                 "PowerShell, not from videocaptioner",
                 "BOM 缺陷是我们自己的 —— 只因为一个测试文件来自 PowerShell 而非 videocaptioner 才被发现"),
    )),

    ("table", dict(
        kicker=T("Transferable disciplines", "可迁移的纪律"),
        title=T("Five habits that apply to any pipeline where a wrong artifact is expensive",
                "五个习惯，适用于任何「产出错误结果代价高昂」的流水线"),
        headers=[T("Discipline", "纪律"), T("Why", "为什么")],
        widths=[3.6, 6.4],
        rows=[
            [T("Check the output, not the exit code", "检查输出，而不是退出码"),
             T("Every failure in our pitfall ledger reported success at least once",
               "我们坑位清单里的每一个失败，都至少曾报告过一次成功")],
            [T("Never verify an artifact against itself", "绝不用产物自己验证自己"),
             T("OCR-vs-own-srt here; an LVS netlist derived from the GDS under test in Tutorial #2 — same error",
               "这里是 OCR 对比自己的 srt；教程 #2 是从待测 GDS 导出网表跑 LVS —— 同一个错误")],
            [T("Give \"meaningless\" its own signal", "给「无意义」一个独立信号"),
             T("VOID has a distinct exit code so it can never be mistaken for PASS",
               "VOID 有独立退出码，不会被误认为 PASS")],
            [T("Name the gap you cannot close", "明确点出你封不住的缺口"),
             T("Gate T5 is not automated and the docs say so, not implying full coverage",
               "Gate T5 没有自动化，文档就直说，而非暗示覆盖完整")],
            [T("The reader's environment is not yours", "读者的环境不是你的环境"),
             T("The translator-choice chapter exists because our first draft handed down our own API setup as a rule",
               "「翻译服务选择」一章的由来：初稿曾把我们自己的 API 配置当成了规则")],
        ],
        emphasis_col=0,
    )),

    ("table", dict(
        kicker=T("The series", "系列定位"),
        title=T("Tutorial #3 tests whether the pattern still pays on an easy subject",
                "教程 #3 检验的是：这套模式在简单主题上是否依然划算"),
        headers=[T("", ""), T("Tutorial #1", "教程 #1"), T("Tutorial #2", "教程 #2"), T("Tutorial #3", "教程 #3")],
        widths=[2.6, 2.6, 3.4, 3.4],
        rows=[
            [T("Carrier", "载体"), T("hello_world.py", "hello_world.py"),
             T("RTL→GDS EDA system", "RTL→GDS 芯片设计系统"),
             T("EN→ZH video captions", "英译中视频字幕")],
            [T("Team", "团队"), T("5 gstack roles", "5 个 gstack 角色"),
             T("5 roles × 2 domain agents", "5 角色 × 2 领域智能体"),
             T("5 roles × 1 domain reviewer", "5 角色 × 1 领域审阅者")],
            [T("Proof of done", "完成的证明"), T("reviews merge", "评审合并"),
             T("gate chain + GDS SHA match", "关卡链 + GDS SHA 一致"),
             T("gates T1-T4 + T5 review", "关卡 T1-T4 + T5 审阅")],
            [T("Setup", "环境"), T("none", "无"), T("multi-GB open EDA + PDK", "数 GB 开源 EDA + PDK"),
             T("one pip install + FFmpeg", "一次 pip install + FFmpeg")],
            [T("Time", "耗时"), T("minutes", "数分钟"), T("10-14 h", "10-14 小时"), T("2.5-7 h", "2.5-7 小时")],
        ],
        emphasis_col=0,
        lead=T("Answer: yes, but the authority split is lighter. One domain reviewer, "
               "not two, and its veto fires on exactly one gate.",
               "答案：是的，但权威划分更轻。一位领域审阅者而非两位，且其否决权只在一道关卡上生效。"),
    )),

    ("bullets", dict(
        kicker=T("Definition of done", "完成的定义"),
        title=T("Eight lines. Anything less is a draft, not a deliverable",
                "八条。达不到任何一条，就还是草稿，不是交付物"),
        bullets=[
            T((None, "Gates T1-T4 PASS — run_gates.py exits 0"),
              (None, "Gates T1-T4 全部通过 —— run_gates.py 以 0 退出")),
            T((None, "Gate T5 reviewed, every flag resolved in writing"),
              (None, "Gate T5 已审阅，每处标记均有书面处理")),
            T((None, "config show evidence captured proving the intended translator ran"),
              (None, "已捕获 config show 证据，证明运行的是预期的翻译服务")),
            T((None, "Output resolution and duration verified identical to source"),
              (None, "已验证输出的分辨率与时长与源文件完全一致")),
            T((None, "At least one rendered frame visually inspected"),
              (None, "至少目视检查了一帧输出画面")),
            T((None, "Source checked for pre-existing burned-in captions"),
              (None, "已检查源视频是否有预先烧录的字幕")),
            T((None, "versions.lock filled in — versions, provider, model, run date"),
              (None, "versions.lock 已填写 —— 版本、服务商、模型、运行日期")),
            T((None, "Known gaps stated in writing, not hidden"),
              (None, "已知缺口已书面写明，而非隐藏")),
        ],
    )),

    ("quote", dict(
        kicker=T("Close", "结语"),
        quote=T("A gate that is relaxed to pass\nis not a gate.",
                "为了通过而放宽的关卡，\n就不是关卡。"),
        attrib=T("gstack Tutorial series — the rule that survives every subject change",
                 "gstack 教程系列 —— 唯一一条跨越所有主题都成立的规则"),
    )),
]
