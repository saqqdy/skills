# Kafka Log Analyzer 使用指南

分析 Java 服务的 Kafka 日志，提取关键事件、检测异常模式、生成诊断报告，并支持源码联动修复。

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **双格式自动检测** | 自动识别纯文本和 JSON 日志格式，无需手动指定 |
| **P0-P3 优先级分级** | 基于错误类型、频率和影响自动判定，快速聚焦关键问题 |
| **7 种异常检测器** | 错误率突增 / 消费积压 / Rebalance 风暴 / Leader 不稳定 / 副本同步延迟 / 序列化异常 / 错误率趋势上升 |
| **时间线分析** | 按分钟/小时统计事件分布，定位错误集中时段 |
| **实时监控** | `--watch` 模式实时追踪日志变化，适合排查正在发生的问题 |
| **源码联动** | 引导 Claude 搜索项目中的 Kafka 配置和 Producer/Consumer 类，生成代码级修复方案 |
| **完整诊断报告** | 整合统计数据 + 异常检测结果，输出含优先级排序和修复建议的 Markdown 报告 |

---

## 工作原理

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  日志预处理    │────→│  事件提取+分级  │────→│  异常检测      │
│  auto detect  │     │  P0 ~ P3      │     │  7 detectors  │
└───────────────┘     └───────────────┘     └───────────────┘
                                                    │
                              ┌─────────────────────┤
                              │                     │
                              ▼                     ▼
                     ┌───────────────┐     ┌───────────────┐
                     │  诊断报告生成  │     │  源码联动修复  │
                     │  Markdown/JSON │     │  配置+代码diff │
                     └───────────────┘     └───────────────┘
```

---

## 使用方法

### 方式 1：直接粘贴日志询问 Claude

```
分析这段 Kafka 日志：

[2026-01-15 10:23:45] INFO  [kafka-producer-thread] Successfully sent record to topic orders
[2026-01-15 10:23:46] ERROR [kafka-producer-thread] Failed to send record to topic payments: TimeoutException
[2026-01-15 10:23:47] WARN  [kafka-producer-thread] BufferExhaustedException: Buffer is full
```

### 方式 2：指定分析重点

```
分析以下 Kafka Consumer 日志，重点关注消费积压和 Rebalance 问题：

[日志内容...]
```

### 方式 3：请求特定诊断

```
这段日志显示 Producer 发送超时，请提供修复建议：

[日志内容...]
```

### 方式 4：时间线分析

```
分析以下 Kafka 日志的时间分布，找出错误集中的时间段：

[日志内容...]
```

### 方式 5：源码联动修复

```
这段日志显示 orders 这个 topic 的 Producer 频繁超时，
请搜索项目中的 Kafka 配置和 OrderProducer 类，给出代码层面的修复方案：

[日志内容...]
```

---

## 辅助脚本

### parse_kafka_log.py — 日志解析

```bash
# 基础解析（自动检测格式）
python scripts/parse_kafka_log.py kafka.log

# 指定格式
python scripts/parse_kafka_log.py --format json kafka.log

# 解析目录下所有 .log 文件
python scripts/parse_kafka_log.py ./logs/

# 时间线分布（按分钟）
python scripts/parse_kafka_log.py kafka.log --timeline

# 时间线分布（按小时）
python scripts/parse_kafka_log.py kafka.log --timeline --timeline-window 1h

# 输出到文件
python scripts/parse_kafka_log.py kafka.log -o stats.json
```

### 实时监控模式

```bash
# 实时追踪日志变化（每秒轮询）
python scripts/parse_kafka_log.py kafka.log --watch

# 调整轮询间隔
python scripts/parse_kafka_log.py kafka.log --watch --watch-interval 2.0
```

输出示例：

```
监控 kafka.log (格式: text)，Ctrl+C 退出...
------------------------------------------------------------
🔴 2026-01-15 10:24:15 ERROR [orders] send_failure: Failed to send record to topic orders: TimeoutException
🟡 2026-01-15 10:24:16 WARN  [orders] consumer_lag: lag exceeded threshold (5000 messages)
🟢 2026-01-15 10:24:20 INFO  [payments] send_success: Successfully sent record to topic payments partition 0 offset 99
```

### detect_anomalies.py — 异常检测

```bash
# 基础检测
python scripts/detect_anomalies.py events.json

