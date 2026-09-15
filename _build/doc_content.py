# -*- coding: utf-8 -*-
"""Word-document content for gstack Tutorial No.3, both languages in one tree.

Same single-source principle as deck_content.py: EN and ZH are generated
from one structure so they cannot drift apart.
"""
from deck_content import L, pick  # reuse the localization marker

T = L

DOC = {
    "kicker": T("gstack Tutorial No. 3", "gstack 教程 第三部"),
    "title": T("English → Chinese Video Captioning, Verified",
               "英译中视频字幕：可验证的工作流"),
    "subtitle": T("Building a caption pipeline with videocaptioner, and proving "
                  "the output is right with a five-gate verification chain",
                  "用 videocaptioner 搭建字幕流水线，并用五道关卡验证链证明输出正确"),
    "meta": [
        T("gstack orchestration + one domain reviewer",
          "gstack 流程编排 + 一位领域审阅者"),
        T("Prof. Yi-Kuen Lee", "李奕锟 教授"),
        T("September 2026", "2026 年 9 月"),
        T("Prose CC BY 4.0 · Code Apache-2.0", "文字 CC BY 4.0 · 代码 Apache-2.0"),
    ],

    "exec_heading": T("Executive Summary", "执行摘要"),
    "exec_paras": [
        T("This tutorial teaches a complete English-to-Chinese video captioning "
          "pipeline built on the videocaptioner CLI: transcribe speech with ASR, "
          "correct the transcript, translate to Simplified Chinese, and burn the "
          "captions into the video. Those four commands are the easy part and take "
          "an afternoon to learn.",
          "本教程讲授一条完整的英译中视频字幕流水线，基于 videocaptioner 命令行工具：用 ASR 转写语音、"
          "校正转写稿、翻译为简体中文，并将字幕烧录进视频。这四条命令是简单的部分，一个下午就能学会。"),
        T("The subject of the tutorial is not the commands. It is verification. "
          "Every stage of this pipeline can fail while reporting success: ASR "
          "mishears a word and writes something plausible; a translation service "
          "hits a rate limit, swallows the error, and returns your English text as "
          "the translation with exit code 0; captions render off-frame or overlap "
          "text already burned into the source video.",
          "本教程的主题不是命令，而是验证。这条流水线的每个阶段都可能在报告成功的同时失败：ASR 听错一个词却"
          "写出看似合理的内容；翻译服务触发限流、吞掉错误，把你的英文原文当作译文返回且退出码为 0；"
          "字幕渲染到画面外，或与源视频中已烧录的文字重叠。"),
        T("The middle failure is not hypothetical. It occurred while this tutorial "
          "was being built, and it defeated four of the five verification gates that "
          "existed at the time: the translator provenance check passed (the service "
          "really was the one requested), the segment parity check passed (two "
          "segments in, two out), and the synthesis fidelity check would have passed "
          "(the video was structurally perfect). The chain verified everything except "
          "whether translation had actually occurred. A sixth gate was added because "
          "of it.",
          "中间那个失败不是假设。它在本教程编写过程中真实发生，并骗过了当时已有的五道关卡中的四道：翻译服务"
          "溯源检查通过（实际运行的确实是指定的服务）、分段一致性检查通过（输入两段、输出两段）、"
          "合成保真度检查也会通过（视频结构完美）。整条验证链检查了一切，唯独没检查翻译是否真的发生。"
          "正因如此，我们新增了一道关卡。"),
        T("The discipline this teaches transfers to any pipeline where a wrong "
          "artifact is expensive and a generalist cannot detect it: check the output "
          "rather than the exit code, never verify an artifact against something "
          "derived from itself, give \"meaningless\" its own distinct signal, and name "
          "the gap you cannot close instead of implying full coverage.",
          "本教程教授的纪律，可迁移到任何「产出错误结果代价高昂、且通才无法察觉」的流水线：检查输出而非退出码、"
          "绝不用源自产物自身的东西验证该产物、给「无意义」一个独立信号，以及明确点出你封不住的缺口，"
          "而不是暗示覆盖完整。"),
    ],

    "metrics_heading": T("At a glance", "关键指标"),
    "metrics_caption": T("Key question: what does this cost, and what do you get?",
                         "关键问题：这需要多少投入，又能得到什么？"),
    "metrics_headers": [T("Dimension", "维度"), T("Value", "数值")],
    "metrics_rows": [
        [T("Time investment (first run)", "时间投入（首次运行）"),
         T("2-4 h no-surprises; 2.5-7 h honest range", "顺利情况 2-4 小时；老实区间 2.5-7 小时")],
        [T("Difficulty", "难度"),
         T("Low mechanically; the discipline is the hard part", "机械操作难度低；纪律才是难点")],
        [T("Team size", "团队规模"),
         T("Solo, or 5 gstack roles + 1 domain reviewer", "单人，或 5 个 gstack 角色 + 1 位领域审阅者")],
        [T("Toolchain", "工具链"),
         T("One pip install + FFmpeg", "一次 pip install + FFmpeg")],
        [T("Verification gates", "验证关卡"),
         T("5 — four mechanical, one human", "5 道 —— 四道机械，一道人工")],
        [T("Outcome", "产出"),
         T("Captioned video plus evidence it is correct", "带字幕的视频，以及它正确的证据")],
    ],

    "toc_heading": T("Table of Contents", "目录"),
    "toc": [
        T("Why Verification Is the Subject", "为什么「验证」才是主题"),
        T("The Pipeline and Its Gates", "流水线及其关卡"),
        T("Installation", "安装"),
        T("Choosing a Translator", "选择翻译服务"),
        T("Running the Pipeline", "运行流水线"),
        T("Verification in Practice", "验证实操"),
        T("Pitfall Ledger", "坑位清单"),
        T("Definition of Done", "完成的定义"),
    ],

    "sections": [
        # ---------------------------------------------------------- 1
        {
            "title": T("Why Verification Is the Subject", "为什么「验证」才是主题"),
            "blocks": [
                ("p", T("A pipeline that produces a file is not the same as a pipeline "
                        "that produces a correct file. The distance between those two "
                        "things is what this tutorial is about.",
                        "「能产出文件的流水线」和「能产出正确文件的流水线」不是一回事。"
                        "本教程讲的就是这两者之间的距离。")),
                ("callout", T("\"✓ Done\" is a string. The output file is the evidence.",
                              "「✓ Done」只是一个字符串。输出文件本身才是证据。")),
                ("p", T("This is the same lesson gstack Tutorial #2 taught with \"'PASS' "
                        "is a string, the log is the evidence\" — a different domain, an "
                        "identical discipline. The pattern is worth learning on an easy "
                        "subject before you need it on a hard one.",
                        "这与 gstack 教程 #2 的「'PASS' 只是字符串，日志才是证据」是同一条教训 —— "
                        "领域不同，纪律相同。值得先在简单主题上学会，免得等到困难主题才需要。")),
                ("h2", T("How each stage fails quietly", "每个阶段如何静默失败")),
                ("table", [T("Stage", "阶段"), T("Quiet failure", "静默失败"),
                           T("What catches it", "由谁抓住")],
                 [[T("Transcribe", "转写"),
                   T("ASR mishears a word and writes something plausible",
                     "ASR 听错一个词，写出看似合理的内容"),
                   T("A human reading it", "人工通读")],
                  [T("Translate", "翻译"),
                   T("Rate limit swallowed; English returned as the translation",
                     "限流被吞掉；英文原文被当作译文返回"),
                   T("Gate T3b", "Gate T3b")],
                  [T("Translate", "翻译"),
                   T("A different translator runs than the one requested",
                     "实际运行的翻译服务并非指定的那个"),
                   T("Gate T2", "Gate T2")],
                  [T("Synthesize", "合成"),
                   T("Captions off-frame or overlapping burned-in text",
                     "字幕在画面外，或与已烧录文字重叠"),
                   T("Gate T4 and your eyes", "Gate T4 与你的眼睛")]],
                 [2, 5, 3]),
                ("h2", T("The incident, reproduced", "事故复现")),
                ("p", T("Tested on 2026-09-15 with videocaptioner 1.4.2 on Windows 11 "
                        "from a Hong Kong network, using a two-segment probe file:",
                        "2026-09-15 实测，videocaptioner 1.4.2，Windows 11，香港网络，"
                        "使用两段字幕的探测文件：")),
                ("code", [
                    "$ videocaptioner subtitle probe.srt --translator google \\",
                    "      --target-language zh-Hans --layout target-only -o out.srt",
                    "",
                    "ERROR - Google translation failed 1: 429 Too Many Requests",
                    "ERROR - Google translation failed 2: 429 Too Many Requests",
                    "OK Done -> out.srt (2 segments)",
                    "exit code: 0",
                ]),
                ("p", T("The output file contained the original English, unchanged. The "
                        "errors were logged and then swallowed. The exit code was 0. The "
                        "segment count was correct. The file was well-formed. The only "
                        "thing wrong with it was that it contained no Chinese.",
                        "输出文件包含的是原封不动的英文。错误被记录，然后被吞掉。退出码是 0。分段数正确。"
                        "文件格式良好。它唯一的问题是：里面没有中文。")),
                ("caption", T("Source: reviews/04-qa-report.md, Finding 1",
                              "来源：reviews/04-qa-report.md 发现 1")),
            ],
        },
        # ---------------------------------------------------------- 2
        {
            "title": T("The Pipeline and Its Gates", "流水线及其关卡"),
            "blocks": [
                ("p", T("Four commands, one mandatory human read-through, and a chain of "
                        "five gates.",
                        "四条命令、一次必须的人工通读，以及一条由五道关卡组成的验证链。")),
                ("code", [
                    "your .mp4  -> [transcribe] ->  English .srt",
                    "                                    |",
                    "                              [you read it]   <- do not skip",
                    "                                    v",
                    "                              corrected .srt",
                    "                                    |",
                    "                               [translate]",
                    "                                    v",
                    "                              Chinese .srt",
                    "                                    |",
                    "                              [synthesize]",
                    "                                    v",
                    "                         captioned .mp4 -> [5 gates]",
                ]),
                ("h2", T("The five gates", "五道关卡")),
                ("table", [T("Gate", "关卡"), T("Checks", "检查什么"),
                           T("Mechanical", "可机械执行")],
                 [[T("T1", "T1"), T("Transcription produced segments", "转写确实产出了分段"), T("Yes", "是")],
                  [T("T2", "T2"), T("The translator that ran is the one requested", "实际运行的翻译服务就是指定的那个"), T("Yes", "是")],
                  [T("T3", "T3"), T("No segments dropped or merged", "没有分段被丢弃或合并"), T("Yes", "是")],
                  [T("T3b", "T3b"), T("Translation happened — not English passthrough", "翻译确实发生 —— 而非英文透传"), T("Yes", "是")],
                  [T("T4", "T4"), T("Output matches source resolution and duration", "输出与源文件分辨率、时长一致"), T("Yes", "是")],
                  [T("T5", "T5"), T("The Chinese is faithful and natural", "中文忠实且地道"), T("No", "否")]],
                 [1.2, 6, 2]),
                ("h2", T("The circularity trap", "循环论证陷阱")),
                ("p", T("A tempting way to verify the translation: OCR the burned-in "
                        "captions from the finished video and compare that text against "
                        "the subtitle file used to produce it. That check is worthless "
                        "for translation fidelity. It compares the output to itself. It "
                        "proves synthesis did not corrupt the text, which Gate T4 already "
                        "covers, and says nothing about whether the Chinese is a correct "
                        "translation of the English audio.",
                        "一个诱人的译文验证方法：用 OCR 识别成片中烧录的字幕，与生成它的字幕文件比对。"
                        "这个检查对翻译保真度毫无价值 —— 它是拿输出和它自己比。它只能证明合成没有损坏文本"
                        "（而 Gate T4 已覆盖），完全无法说明中文是否是英文音频的正确翻译。")),
                ("p", T("The gate script refuses this explicitly. Passing --ocr-check "
                        "exits with code 2 (VOID), not 0 and not 1. VOID has its own exit "
                        "code so that \"the gate passed\" and \"the gate was meaningless\" can "
                        "never print the same result.",
                        "关卡脚本显式拒绝这种做法。传入 --ocr-check 会以退出码 2（VOID，无效）退出，"
                        "既不是 0 也不是 1。VOID 拥有独立退出码，就是为了让「关卡通过」与「关卡毫无意义」"
                        "永远不会输出相同结果。")),
                ("callout", T("Never verify an artifact against something derived from itself.",
                              "绝不用源自产物自身的东西去验证该产物。")),
            ],
        },
        # ---------------------------------------------------------- 3
        {
            "title": T("Installation", "安装"),
            "blocks": [
                ("table", [T("Component", "组件"), T("Constraint", "约束"), T("Purpose", "用途")],
                 [[T("Python", "Python"), T("`>=3.10, <3.13`", "`>=3.10, <3.13`"),
                   T("videocaptioner requirement; 3.13 is not supported", "videocaptioner 的要求；3.13 尚不支持")],
                  [T("FFmpeg", "FFmpeg"), T("any recent build", "任意较新版本"),
                   T("Audio extraction, burn-in, and every gate", "音频提取、烧录，以及每道关卡")],
                  [T("videocaptioner", "videocaptioner"), T("`pip install videocaptioner`", "`pip install videocaptioner`"),
                   T("The pipeline itself", "流水线本体")]],
                 [2.2, 2.4, 4.4]),
                ("p", T("Verify the installation before proceeding. The doctor subcommand "
                        "checks Python, FFmpeg, ffprobe and the configuration file in one "
                        "shot. A warning about the dubbing API key is expected and harmless; "
                        "dubbing is out of scope for this tutorial.",
                        "继续之前先验证安装。doctor 子命令会一次性检查 Python、FFmpeg、ffprobe 和配置文件。"
                        "关于配音 API 密钥的警告是预期内的、无害的；配音不在本教程范围内。")),
                ("code", [
                    "videocaptioner --version",
                    "videocaptioner doctor",
                    "videocaptioner config show",
                ]),
                ("callout", T("Windows: read starter/INSTALL.md section 6 on PowerShell "
                              "quote-stripping before you need it, not after the error appears.",
                              "Windows 用户：请在需要之前就读 starter/INSTALL.md 第 6 节关于 "
                              "PowerShell 剥除引号的说明，而不是等报错出现才读。")),
            ],
        },
        # ---------------------------------------------------------- 4
        {
            "title": T("Choosing a Translator", "选择翻译服务"),
            "blocks": [
                ("p", T("This is the step most likely to differ between you and every "
                        "other reader. The first draft of this tutorial instructed readers "
                        "to use the LLM translator and never fall back to a free service. "
                        "That was the author's own API setup restated as a universal rule. "
                        "Which translators are actually available depends on your machine, "
                        "your network, your country, and whether you hold a paid API key.",
                        "这一步最可能因人而异。本教程初稿要求读者使用 LLM 翻译服务且绝不回退到免费服务 —— "
                        "那其实只是把作者自己的 API 配置当成了普适规则。实际可用的翻译服务，取决于你的电脑、"
                        "你的网络、你所在的国家，以及你是否持有付费 API 密钥。")),
                ("h2", T("Three surprises", "三个意外")),
                ("bullets", [
                    (T("The default is bing, not llm.", "默认是 bing，不是 llm。"),
                     T("Omit the --translator flag and you silently get Bing. Every command "
                       "in this tutorial names the translator explicitly for this reason.",
                       "省略 --translator 参数，你会悄无声息地用上 Bing。正因如此，本教程每条命令都显式写出翻译服务。")),
                    (T("A free translator still needs an LLM key.", "免费翻译服务仍需 LLM 密钥。"),
                     T("The split and optimize steps are LLM-powered regardless of translator "
                       "choice. A reader with no key also needs --no-optimize --no-split.",
                       "断句与优化两步无论选哪个翻译服务都由 LLM 驱动。没有密钥的读者还需加 --no-optimize --no-split。")),
                    (T("Region decides more than budget.", "地域比预算更具决定性。"),
                     T("Behind a restrictive firewall, Google and Bing endpoints are often "
                       "unreachable while a domestic LLM endpoint is not.",
                       "在严格防火墙之后，Google 与 Bing 端点常常不可达，而境内 LLM 端点通常可达。")),
                ]),
                ("h2", T("What we observed", "我们的实测结果")),
                ("table", [T("Option", "选项"), T("Cost", "费用"), T("Result", "结果")],
                 [[T("`llm` (DeepSeek)", "`llm`（DeepSeek）"), T("Paid", "付费"),
                   T("Worked; fluent across 32- and 1086-segment clips", "可用；在 32 段与 1086 段的片子上都流畅")],
                  [T("`bing`", "`bing`"), T("Free", "免费"),
                   T("Failed loudly — 404 on the auth endpoint", "吵闹地失败 —— 认证端点 404")],
                  [T("`google`", "`google`"), T("Free", "免费"),
                   T("Silently returned untranslated English, exit 0", "静默返回未翻译的英文，退出码 0")]],
                 [2.2, 1.6, 5.2]),
                ("caption", T("Tested 2026-09-15 from Hong Kong. Your results may differ — "
                              "that is the point. Re-run the probe yourself.",
                              "2026-09-15 于香港实测。你的结果可能不同 —— 这正是重点。请自行重跑探测。")),
                ("p", T("A service that degrades silently is more dangerous than one that "
                        "fails loudly. Bing's 404 wastes an afternoon. Google's silent "
                        "passthrough could waste a submission.",
                        "静默降级的服务比吵闹失败的服务更危险。Bing 的 404 浪费你一个下午；"
                        "Google 的静默透传可能毁掉你的一次提交。")),
                ("h2", T("Probe before committing", "投入前先探测")),
                ("code", [
                    "# Make a 2-segment probe.srt, then:",
                    "videocaptioner subtitle probe.srt --translator llm \\",
                    "    --target-language zh-Hans --layout target-only -o probe_out.srt",
                    "",
                    "# Then OPEN probe_out.srt and look at it:",
                    "#   Chinese text        -> good, proceed",
                    "#   A loud error        -> try another option",
                    "#   English + 'OK Done' -> silent passthrough, do NOT proceed",
                ]),
            ],
        },
        # ---------------------------------------------------------- 5
        {
            "title": T("Running the Pipeline", "运行流水线"),
            "blocks": [
                ("h2", T("Transcribe, then read", "转写，然后通读")),
                ("code", [
                    "videocaptioner transcribe clip.mp4 --asr bijian --language en \\",
                    "    -o clip.srt",
                ]),
                ("p", T("Then open the transcript and read it. This is the step everyone "
                        "skips. ASR errors are two-minute fixes in English and become "
                        "permanent translation-quality problems if allowed through. Edit "
                        "the text lines only, never the segment indices or timestamps, "
                        "because Gate T3 checks that the count is unchanged.",
                        "然后打开转写稿通读。这是所有人都想跳过的一步。ASR 错误在英文阶段改只要两分钟，"
                        "放过去就会变成永久的翻译质量问题。只修改文本行，绝不动分段序号和时间轴，"
                        "因为 Gate T3 会检查分段数未变。")),
                ("table", [T("ASR wrote", "ASR 写成"), T("Should be", "应为")],
                 [[T("`ai`", "`ai`"), T("`AI`", "`AI`")],
                  [T("`home humanoid robots`", "`home humanoid robots`"), T("`humanoid robots`", "`humanoid robots`")],
                  [T("`neural netells me`", "`neural netells me`"), T("`neural network tells me`", "`neural network tells me`")]],
                 [4, 4]),
                ("caption", T("Three real errors caught in an 89-second pilot clip.",
                              "在 89 秒的试点片段中抓到的三处真实错误。")),
                ("h2", T("Check the source for burned-in captions", "检查源视频是否已烧录字幕")),
                ("p", T("Do this before translating; it decides whether caption positioning "
                        "work is needed at all. Grab two or three frames spread across the "
                        "clip, because a caption may only appear during certain moments. "
                        "If you find burned-in text, it is fused into the pixels — to ffmpeg "
                        "it is indistinguishable from someone's face, and no subtitle tool "
                        "can remove it.",
                        "请在翻译之前做这件事；它决定你是否需要做字幕位置调整。在片子不同位置抓两三帧，"
                        "因为字幕可能只在某些时段出现。如果发现已烧录的文字，它已与像素融为一体 —— "
                        "对 ffmpeg 而言它和人脸没有区别，任何字幕工具都无法移除。")),
                ("code", [
                    "ffmpeg -y -ss 30 -i clip.mp4 -frames:v 1 -update 1 frame30.png",
                    "ffmpeg -y -ss 60 -i clip.mp4 -frames:v 1 -update 1 frame60.png",
                ]),
                ("h2", T("Translate and synthesize", "翻译与合成")),
                ("code", [
                    "# target-only avoids a bilingual file you would have to redo",
                    "videocaptioner subtitle clip.srt --translator llm \\",
                    "    --target-language zh-Hans --layout target-only -o clip_zh.srt",
                    "",
                    "# Gate T2 - run IMMEDIATELY after the translate you care about",
                    "videocaptioner config show",
                    "",
                    "videocaptioner synthesize clip.mp4 -s clip_zh.srt \\",
                    "    --subtitle-mode hard --style default -o clip_captioned_v1.mp4",
                ]),
                ("p", T("config show reports current configuration state, not per-invocation "
                        "history. Running several translations before checking makes the "
                        "gate useless.",
                        "config show 报告的是当前配置状态，而非逐次调用历史。连跑多次翻译再检查，"
                        "这道关卡就失去意义。")),
            ],
        },
        # ---------------------------------------------------------- 6
        {
            "title": T("Verification in Practice", "验证实操"),
            "blocks": [
                ("code", [
                    "$ python starter/scripts/run_gates.py \\",
                    "      --source-video clip.mp4  --source-srt clip.srt \\",
                    "      --target-srt clip_zh.srt \\",
                    "      --output-video clip_captioned_v2.mp4 \\",
                    "      --translator llm --target-language zh-Hans",
                    "",
                    "T1 PASS - clip.srt: 32 segments",
                    "T2 PASS - translate.service = llm",
                    "T3 PASS - 32 segments in both source and target",
                    "T3b PASS - target is genuinely translated, not passthrough",
                    "T4 PASS - 1080x596, 89.131s (source) vs 89.131s (output)",
                    "T5 NOT AUTO-VERIFIED - run the procedure by hand",
                ]),
                ("h2", T("Exit-code contract", "退出码契约")),
                ("table", [T("Code", "码"), T("Meaning", "含义"), T("Action", "应对")],
                 [[T("`0`", "`0`"), T("T1-T4 PASS", "T1-T4 全部通过"), T("Proceed to Gate T5 by hand", "人工执行 Gate T5")],
                  [T("`1`", "`1`"), T("A gate caught a real defect", "某道关卡抓到真实缺陷"), T("Fix the artifact, never the gate", "修产物，绝不修关卡")],
                  [T("`2`", "`2`"), T("VOID — the check was self-referential", "无效 —— 该检查自我指涉"), T("Alert separately; nothing was proved", "单独告警；什么也没证明")],
                  [T("`3`", "`3`"), T("Environment error", "环境错误"), T("Missing tool or file", "工具或文件缺失")]],
                 [1.2, 4, 4]),
                ("h2", T("Gate T5, by hand", "人工执行 Gate T5")),
                ("p", T("gstack's process roles can count segments and diff durations. None "
                        "of them can read Chinese and judge whether it carries the meaning "
                        "of the English. That is the single expertise gap in this project, "
                        "and Gate T5 closes it with a procedure rather than a hope.",
                        "gstack 的流程角色能数分段、比对时长，但都无法读中文并判断其是否承载了英文原意。"
                        "这是本项目唯一的专业能力缺口，Gate T5 用流程而非祈祷来封堵它。")),
                ("bullets", [
                    (T("Inputs:", "输入："),
                     T("the English .srt and the Chinese .srt — never the video, which is "
                       "the circular check.",
                       "英文 .srt 与中文 .srt —— 绝不是视频，那是循环检查。")),
                    (T("Sample:", "抽样："),
                     T("segments 1-5, a block at roughly the 50% mark, and the last 5. Note "
                       "the source's register first, as calibration.",
                       "第 1-5 段、约 50% 处的一段，以及最后 5 段。先记录原文语域作为校准基准。")),
                    (T("Four questions per segment:", "每段四个问题："),
                     T("Is the meaning preserved? Is it natural rather than literal? Is "
                       "anything hallucinated or dropped? Are proper nouns and idioms right?",
                       "原意是否保全？是否地道而非死译？有无凭空增补或遗漏？专有名词与习语是否正确？")),
                    (T("Verdict:", "结论："),
                     T("PASS, or PASS-WITH-FLAG naming the segment. A flagged run is not "
                       "done until a human resolves each flag in writing.",
                       "PASS，或 PASS-WITH-FLAG 并注明段落。带标记的运行在每处标记被书面处理之前都不算完成。")),
                ]),
            ],
        },
        # ---------------------------------------------------------- 7
        {
            "title": T("Pitfall Ledger", "坑位清单"),
            "blocks": [
                ("p", T("Every entry below reported success at least once before being "
                        "caught.",
                        "以下每一条，在被抓到之前都至少报告过一次成功。")),
                ("table", [T("Symptom", "现象"), T("Cause", "原因"), T("Fix", "处理")],
                 [[T("Translation succeeded, output is English", "翻译成功，但输出是英文"),
                   T("Free translator swallowed a 429", "免费翻译器吞掉了 429"),
                   T("Gate T3b; switch translators", "Gate T3b；更换翻译服务")],
                  [T("JSON error on a correct-looking command", "命令看起来正确却报 JSON 错误"),
                   T("PowerShell stripped the quotes", "PowerShell 剥掉了引号"),
                   T("Backslash-escape each quote", "为每个引号加反斜杠转义")],
                  [T("Gate T1 counts one segment short", "Gate T1 少数一个分段"),
                   T("UTF-8 BOM on the first line", "首行有 UTF-8 BOM"),
                   T("Read with `utf-8-sig`", "用 `utf-8-sig` 读取")],
                  [T("Captions overlap on-screen text", "字幕与画面文字重叠"),
                   T("Source has burned-in captions", "源视频有已烧录字幕"),
                   T("Raise `margin_bottom`", "调大 `margin_bottom`")],
                  [T("`command not found` after a good install", "安装成功后仍提示未找到命令"),
                   T("Scripts directory not on PATH", "Scripts 目录不在 PATH 中"),
                   T("Add it and reopen the terminal", "加入 PATH 并重开终端")]],
                 [3.6, 3, 3.4]),
                ("caption", T("The BOM bug was our own, found only because a test file came "
                              "from PowerShell rather than from videocaptioner. Test your "
                              "gates with files from a different producer than the one they "
                              "normally consume.",
                              "BOM 缺陷是我们自己的，只因为一个测试文件来自 PowerShell 而非 videocaptioner 才被发现。"
                              "请用「与关卡平常消费的生产者不同」的来源文件去测试你的关卡。")),
            ],
        },
        # ---------------------------------------------------------- 8
        {
            "title": T("Definition of Done", "完成的定义"),
            "blocks": [
                ("p", T("Eight lines. Anything less is a draft, not a deliverable.",
                        "八条。达不到任何一条，就还是草稿，不是交付物。")),
                ("bullets", [
                    (None, T("Gates T1-T4 PASS — run_gates.py exits 0",
                             "Gates T1-T4 全部通过 —— run_gates.py 以 0 退出")),
                    (None, T("Gate T5 reviewed, every flag resolved in writing",
                             "Gate T5 已审阅，每处标记均有书面处理")),
                    (None, T("config show evidence captured proving the intended translator ran",
                             "已捕获 config show 证据，证明运行的是预期的翻译服务")),
                    (None, T("Output resolution and duration verified identical to source",
                             "已验证输出的分辨率与时长与源文件完全一致")),
                    (None, T("At least one rendered frame visually inspected",
                             "至少目视检查了一帧输出画面")),
                    (None, T("Source checked for pre-existing burned-in captions",
                             "已检查源视频是否有预先烧录的字幕")),
                    (None, T("versions.lock filled in — versions, provider, model, run date",
                             "versions.lock 已填写 —— 版本、服务商、模型、运行日期")),
                    (None, T("Known gaps stated in writing, not hidden",
                             "已知缺口已书面写明，而非隐藏")),
                ]),
                ("callout", T("A gate that is relaxed to pass is not a gate.",
                              "为了通过而放宽的关卡，就不是关卡。")),
            ],
        },
    ],
}
