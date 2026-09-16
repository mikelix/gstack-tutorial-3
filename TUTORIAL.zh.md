# gstack 教程 #3 —— 英译中视频字幕，并加以验证

**学完之后你能做到：** 拿到任意一段英文口语视频，产出烧录了规范、位置得当的
中文字幕的版本 —— 并且手上有**具体证据**证明输出正确，而不是只看了一遍觉得
"看起来没问题"。

**耗时：** 顺利情况下 2-4 小时；老实说是 2.5-7 小时（区间为何这么宽，见
[`reviews/02-spec.md`](reviews/02-spec.md)）。

**前置条件：** 一台 Windows 11、macOS 或 Linux 电脑；一段英文口语视频；以及
关于翻译服务可用性的一个决定 —— 第 2 部分会带你做这个决定。

English version: [`TUTORIAL.md`](TUTORIAL.md)

> **教育用途声明。** 本教程以及 [`starter/sample/`](starter/sample/README.md)
> 中的示例片段，仅供教学使用 —— 目的是讲授一套可验证的字幕制作流程。对你
> 用它来字幕化的任何视频，请遵循第 2 部分与 [`LICENSE.md`](LICENSE.md) 所述
> 的素材版权审查原则：本项目不授予任何第三方素材的使用权，本文档也不构成
> 版权法律意见。

---

## 第 0 部分 —— 心智模型

### 0.1 这条流水线到底是什么

```
  你的 .mp4 ──► [转写] ──►  英文 .srt
                                │
                           [你亲自通读]      ← 不要跳过
                                │
                                ▼
                          校正后的 .srt
                                │
                            [翻译]
                                ▼
                           中文 .srt
                                │
                            [合成]
                                ▼
                      带字幕的 .mp4  ──► [验证：5 道关卡]
```

四条命令、一次人工通读，外加一条验证链。命令是简单的部分。
**本教程真正讲的是验证。**

### 0.2 为什么验证才是主题

这条流水线的每一个阶段，都可能在"报告成功"的同时悄悄出错：

| 阶段 | 它如何静默失败 |
|---|---|
| 转写 | ASR 听错一个词，写出一个看似合理的结果 |
| 翻译 | 服务触发限流，吞掉错误，把你的**英文原文**当作"译文"返回 —— 退出码 0，还带着愉快的成功提示 |
| 合成 | 字幕渲染到画面外，或与源视频中已烧录的文字重叠 |

中间那一行不是假设。它在编写本教程时真实发生过，并且骗过了当时已有的
五道关卡中的四道。见 [`reviews/04-qa-report.md`](reviews/04-qa-report.md)
发现 1。

> **贯穿整份教程、需要你始终记住的一句话：**
> **`✓ Done` 只是一个字符串。输出文件本身才是证据。**

这是教程 #2 的教训（`"PASS" 只是字符串，日志才是证据`）在另一个领域的
复现。这个模式是通用的 —— 正因如此，值得先在一个简单主题上学会它，
免得等到困难主题上才需要。

### 0.3 五道关卡

| 关卡 | 检查什么 | 可机械执行？ |
|---|---|---|
| **T1** | 转写确实产出了分段 | 是 |
| **T2** | 实际运行的翻译服务就是你指定的那个 | 是 |
| **T3** | 翻译过程中没有丢失或合并分段 | 是 |
| **T3b** | 翻译**确实发生了**（不是英文原样透传） | 是 |
| **T4** | 输出视频的分辨率与时长与源文件完全一致 | 是 |
| **T5** | 中文是忠实、地道的翻译 | **否 —— 需人工/智能体判断** |

T1-T4 以代码形式运行：
[`starter/scripts/run_gates.py`](starter/scripts/run_gates.py)。
T5 是一套由双语审阅者执行的流程：
[`docs/expertise_division.zh.md`](docs/expertise_division.zh.md) 第 4 节。

### 0.4 为什么有一道关卡无法自动化

gstack 的流程角色能数分段、比对时长、在配置文件里检索字段。
**但它们都无法读中文，判断译文是否承载了英文的原意。**
这是本项目唯一的专业能力缺口，Gate T5 的存在就是为了正面承认并封堵它，
而不是假装它不存在。