# 自定义阈值
python scripts/detect_anomalies.py events.json --lag-threshold 5000
python scripts/detect_anomalies.py events.json --rebalance-threshold 5

# 输出到文件
python scripts/detect_anomalies.py events.json -o anomalies.json
```

### generate_report.py — 报告生成

```bash
# 从分别的 JSON 文件生成
python scripts/generate_report.py --stats stats.json --anomalies anomalies.json

# 从目录批量读取
python scripts/generate_report.py --input-dir ./analysis_output

# 指定分析周期
python scripts/generate_report.py --input-dir ./analysis_output --period "24h"

# JSON 格式输出
python scripts/generate_report.py --input-dir ./analysis_output --format json
```

---

## 支持的事件类型

| 事件类型 | 日志特征 | 提取字段 |
|----------|----------|----------|
| `send_success` | `Successfully sent record to topic` | topic, partition, offset |
| `send_failure` | `Failed to send record` | topic, error |
| `buffer_exhausted` | `BufferExhaustedException` | block_ms |
| `consumer_lag` | `lag exceeded threshold` | offset_lag |
| `rebalance` | `Revoking previously assigned` | - |
| `commit_failure` | `CommitFailedException` | - |
| `leader_change` | `leader changed from` | topic, partition |
| `offset_out_of_range` | `OffsetOutOfRange` | - |
| `serialization_error` | `SerializationException` | - |
| `network_error` | `NetworkException` | - |
| `auth_error` | `TopicAuthorizationException` | - |

---

## 支持的日志格式

### 纯文本

```
[2026-01-15 10:23:45] INFO  [kafka-producer-thread] Successfully sent record to topic orders partition 5 offset 12345
```

### JSON

```json
{
  "timestamp": "2026-01-15T10:23:45Z",
  "level": "INFO",
  "message": "Successfully sent record to topic orders",
  "topic": "orders",
  "traceId": "abc-123"
}
```

自动检测逻辑：首行以 `{` 或 `[` 开头则为 JSON 格式。

---

## 优先级分级

| 优先级 | 条件 | 行动 |
|--------|------|------|
| 🔴 **P0** | `ProducerFenced` / 消息丢失 / 数据损坏 / ERROR >= 100次 | 立即修复 |
| 🟠 **P1** | ERROR >= 10次 / 消费积压 / 提交失败 | 当天处理 |
| 🟡 **P2** | WARN >= 5次 / 偶发 ERROR / 单次 Rebalance | 排入迭代 |
| ⚪ **P3** | INFO / 低频 WARN / 正常 Leader 切换 | 观察或忽略 |

---

## 异常检测器详情

| 检测器 | 检测目标 | 严重度规则 |
|--------|----------|-----------|
| `error_rate_spike` | 错误率突增 | >2% medium, >5% high, >10% critical |
| `consumer_lag` | 消费积压 | >阈值 high, >10×阈值 critical |
| `rebalance_storm` | 频繁 Rebalance | >=3次 high, >10次 critical |
| `leader_instability` | Leader 频繁切换 | >=3次 medium, >5次 high |
| `replica_sync_lag` | 副本同步延迟 | 出现 medium, >5次 high |
| `serialization_errors` | 序列化异常聚类 | >=3次 medium, >10次 high |
| `error_rate_trend_up` | 错误率趋势上升 | 翻倍且后半段 >5% high |

---

## 参考文档

| 文档 | 内容 |
|------|------|
| [kafka-patterns.md](references/kafka-patterns.md) | 常见日志模式及解决方案 |
| [error-codes.md](references/error-codes.md) | Kafka 错误码参考表 |
| [tuning-guide.md](references/tuning-guide.md) | 性能调优配置指南 |

---

## 文件结构

```
kafka-log-analyzer/
├── SKILL.md                 # 主指令文件（5 阶段分析流水线）
├── README.md                # 本文档
├── references/
│   ├── kafka-patterns.md    # 常见日志模式库
│   ├── error-codes.md       # Kafka 错误码参考
│   └── tuning-guide.md      # 性能调优指南
├── scripts/
│   ├── parse_kafka_log.py   # 日志解析（支持 --timeline / --watch）
│   ├── detect_anomalies.py  # 异常检测（7 种检测器）
│   └── generate_report.py   # 分析报告生成
└── evals/
    └── evals.json           # 9 个测试用例
```

---

## 许可证

Apache License 2.0 © 2026 saqqdy
