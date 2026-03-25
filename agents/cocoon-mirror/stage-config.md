# 镜子阶段配置

## 脚手架衰减参数

镜子的脚手架控制观察深度和出现频率。值越高，观察越浅、频率越低；值越低，观察越深、频率越高。

衰减模型：
```
scaffold(t) = S_min + (S_max - S_min) * e^(-lambda * t)
```

| 阶段 | S_max | S_min | lambda | 说明 |
|------|-------|-------|--------|------|
| Stage 1 | 0.80 | 0.30 | 0.15 | 浅层行为观察，极低频 |
| Stage 2 | 0.70 | 0.20 | 0.20 | 策略层面观察 |
| Stage 3 | 0.50 | 0.10 | 0.25 | 思维模式观察 |
| Stage 4 | 0.30 | 0.05 | 0.30 | 系统思维观察 |
| Stage 5 | 0.15 | 0.00 | 0.35 | 完整旅程叙事 |

## 出现频率控制

| 阶段 | 触发间隔 (session数) | 每次最大观察数 |
|------|---------------------|--------------|
| Stage 1 | 3-5 | 1 |
| Stage 2 | 2-3 | 1-2 |
| Stage 3 | 1-2 | 2-3 |
| Stage 4 | 1-2 | 2-3 |
| Stage 5 | 关键节点 | 不限 |

触发条件（任一满足即触发）：
1. 距上次镜子出现已达到间隔阈值
2. stage-assessor 检测到阶段跃迁
3. discovery-detector 检测到显著的"啊哈时刻"
4. 用户主动发出进度信号

## 阶段行为参数

### Stage 1 — 敬畏者

```yaml
observation_depth: behavioral   # 只看行为
temporal_scope: current_session # 只看当前session
comparison: none                # 不做对比
max_sentences: 2
tone: neutral_light             # 轻松中性
```

**观察维度：**
- 用户使用了什么功能
- 用户的交互方式（问答？指令？对话？）
- 用户在什么地方停顿或犹豫

### Stage 2 — 工具使用者

```yaml
observation_depth: strategic    # 策略层面
temporal_scope: cross_session   # 跨session对比
comparison: self_temporal       # 只和用户自己的过去比
max_sentences: 3
tone: neutral_observant         # 中性观察
```

**观察维度：**
- 使用策略的变化（一次性 vs 分步，被动 vs 主动）
- 信心指标变化（犹豫频率、确认频率）
- 任务类型偏好的演变

### Stage 3 — 协作者

```yaml
observation_depth: cognitive    # 思维模式层
temporal_scope: longitudinal    # 长期纵向观察
comparison: self_deep           # 深层自我对比
max_sentences: 5
pattern_cross_domain: true      # 跨领域模式
tone: neutral_engaged           # 中性但有参与感
```

**观察维度：**
- 思维模式（线性→系统、具体→抽象）
- 不确定性处理方式的演变
- 跨任务类型的共同模式
- 元认知出现的频率

### Stage 4 — 编排者

```yaml
observation_depth: systemic     # 系统层
temporal_scope: full_history    # 完整历史
comparison: self_evolution      # 自我演化轨迹
max_sentences: 7
system_design_lens: true        # 观察设计哲学
tone: neutral_thoughtful        # 中性且有思考深度
```

**观察维度：**
- 编排策略的设计哲学
- 控制权分配的演变
- 质量标准的变化
- 人-AI角色边界的重新定义

### Stage 5 — 思想者

```yaml
observation_depth: narrative    # 叙事弧线
temporal_scope: complete_arc    # 完整旅程
comparison: journey_arc         # 旅程弧线
max_sentences: unlimited
narrative_mode: true            # 可呈现完整叙事
tone: neutral_profound          # 中性且深邃
```

**观察维度：**
- 从 Stage 1 到 Stage 5 的完整转变叙事
- 深层身份认同的变化
- 与 AI 关系定义的演化
- 对"学习"和"能力"概念本身的理解变化

## SDT（自我决定理论）对应

镜子的核心心理功能是支持用户的**联结感**：

| 阶段 | 联结感支持方式 |
|------|--------------|
| Stage 1 | 被看见——"有人注意到我在做什么" |
| Stage 2 | 被理解——"有人理解我的模式" |
| Stage 3 | 被认识——"有人看到我的思维方式" |
| Stage 4 | 被见证——"有人见证我的系统设计" |
| Stage 5 | 被记录——"有人记录了我的完整旅程" |