教程 #2 把这称为**双钥匙系统**（流程权威 vs 物理权威）。本教程是它的
轻量版：一位领域审阅者，其否决权只在一道关卡上生效。完整契约见
[`docs/expertise_division.zh.md`](docs/expertise_division.zh.md)。

### 0.5 循环论证陷阱（在你发明自己的检查方法之前先读这节）

假设你想验证译文质量。一个很诱人的想法是：用 OCR 识别成片中烧录的字幕，
再与你用来生成它的 `.srt` 比对。

**这个检查对"翻译保真度"毫无价值。** 它是拿输出和它自己比。它只能证明
合成步骤没有损坏文本（而这已经由 Gate T4 覆盖），完全无法说明中文是否是
英文音频的正确翻译。

`run_gates.py` 显式拒绝这种做法 —— 传入 `--ocr-check`，它会以退出码
**2（VOID，无效）** 退出，既不是 0 也不是 1。VOID 拥有独立的退出码，
就是为了让"关卡通过"和"关卡毫无意义"永远不会打印出相同的结果。

这正是教程 #2 的 LVS 循环论证教训的移植版。如果你只从本教程带走一个
可迁移的概念，请让它是这一个。

### 0.6 30 秒内看到真实结果，甚至不用先安装任何东西

[`starter/sample/`](starter/sample/) 提供了一个真实的、极短（约 12 秒）的
完整实例——源片段、经过校正的英文转写稿、中文译文，以及最终带字幕的输出，
全部已经用这套完整流程跑过一遍。`run_gates.py` 只需要 Python 和
FFmpeg——不需要 `videocaptioner` 本身——所以你现在就能验证一个真实结果：

```bash
python starter/scripts/run_gates.py \
    --source-video starter/sample/sample_clip.mp4 \
    --source-srt starter/sample/sample_clip.srt \
    --target-srt starter/sample/sample_clip_zh.srt \
    --output-video starter/sample/sample_clip_captioned.mp4 \
    --translator llm --target-language zh-Hans
```

预期结果：`T1`-`T4` 全部 `PASS`。这个样例的画面与配音都是专为本教程生成的
（不含任何第三方素材——具体做法与原因见
`starter/sample/README.md`），所以可以放心查看，本仓库公开发布也不涉及
版权问题。

### 检查点 0

- [ ] 我能不看文档说出流水线的四个阶段
- [ ] 我能说明为什么 `✓ Done` 不构成证据
- [ ] 我能解释为什么"OCR 对比自己的 srt"是循环检查
- [ ] 我知道哪一道关卡不是机械的，以及为什么

---

## 第 1 部分 —— 安装

完整分步说明，涵盖三大平台：
**[`starter/INSTALL.md`](starter/INSTALL.md)**

你要安装的东西概览：

| 组件 | 约束 | 用途 |
|---|---|---|
| Python | **>= 3.10，< 3.13** | `videocaptioner` 的硬性要求。3.13 尚不支持，安装前务必确认 |
| FFmpeg（`ffmpeg` + `ffprobe`） | 任意较新版本 | 音频提取、字幕烧录，以及每一道验证关卡 |
| `videocaptioner` | `pip install videocaptioner` | 流水线本体 |

然后执行：

```bash
videocaptioner --version
videocaptioner doctor
```

`doctor` 会一次性检查 Python、FFmpeg 和你的配置。关于
`dubbing.api_key` 的 `WARN` 是预期内的、无害的 —— 配音功能不在本教程范围内。

> **Windows 用户注意：** `starter/INSTALL.md` 第 6 节记录了一个 PowerShell
> 引号陷阱，如果你跳过它，它会在第 5 部分咬你一口。现在就读，不要等报错
> 出现才读。它是整份安装指南中价值最高的一段。

### 检查点 1

- [ ] `videocaptioner --version` 能打印版本号
- [ ] `videocaptioner doctor` 对 python、ffmpeg、ffprobe 均显示 `OK`
- [ ] 以上三项检查都是在**新开的**终端窗口中执行的
- [ ]（Windows）我已读过 INSTALL.md 第 6 节关于引号被剥除的说明

---

