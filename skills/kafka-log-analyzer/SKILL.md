---
name: kafka-log-analyzer
description: 分析 Java 服务的 Kafka 日志，提取关键事件、检测异常模式、生成诊断报告。当用户需要排查 Kafka 消息问题、分析 Producer/Consumer 日志、检测消息积压时触发。
metadata:
  author: saqqdy
  version: "2026.06.17"
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

支持纯文本和 JSON 两种格式，自动检测：
- 纯文本：`[2026-01-15 10:23:45] INFO  [thread] message`
- JSON：`{"timestamp": "2026-01-15T10:23:45Z", "level": "INFO", "message": "..."}`

### 2. 事件提取

识别 Kafka 相关事件类型：

| 事件类型 | 说明 | 日志特征 |
|----------|------|----------|
| `send_success` | 发送成功 | `Successfully sent record to topic` |
| `send_failure` | 发送失败 | `Failed to send record` |
| `consumer_lag` | 消费积压 | `lag exceeded threshold` |
| `rebalance` | 重平衡 | `Consumer group.*rebalance` |
| `commit_failure` | 提交失败 | `CommitFailedException` |
| `buffer_exhausted` | 缓冲区满 | `BufferExhaustedException` |
| `leader_change` | Leader 切换 | `leader changed from` |
| `offset_out_of_range` | 偏移量越界 | `OffsetOutOfRange` |
| `serialization_error` | 序列化失败 | `SerializationException` |
| `network_error` | 网络异常 | `NetworkException` |
| `auth_error` | 权限拒绝 | `TopicAuthorizationException` |

### 3. 优先级分级

按以下规则对事件和 Issue 自动分级：

| 优先级 | 条件 | 示例 |
|--------|------|------|
| 🔴 **P0** | 影响数据完整性的严重错误，或高频 ERROR（>=100次） | `ProducerFencedException`、消息丢失、ERROR >= 100 |
| 🟠 **P1** | 持续 ERROR（>=10次）或关键业务 WARN | `TimeoutException` 频率持续上升、消费积压超过阈值 |
| 🟡 **P2** | 一般 WARN（>=5次）或偶发 ERROR | 偶发超时、单次 Rebalance、偶尔的 Leader 切换 |
| ⚪ **P3** | 信息性日志或低频 WARN | 正常 Leader 切换（自动恢复）、INFO 级消息 |

分级判定流程：

```
收到事件
  │
  ├─ 是 P0 类型？（ProducerFenced / 消息丢失 / 数据损坏）
  │   └─→ 🔴 P0
  │
  ├─ ERROR 且 次数 >= 100？
  │   └─→ 🔴 P0
  │
  ├─ ERROR 且 次数 >= 10？
  │   └─→ 🟠 P1
  │
  ├─ 关键 WARN？（消费积压 / 提交失败）
  │   └─→ 🟠 P1
  │
  ├─ WARN 且 次数 >= 5？
  │   └─→ 🟡 P2
  │
  ├─ 偶发 ERROR？
  │   └─→ 🟡 P2
  │
  └─→ ⚪ P3
```

### 4. 异常检测

聚类错误日志，识别重复模式（7 个检测器）：

| 检测器 | 目标 | 严重度阈值 |
|--------|------|-----------|
| `error_rate_spike` | 错误率突增 | >2% medium, >5% high, >10% critical |
| `consumer_lag` | 消费积压 | >阈值 high, >10x阈值 critical |
| `rebalance_storm` | 频繁 Rebalance | >=3次 high, >10次 critical |
| `leader_instability` | Leader 频繁切换 | >=3次 medium, >5次 high |
| `replica_sync_lag` | 副本同步延迟 | 有出现 medium, >5次 high |
| `serialization_errors` | 序列化异常 | >=3次 medium, >10次 high |
| `error_rate_trend_up` | 错误率趋势上升 | 前后段错误率翻倍且后半段 >5% |

### 5. 源码联动（可选）

如果项目源码在当前仓库中，Claude 可以直接关联代码层面：

1. **搜索 Kafka 配置**：定位 `application.yml` / `application.properties` 中的 Kafka 相关配置
2. **定位出错的类**：根据日志中的线程名、异常类名找到对应的 Producer / Consumer 代码
3. **读取相关代码**：理解发送/消费逻辑，发现配置问题或代码缺陷
4. **生成修复方案**：给出配置调整 + 代码修改的完整 diff

典型联动示例：

```
日志显示: TimeoutException → topic=orders → thread=order-producer
  │
  ├→ 搜索: grep -r "order-producer" src/
  │   └→ 找到: src/main/java/com/example/OrderProducer.java
  │
  ├→ 读取: OrderProducer.java
  │   └→ 发现: request.timeout.ms=5000（过小）
  │
  └→ 修复:
     • 配置: request.timeout.ms=30000
     • 代码: 添加异步回调错误处理逻辑
     • 生成 diff 补丁
```

