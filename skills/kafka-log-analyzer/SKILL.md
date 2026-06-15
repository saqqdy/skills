---
name: kafka-log-analyzer
description: 分析 Java 服务的 Kafka 日志，提取关键事件、检测异常模式、生成诊断报告。当用户需要排查 Kafka 消息问题、分析 Producer/Consumer 日志、检测消息积压时触发。
metadata:
  author: saqqdy
  version: "2026.06.15"
---

# Kafka 日志分析器

分析 Java 服务在 Kafka 上产生的日志，提供智能诊断和修复建议。

## 分析流程

### 1. 日志预处理

识别日志格式，提取关键字段：

| 字段 | 说明 | 示例 |
|------|------|------|
| `timestamp` | 时间戳 | `2026-01-15 10:23:45` |
| `level` | 日志级别 | `INFO`, `WARN`, `ERROR` |
| `thread` | 线程名 | `kafka-producer-network-thread` |
| `message` | 日志消息 | `Successfully sent record...` |

### 2. 事件提取

识别 Kafka 相关事件类型：

| 事件类型 | 说明 | 日志特征 |
|----------|------|----------|
| `send_success` | 发送成功 | `Successfully sent record to topic` |
| `send_failure` | 发送失败 | `Failed to send record` |
| `consumer_lag` | 消费积压 | `lag exceeded threshold` |
| `rebalance` | 重平衡 | `Consumer group.*rebalance` |
| `commit` | 提交偏移量 | `Committing offsets` |
| `fetch` | 拉取消息 | `Fetching from topic` |

### 3. 异常检测

聚类错误日志，识别重复模式：

- **网络类**：超时、连接拒绝、断开
- **权限类**：认证失败、授权拒绝
- **资源类**：缓冲区满、内存不足
- **数据类**：序列化失败、格式错误

### 4. 诊断生成

提供根因分析和修复建议：

```
问题: Producer 发送超时
原因: 网络延迟或 Broker 负载高
建议:
  1. 检查网络连通性: ping <broker-host>
  2. 调整超时配置: request.timeout.ms=30000
  3. 监控 Broker 指标: JMX kafka.server:type=BrokerTopicMetrics
```

## 日志格式识别

### Kafka Producer 日志

```
[2026-01-15 10:23:45] INFO  [kafka-producer-network-thread | producer-1] 
  Successfully sent record to topic orders partition 5 offset 12345

[2026-01-15 10:23:46] WARN  [kafka-producer-network-thread | producer-1] 
  BufferExhaustedException: Buffer is full, blocking for 1000ms

[2026-01-15 10:23:47] ERROR [kafka-producer-network-thread | producer-1] 
  Failed to send record to topic payments: TimeoutException
```

### Kafka Consumer 日志

```
[2026-01-15 10:23:48] INFO  [kafka-consumer-thread] 
  Consumer group order-processor: assigned partitions [orders-0, orders-1]

[2026-01-15 10:23:49] WARN  [kafka-consumer-thread] 
  Consumer group order-processor: lag exceeded threshold (5000 messages)

[2026-01-15 10:23:50] ERROR [kafka-consumer-thread] 
  CommitFailedException: Commit cannot be completed due to group rebalance
```

### Kafka Broker 日志

```
[2026-01-15 10:23:51] INFO  [ReplicaManager] 
  Partition orders-5: leader changed from 1 to 2

[2026-01-15 10:23:52] WARN  [ReplicaFetcherThread] 
  Replica not available for partition orders-5

[2026-01-15 10:23:53] ERROR [KafkaApi] 
  NotLeaderForPartitionException: Leader not local for partition orders-5
```

## 分析输出格式

### 事件对象

```json
{
  "event_type": "send_success",
  "timestamp": "2026-01-15 10:23:45",
  "level": "INFO",
  "thread": "kafka-producer-network-thread | producer-1",
  "topic": "orders",
  "partition": 5,
  "offset": 12345,
  "latency_ms": 15,
  "raw_message": "Successfully sent record to topic orders partition 5 offset 12345"
}
```