## 第 2 部分 —— 选择你的翻译服务（不要跳过，也不要照抄我的）

这是你与其他每一位读者之间最可能不同的一部分。

**请阅读：[`docs/choosing_a_translator.zh.md`](docs/choosing_a_translator.zh.md)。**

简要版：

| 选项 | 费用 | 需要密钥 | 英译中质量 |
|---|---|---|---|
| `llm` | 付费，约每小时语音几美分 | 需要 | 最好 —— 有上下文感知 |
| `bing` | 免费 | 不需要 | 机械直译（且上游目前已损坏 —— 见文档） |
| `google` | 免费 | 不需要 | 机械直译（且可能静默透传英文原文） |

三件会让人意外的事：

1. **`--translator` 的默认值是 `bing`**，不是 `llm`。省略该参数，你会
   悄无声息地用上 Bing。下文每条命令都显式写出该参数。
2. **用免费翻译器仍然需要 LLM 密钥** —— 除非你同时加上
   `--no-optimize --no-split`，因为"断句"和"优化"这两步无论你选哪个
   翻译服务都由 LLM 驱动。
3. **你的访问条件不等于我的。** 试点运行选用 DeepSeek，是因为它在香港
   可达且便宜。如果你在别处、在防火墙之后、使用院校的 OpenAI 配额，
   或者完全没有预算，正确答案都不一样。决策指南是按你的处境编排的。

### 在投入长视频之前，先探测你的访问条件

做一个两段的 `probe.srt` 并翻译它：

```bash
videocaptioner subtitle probe.srt --translator llm \
    --target-language zh-Hans --layout target-only -o probe_out.srt
```

然后**打开 `probe_out.srt` 亲眼看一下**。看到中文就说明可用。看到明确的
报错说明该选项对你不可用，换下一个。**看到英文却带着 `✓ Done` 提示，
说明发生了静默透传 —— 无论它声称什么，那个翻译器对你都是不工作的。**

这里花两分钟，后面省一小时。

### 检查点 2

- [ ] 我基于**自己的**访问条件选择了翻译服务，而不是照搬教程默认值
- [ ] 我跑了探测，并**亲眼确认**输出中是中文
- [ ] 我把选择（以及 `api_base`/`model`）记入了 `starter/versions.lock`

---

## 第 3 部分 —— 阶段 1-2：范围与拆解（`/plan-ceo-review`、`/spec`）

在碰视频之前，先锁定"完成"的定义。

本教程附带的实例，两份都是本仓库上的真实运行记录：
- [`reviews/01-ceo-review.md`](reviews/01-ceo-review.md) —— 在本教程自己的
  计划中找出三个阻塞问题，结论为 REVISE（需修订），修复后才升级为 PASS
- [`reviews/02-spec.md`](reviews/02-spec.md) —— W1-W10 工作拆解，并且它
  **上调**了 CEO 的时间估算，而不是默默接受

两个值得照搬的特性：

1. **每个工作项都指明由哪道关卡裁定。** 没有任何关卡能裁定的工作项，
   是愿望，不是任务。
2. **本角色无法回答的问题标记为"已转交"，而不是猜一个答案。** 两份评审
   都这样做。这就是"转交条款"在起作用。

### 检查点 3

- [ ] 我的范围说明写清了什么被**刻意排除**，而不只是包含什么
- [ ] 每个工作项都指明了它的关卡
- [ ] 任何需要双语判断的问题都被转交，而非猜测

---

## 第 4 部分 —— 阶段 3：转写与校正

### 4.1 转写

```bash
videocaptioner transcribe myclip.mp4 --asr bijian --language en -o myclip.srt
```

`bijian` 免费、无需配置，处理英文效果不错。其他源语言请使用
`--asr whisper-api` 并配合 `--whisper-api-key`。

记下输出中的分段数 —— 后续每一步都要用它来核对。

### 4.2 通读转写稿（所有人都想跳过的那一步）

**打开 `myclip.srt` 并通读。** ASR 会犯一些小错误：在英文阶段是两分钟就能
改好的问题，一旦放过去，就会变成翻译质量问题。

本教程试点运行中的真实案例，三处都是在这一步抓到的：

