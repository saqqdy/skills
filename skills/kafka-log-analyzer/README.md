# Kafka Log Analyzer 使用指南

## 简介

`kafka-log-analyzer` 是一个用于分析 Java 服务 Kafka 日志的 Claude Code Skill，提供智能诊断和修复建议。

### 核心特性

| 特性 | 说明 |
|------|------|
| **多格式支持** | 自动识别 JSON 和纯文本日志格式 |
| **事件提取** | 识别 Producer/Consumer/Broker 事件类型 |
| **异常检测** | 检测错误率突增、消费积压、频繁 Rebalance 等 |
| **智能诊断** | 提供根因分析和配置修复建议 |
| **TraceID 支持** | 解析 JSON 日志中的 traceId 字段便于追踪 |
| **报告生成** | 输出 Markdown 或 JSON 格式分析报告 |

---

## 使用方法

### 方式 1：直接询问 Claude

```
分析这段 Kafka 日志：

[2026-01-15 10:23:45] INFO  [kafka-producer-thread] Successfully sent record to topic orders
[2026-01-15 10:23:46] ERROR [kafka-producer-thread] Failed to send: TimeoutException
```

### 方式 2：指定分析维度

```
分析以下 Kafka Consumer 日志，重点关注消费积压问题：

[日志内容...]
```

### 方式 3：请求诊断建议

```
这段日志显示 Producer 发送超时，请提供修复建议：

[日志内容...]
```

---

## 辅助脚本

### parse_kafka_log.py - 日志解析

```bash
python scripts/parse_kafka_log.py kafka.log
python scripts/parse_kafka_log.py --format json kafka.log
python scripts/parse_kafka_log.py kafka.log -o output.json
```

### detect_anomalies.py - 异常检测

```bash
python scripts/detect_anomalies.py events.json
python scripts/detect_anomalies.py --lag-threshold 5000 events.json -o anomalies.json
```

### generate_report.py - 报告生成

```bash
python scripts/generate_report.py stats.json anomalies.json
python scripts/generate_report.py stats.json anomalies.json --format json -o report.md
```

---

## 支持的事件类型

| 事件类型 | 日志特征 | 提取字段 |
|----------|----------|----------|
| `send_success` | `Successfully sent record to topic` | topic, partition, offset |
| `send_failure` | `Failed to send record` | topic, error |
| `buffer_exhausted` | `BufferExhaustedException` | block_ms |
| `consumer_lag` | `lag exceeded threshold` | offset_lag |
| `rebalance_start` | `Revoking previously assigned` | - |
| `commit_failure` | `CommitFailedException` | - |
| `leader_change` | `leader changed from` | topic, partition |

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

---

## 诊断能力

| 问题类型 | 检测逻辑 | 建议配置 |
|----------|----------|----------|
| 发送超时 | TimeoutException | `request.timeout.ms=30000` |
| 缓冲区满 | BufferExhaustedException | `buffer.memory=64MB` |
| 消费积压 | lag > 10000 | 增加 Consumer 实例 |
| 频繁 Rebalance | rebalance > 5 次 | `session.timeout.ms=60000` |
| 错误率突增 | error_rate > 5% | 检查网络/Broker |

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
├── SKILL.md
├── README.md
├── references/
│   ├── kafka-patterns.md
│   ├── error-codes.md
│   └── tuning-guide.md
├── scripts/
│   ├── parse_kafka_log.py
│   ├── detect_anomalies.py
│   └── generate_report.py
└── evals/
    └── evals.json
```