### 异常对象

```json
{
  "event_type": "send_failure",
  "timestamp": "2026-01-15 10:23:47",
  "level": "ERROR",
  "thread": "kafka-producer-network-thread | producer-1",
  "topic": "payments",
  "error_type": "TimeoutException",
  "error_message": "Request timed out after 30000ms",
  "suggestion": "检查网络连通性，调整 request.timeout.ms 配置"
}
```

### 统计报告

```json
{
  "summary": {
    "total_events": 10000,
    "success_rate": 0.98,
    "error_count": 200,
    "avg_latency_ms": 25,
    "p99_latency_ms": 150
  },
  "by_type": {
    "send_success": 8500,
    "send_failure": 200,
    "consumer_lag": 100,
    "rebalance": 50
  },
  "by_topic": {
    "orders": 5000,
    "payments": 3000,
    "notifications": 2000
  },
  "top_errors": [
    {
      "error_type": "TimeoutException",
      "count": 100,
      "topic": "payments"
    }
  ]
}
```

## 常见问题诊断

### Producer 问题

| 问题 | 日志特征 | 原因 | 解决方案 |
|------|----------|------|----------|
| 发送超时 | `TimeoutException` | 网络延迟或 Broker 负载高 | 调整 `request.timeout.ms` |
| 缓冲区满 | `BufferExhaustedException` | 发送速度超过网络速度 | 增加 `buffer.memory` |
| 权限拒绝 | `TopicAuthorizationException` | ACL 配置问题 | 检查 ACL 配置 |
| 序列化失败 | `SerializationException` | Schema 不匹配 | 检查 Serializer 配置 |

### Consumer 问题

| 问题 | 日志特征 | 原因 | 解决方案 |
|------|----------|------|----------|
| 提交失败 | `CommitFailedException` | Rebalance 中断提交 | 减少 `max.poll.interval.ms` |
| 偏移量越界 | `OffsetOutOfRange` | 消息过期被删除 | 调整 `auto.offset.reset` |
| Rebalance 频繁 | `Revoking previously assigned partitions` | 心跳超时或处理慢 | 增加 `session.timeout.ms` |
| 消费积压 | `lag exceeded threshold` | 消费速度慢于生产 | 增加 Consumer 实例 |

### Broker 问题

| 问题 | 日志特征 | 原因 | 解决方案 |
|------|----------|------|----------|
| Leader 切换 | `NotLeaderForPartitionException` | Broker 宕机或维护 | 重试即可，自动恢复 |
| 副本不可用 | `ReplicaNotAvailableException` | ISR 同步中 | 等待 ISR 恢复 |
| 磁盘满 | `Log segment allocation failed` | 磁盘空间不足 | 清理磁盘或扩容 |
| 内存不足 | `OutOfMemoryError` | Heap 配置不足 | 增加 `KAFKA_HEAP_OPTS` |

## 使用方法

### 基础用法

```
分析这段 Kafka 日志：

[日志内容...]
```

### 指定分析维度

```
分析以下 Kafka Consumer 日志，重点关注消费积压和 Rebalance 问题：

[日志内容...]
```

### 请求特定诊断

```
这段日志显示 Producer 发送超时，请提供修复建议：

[日志内容...]
```

## 参考资料

| 主题 | 参考 |
|------|------|
| Kafka 常见模式 | [kafka-patterns.md](references/kafka-patterns.md) |
| 错误码参考 | [error-codes.md](references/error-codes.md) |
| 性能调优指南 | [tuning-guide.md](references/tuning-guide.md) |

## 辅助脚本

| 脚本 | 用途 |
|------|------|
| `parse_kafka_log.py` | 解析日志文件，提取结构化事件 |
| `detect_anomalies.py` | 异常检测，聚类分析 |
| `generate_report.py` | 生成可视化报告 |