| ASR 写成 | 应为 |
|---|---|
| `ai` | `AI` |
| `home humanoid robots` | `humanoid robots` |
| `neural netells me` | `neural network tells me` |

只修改文本行。**不要改动分段序号和时间轴** —— Gate T3 会检查分段数未变。

### 检查点 4

- [ ] 转写稿已生成，分段数已记录
- [ ] 我通读了全文并修正了 ASR 错误
- [ ] 我编辑之后，分段数和时间轴保持不变

---

## 第 5 部分 —— 阶段 3（续）：翻译与合成

### 5.1 检查源视频是否已烧录字幕

在翻译**之前**做这件事 —— 它决定你是否需要做字幕位置调整。

```bash
ffmpeg -y -ss 30 -i myclip.mp4 -frames:v 1 -update 1 frame30.png
ffmpeg -y -ss 60 -i myclip.mp4 -frames:v 1 -update 1 frame60.png
```

在片子的不同位置抓 2-3 帧（字幕可能只在某些时段出现），然后看一看。

**如果发现已烧录的文字：** 它已经和像素融为一体。任何字幕工具都无法看见
或移除它 —— 对 `ffmpeg` 而言，它和人脸没有区别。你的选项是：找一份干净的
源导出、使用 AI 视频修复（复杂，常常发糊）、裁掉该区域，或者
**把中文字幕放到避开它的位置**（第 5.3 节）。试点的第一段视频有这个问题，
第二段没有。

### 5.2 翻译，仅输出中文

```bash
videocaptioner subtitle myclip.srt --translator llm \
    --target-language zh-Hans --layout target-only -o myclip_zh.srt
```

`--layout target-only` 产出只有中文、没有英文行的字幕。请直接用它；
默认值（`target-above`）会产出双语文件，而如果你在烧录**之后**才发现
自己只想要中文，就得重跑一遍合成。

紧接着执行：

```bash
videocaptioner config show     # Gate T2 —— 确认实际运行的是哪个服务
```

请在你关心的那条翻译命令之后**立刻**执行它。它报告的是配置的*当前*状态，
而非逐次调用的历史记录，所以如果你连续跑好几次翻译再来检查，它就失去意义了
（见 [`reviews/03-eng-review.md`](reviews/03-eng-review.md) 的非阻塞说明）。

### 5.3 调整字幕位置（仅当第 5.1 节发现冲突时）

```bash
videocaptioner style     # 列出预设及其字段
```

字段包括：`font_name`、`font_size`、`primary_color`、`outline_color`、
`outline_width`、`bold`、`spacing`、`margin_bottom`。调大 `margin_bottom`
可把中文字幕抬高，避开画面底部已有的文字。

### 5.4 合成

```bash
videocaptioner synthesize myclip.mp4 -s myclip_zh.srt \
    --subtitle-mode hard --style default -o myclip_captioned_v1.mp4
```

`hard` 把字幕烧进画面；`soft` 则添加一条可开关的字幕轨。输出文件名加上
版本后缀（`_v1`、`_v2`），这样你可以对比不同尝试，而不是覆盖掉它们。

**不想新建预设、只想改样式时**（例如把字号调大 —— 默认的 42 在 1080 宽的
画面上偏小，54-56 效果较好）：

```bash
videocaptioner synthesize myclip.mp4 -s myclip_zh.srt --subtitle-mode hard \
    --style default --style-override '{"font_size":56}' -o myclip_captioned_v2.mp4
```

> **Windows PowerShell 用户 —— 上面这条命令照抄会失败。** PowerShell 会在
> 参数送达程序之前剥掉双引号，于是你会看到
> `Invalid --style-override JSON: Expecting property name enclosed in double
> quotes`，尽管命令在屏幕上看起来完全正确。请在单引号字符串内给每个双引号
> 加反斜杠转义：
> ```powershell
> --style-override '{\"font_size\":56}'
> ```
> 验证方法：`python -c "import sys; print(sys.argv)" '{\"font_size\":56}'`
> —— 它应当打印 `['{"font_size":56}']`。完整解释见
> [`starter/INSTALL.md`](starter/INSTALL.md) 第 6 节。

### 检查点 5