## 时间线分析

使用 `--timeline` 参数可按时间窗口（1m/5m/15m/1h/6h/1d）统计事件分布，快速定位错误集中时段：

```bash
# 按分钟统计
python scripts/parse_kafka_log.py kafka.log --timeline

# 按小时统计
python scripts/parse_kafka_log.py kafka.log --timeline --timeline-window 1h
```

## 实时监控

使用 `--watch` 参数可实时追踪日志文件变化，适合排查正在发生的问题：

```bash
python scripts/parse_kafka_log.py kafka.log --watch
```

## 诊断输出格式

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
  "raw_message": "Successfully sent record to topic orders partition 5 offset 12345"
}
```

### 异常对象

```json
{
  "anomaly_type": "error_rate_spike",
  "severity": "high",
  "description": "错误率 5.8%（阈值 5%），共 203 条 ERROR 日志",
  "evidence": ["send_failure: 100次", "TimeoutException: 50次"],
  "suggestion": "检查网络连通性，调整 request.timeout.ms 配置",
  "count": 203
}
```

### 分析报告

```markdown
# Kafka 日志分析报告

- **生成时间**: 2026-06-17T14:30:00
- **分析周期**: 24h
- **总行数**: 50000
- **解析事件数**: 42000
- **检测到异常**: 5 项

## 优先级分布
| 优先级 | 含义 | 事件类型数 |
|--------|------|-----------|
| 🔴 P0 | 数据完整性/生产故障 | 1 |
| 🟠 P1 | 持续错误/关键告警 | 2 |
| 🟡 P2 | 一般告警 | 1 |
| ⚪ P3 | 信息性 | 5 |
```

## 常见问题诊断

### Producer 问题

| 问题 | 优先级 | 日志特征 | 原因 | 解决方案 |
|------|--------|----------|------|----------|
| 发送超时 | 🟠 P1 | `TimeoutException` | 网络延迟或 Broker 负载高 | 调整 `request.timeout.ms` |
| 缓冲区满 | 🟡 P2 | `BufferExhaustedException` | 发送速度超过网络速度 | 增加 `buffer.memory` |
| 权限拒绝 | 🟠 P1 | `TopicAuthorizationException` | ACL 配置问题 | 检查 ACL 配置 |
| 序列化失败 | 🟡 P2 | `SerializationException` | Schema 不匹配 | 检查 Serializer 配置 |
| 生产者被隔离 | 🔴 P0 | `ProducerFencedException` | 事务冲突 | 重建 Producer 实例 |

### Consumer 问题

| 问题 | 优先级 | 日志特征 | 原因 | 解决方案 |
|------|--------|----------|------|----------|
| 提交失败 | 🟠 P1 | `CommitFailedException` | Rebalance 中断提交 | 减少 `max.poll.interval.ms` |
| 偏移量越界 | 🟡 P2 | `OffsetOutOfRange` | 消息过期被删除 | 调整 `auto.offset.reset` |
| Rebalance 频繁 | 🟠 P1 | `Revoking previously assigned` | 心跳超时或处理慢 | 增加 `session.timeout.ms` |
| 消费积压 | 🟠 P1 | `lag exceeded threshold` | 消费速度慢于生产 | 增加 Consumer 实例 |

### Broker 问题

| 问题 | 优先级 | 日志特征 | 原因 | 解决方案 |
|------|--------|----------|------|----------|
| Leader 切换 | 🟡 P2 | `NotLeaderForPartitionException` | Broker 宕机或维护 | 重试即可，自动恢复 |
| 副本不可用 | 🟡 P2 | `ReplicaNotAvailableException` | ISR 同步中 | 等待 ISR 恢复 |
| 磁盘满 | 🔴 P0 | `Log segment allocation failed` | 磁盘空间不足 | 清理磁盘或扩容 |
| 内存不足 | 🔴 P0 | `OutOfMemoryError` | Heap 配置不足 | 增加 `KAFKA_HEAP_OPTS` |

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

### 时间线分析

```
分析以下 Kafka 日志的时间分布，找出错误集中的时间段：

[日志内容...]
```

### 源码联动修复

```
这段日志显示 orders 这个 topic 的 Producer 频繁超时，
请搜索项目中的 Kafka 配置和 OrderProducer 类，给出代码层面的修复方案：

[日志内容...]
```

### 批量分析报告

```
输出最近 24h 所有 P0/P1 Kafka 错误的诊断报告
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
| `parse_kafka_log.py` | 解析日志文件，提取结构化事件，支持 `--timeline` 和 `--watch` |
| `detect_anomalies.py` | 异常检测，7 种检测器聚类分析 |
| `generate_report.py` | 生成包含优先级排序的诊断报告 |
