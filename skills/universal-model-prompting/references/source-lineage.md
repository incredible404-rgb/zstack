# 来源谱系与泛化边界

> 检索日期：2026-08-21（Asia/Shanghai）  
> 官方模型页：https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6#prompting-best-practices  
> 官方专用指南：https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6.md

本文件说明每条通用原则从哪里来、如何改写，以及哪里停止泛化。原始 Markdown 快照保存在项目 `sources/` 目录。

| 官方章节 | 提炼后的通用原则 | 分类 | 不应泛化的部分 |
|---|---|---|---|
| Simplify prompts first / Favor leaner prompts | 去重、删无关工具、一次改一组并复测；默认保持单一权威表述 | Conditional | 10–15% 分数、41–66% token、33–67% 成本来自 OpenAI 内部 GPT-5.6 coding-agent 样本；GPT-4.1 官方长上下文指南却建议关键指令首尾各放一次，因此不能把“只说一次”写成跨模型定律 |
| Outcome-first prompts and stopping conditions | 先写结果、完成标准与停止规则；判断题用条件规则 | Conditional | 较弱模型或严格合规流程可能需要更多过程脚手架 |
| Personality, collaboration, and response length | 人格与协作分层；长度写内容保留优先级；语气写可观察选择 | Core | GPT-5.6 默认更简短以及 `text.verbosity` 属于该模型/API |
| Define autonomy and approval boundaries | 按影响半径区分读取、本地可逆改动与高风险副作用 | Conditional | 只在 Agent 能采取行动时完整适用；具体权限由宿主、组织政策和用户授权决定 |
| Tool routing | 工具少而相关；独立读取并行，依赖动作串行；空/部分结果有有限回退 | Conditional | 只在工具可用时适用；并行能力、调用语义和错误字段取决于运行时 |
| Programmatic Tool Calling | 确定性批量归并与逐步语义判断分开；中间输出和最终回答都验收 | Conditional | `programmatic_tool_calling`、`allowed_callers`、`program_output` 是 OpenAI 实现 |
| Grounding, citations, and retrieval budgets | 定义承重主张、证据门槛、检索预算、冲突和缺证行为 | Conditional | 用于有事实依据要求的任务；工具、引用格式和来源范围取决于宿主 |
| Long-running workflows and state | 更新只在主要阶段；里程碑压缩；状态稳定时才复用 | Conditional | `previous_response_id`、phase value、`reasoning.context` 和 prompt caching 是 API 细节 |
| Reasoning effort | 先修合同、依赖和验证，再按评测调整计算投入 | Conditional | 只有目标运行时具备对应计算旋钮时才直接适用；档位名和默认值属于 GPT-5.6 |
| Frontend and visual tasks | 保留既有设计系统和状态；渲染后检查；空间任务按精度与成本选输入 | Conditional | GPT-5.6 前端能力声明和 `original/auto` image detail 属于 OpenAI 模型/API |
| Check work before finishing | 给出与产物匹配的可执行验证，不能运行时说明缺口 | Core | 具体测试命令、渲染工具和可访问环境取决于宿主 |
| Suggested prompt structure | Role、Personality、Goal、Success、Constraints、Tools、Output、Stop 是复杂提示的起点 | Core | 不应变成所有任务必填的固定表格 |
| Prompt migration workflow | 保留基线、一次改一层、以真实轨迹修复、保持回滚 | Core | 任何单一模型上的最优提示不能直接代表其他模型 |

## 跨模型反证与边界核验

为了避免把 GPT-5.6 的版本口味写成普遍规律，额外读取了两类一手材料：

- [OpenAI GPT-4.1 Prompting Guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide) 明确写道，长上下文里把关键指令放在材料开头和结尾，效果可优于只放一处。这与 GPT-5.6 的去重倾向构成条件差异，说明重复与位置必须按目标模型和真实评测决定。
- [Anthropic Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) 强调清楚、直接、上下文充分，并在顺序或完整性重要时使用步骤；[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) 同时主张“足以完整描述预期行为的最小信息集”，其中 minimal 不等于 short。这支持“精简但不删合同”的边界。

这些对照没有证明一份提示能在所有模型上同样最优。它们只支持本 Skill 采用“可移植核心 + 能力画像 + 代表性 eval”的结构。

## 本 Skill 增加的综合推论

以下内容不是官方原句，而是根据多节指南与 Agent 运行经验重编排：

1. **五层提示架构**：平台运行时、可移植核心、人格、单次任务、能力适配。
2. **人格和任务能力分离**：人格负责取舍与声音，工具、权限和触发器留给运行时。
3. **能力协商表**：先写设计意图，再寻找原生字段与文本降级。
4. **质量门**：同时检查输出、证据、副作用、中间结构和最终回答。

这些推论应当由实际模型评测继续修正，不能因被写进 Skill 就视作永恒规则。