- [ ] 我检查了源视频的 2-3 帧，确认是否有已烧录字幕
- [ ] 翻译使用了 `--layout target-only` 和我选定的翻译服务
- [ ] 翻译之后我立刻运行了 `config show`
- [ ] 输出视频带有版本后缀

---

## 第 6 部分 —— 阶段 4：验证（这才是本教程的要点）

### 6.1 运行机械关卡

```bash
python starter/scripts/run_gates.py \
    --source-video   myclip.mp4 \
    --source-srt     myclip.srt \
    --target-srt     myclip_zh.srt \
    --output-video   myclip_captioned_v2.mp4 \
    --translator     llm \
    --target-language zh-Hans
```

一次正常运行的预期输出：

```
T1 PASS — myclip.srt: 32 segments
T2 PASS — translate.service = llm
T3 PASS — 32 segments in both source and target
T3b PASS — target is genuinely translated, not source passthrough
T4 PASS — 1080x596, 89.131s (source) vs 89.131s (output)
T5 NOT AUTO-VERIFIED — run docs/expertise_division.md section 4 by hand
```

**退出码：**

| 码 | 含义 |
|---|---|
| `0` | T1-T4 全部 PASS |
| `1` | 某道机械关卡 FAILED |
| `2` | **VOID** —— 某项检查属于自我指涉，已被拒绝执行 |
| `3` | 环境错误（工具或文件缺失） |

请让你的自动化流程在 `!= 0` 时失败，并对 `== 2` **单独告警**。VOID 不是
一个"重试一下"的失败 —— 它意味着你尝试的这项检查，根本无法证明你想证明的
东西。

### 6.2 人工执行 Gate T5

脚本打印 `T5 NOT AUTO-VERIFIED`，它是认真的。请按
[`docs/expertise_division.zh.md`](docs/expertise_division.zh.md) 第 4 节执行：

**输入：** 英文 `.srt` 和中文 `.srt` —— **绝不是视频**。
**抽样：** 第 1-5 段、约 50% 处的一段，以及最后 5 段。
**每段问四个问题：** 是否保全原意？是否地道而非死译？有无凭空增补或
遗漏？专有名词与习语是否正确？

结论为 PASS，或**PASS-WITH-FLAG**（带标记通过）并注明具体段落。带标记的
运行在每一处标记被人工处理之前，都不算完成。

### 6.3 看一帧画面

关卡能证明文件在结构上是正确的。只有你的眼睛能证明它**可读**。

```bash
ffmpeg -y -ss 30 -i myclip_captioned_v2.mp4 -frames:v 1 -update 1 check30.png
```

检查：文字在背景上是否清晰、有没有在画面边缘被切掉、是否与源视频已烧录的
文字重叠、字号是否舒适。

### 检查点 6

- [ ] `run_gates.py` 以 0 退出
- [ ] Gate T5 是针对 **`.srt` 文件对**执行的，不是针对视频
- [ ] 每一处 T5 标记都有书面处理结论
- [ ] 至少目视检查了一帧输出画面

---

## 第 7 部分 —— 阶段 5：交付

- 证据包：关卡输出、`config show` 摘录、填好的
  `starter/versions.lock`，以及你检查过的那一帧画面
- 发布说明要写明**已知缺口**，而不只是功能
- 任何派生文档都从 Markdown 重新生成；绝不手工编辑生成出来的二进制文件

### 检查点 7

- [ ] 证据包已整理
- [ ] 已知缺口已书面写明
- [ ] `versions.lock` 已填好版本、服务商、模型和运行日期

---

## 第 8 部分 —— 疑难排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `--style-override` 报 JSON 错误，但命令看起来没问题 | PowerShell 剥掉了引号 | 反斜杠转义：`'{\"font_size\":56}'` |
| 翻译"成功"但输出是英文 | 免费翻译器吞掉了限流错误 | Gate T3b 能抓到。换翻译服务 —— 见 `docs/choosing_a_translator.zh.md` |
| `Failed to init Bing session: 404` | 上游端点已变更 | 改用 `llm` 或 `google`；见翻译服务指南 |
| Gate T1 数出的分段比预期少一个 | 首行有 UTF-8 BOM | `run_gates.py` 已修复（用 `utf-8-sig` 读取）。若你自己写了工具，请同样用 `utf-8-sig` |
| 中文字幕与画面上已有文字重叠 | 源视频有已烧录字幕 | 见第 5.1 节 —— 调大 `margin_bottom`；源文字无法移除 |
| `pip install` 成功后仍提示 `videocaptioner: command not found` | Scripts 目录不在 PATH 中 | 执行 `python -c "import sysconfig; print(sysconfig.get_path('scripts'))"`，把结果加入 PATH |
| 在 PowerShell 里中文显示为乱码 | 是控制台代码页问题，不是文件问题 | 用支持 UTF-8 的编辑器打开；文件本身没问题 |
| `pip install` 构建依赖失败 | Python 版本不在 `>=3.10,<3.13` 区间 | 安装 3.12；不要跟 3.13 解释器硬碰 |

---

## 第 9 部分 —— 值得保留的几条纪律

五个可迁移到任何流水线的习惯，不限于本教程。

1. **检查输出，而不是退出码。** 本教程"坑位清单"里的每一个失败，都至少
   曾报告过一次成功。
2. **绝不用产物自己来验证自己。** OCR 对比自己的 srt、用从待测 GDS 导出的
   网表去跑 LVS —— 同一个错误，不同领域。
3. **给"无意义"一个独立信号。** VOID 拥有独立退出码，就是为了它永远不会
   被误认为 PASS。
4. **明确点出你封不住的缺口。** Gate T5 没有自动化，文档就直说，而不是
   暗示覆盖是完整的。
5. **读者的环境不是你的环境。** 第 2 部分之所以存在，是因为初稿把作者的
   API 配置当成了普适规则往下传。

---

## 附录 A —— 命令速查

```bash
# 安装检查
videocaptioner --version
videocaptioner doctor
videocaptioner config show

# 配置 LLM 翻译服务
videocaptioner config set llm.api_key  "sk-..."
videocaptioner config set llm.api_base "https://api.deepseek.com"
videocaptioner config set llm.model    "deepseek-chat"

# 流水线
videocaptioner transcribe clip.mp4 --asr bijian --language en -o clip.srt
videocaptioner subtitle clip.srt --translator llm --target-language zh-Hans \
    --layout target-only -o clip_zh.srt
videocaptioner synthesize clip.mp4 -s clip_zh.srt --subtitle-mode hard \
    --style default -o clip_captioned_v1.mp4

# 验证
python starter/scripts/run_gates.py --source-video clip.mp4 \
    --source-srt clip.srt --target-srt clip_zh.srt \
    --output-video clip_captioned_v1.mp4 --translator llm

# 抓帧
ffmpeg -y -ss 30 -i clip.mp4 -frames:v 1 -update 1 frame.png
```

## 附录 B —— 术语表

| 术语 | 含义 |
|---|---|
| **ASR** | 自动语音识别 —— 音频转文字 |
| **SRT** | SubRip 字幕格式：序号、时间区间、文本 |
| **硬字幕** | 烧录进视频像素，无法关闭 |
| **软字幕** | 独立轨道，播放器可开关 |
| **透传（passthrough）** | 翻译器原样返回源文本，却声称成功 |
| **VOID（无效）** | 检查确实跑了，但什么也没证明 —— 区别于通过或失败 |
| **循环检查** | 用源自产物自身的东西去验证该产物 |
| **BCP 47** | 语言标签标准。`zh-Hans` 表示简体中文 |

## 附录 C —— 完成的定义

- [ ] Gates T1-T4 全部 PASS（`run_gates.py` 以 0 退出）
- [ ] Gate T5 已审阅，无未处理标记
- [ ] 已捕获 `config show` 证据，证明运行的是预期的翻译服务
- [ ] 已验证输出的分辨率与时长与源文件完全一致
- [ ] 至少目视检查了一帧画面
- [ ] 已检查源视频是否有预先烧录的字幕
- [ ] `versions.lock` 已填写
- [ ] 已知缺口已书面写明

达不到以上任何一条，就还是草稿。

---

*许可：文字部分 CC BY 4.0，代码部分 Apache-2.0 —— Copyright 2026 Prof. Yi-Kuen Lee。*
