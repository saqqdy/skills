# Kafka 错误码参考

本文档整理了 Kafka 常见错误码及其说明。

## 客户端错误 (Retriable)

这些错误可以通过重试解决。

| 错误码 | 名称 | 说明 | 重试建议 |
|--------|------|------|----------|
| -1 | `UNKNOWN` | 未知错误 | 重试 |
| 14 | `GROUP_AUTHORIZATION_FAILED` | 组授权失败 | 检查 ACL |
| 15 | `GROUP_COORDINATOR_NOT_AVAILABLE` | Coordinator 不可用 | 重试 |
| 16 | `NOT_COORDINATOR` | 非 Coordinator | 重试 |
| 17 | `INVALID_TOPIC_EXCEPTION` | Topic 名称无效 | 检查名称 |
| 18 | `TOPIC_AUTHORIZATION_FAILED` | Topic 授权失败 | 检查 ACL |
| 19 | `REBALANCE_IN_PROGRESS` | 正在重平衡 | 重试 |
| 20 | `ILLEGAL_GENERATION` | 非法 Generation ID | 重新加入组 |
| 21 | `INVALID_PARTITION` | 无效分区 | 检查分区数 |
| 22 | `INVALID_COMMIT_OFFSET_SIZE` | 提交偏移量无效 | 重试 |
| 23 | `INVALID_RECORD` | 无效记录 | 检查数据格式 |
| 25 | `NOT_ENOUGH_REPLICAS` | 副本不足 | 等待 ISR |
| 26 | `NOT_ENOUGH_REPLICAS_AFTER_APPEND` | 写入后副本不足 | 重试 |
| 35 | `COORDINATOR_LOAD_IN_PROGRESS` | Coordinator 加载中 | 重试 |
| 40 | `TOPIC_AUTHORIZATION_FAILED` | Topic 授权失败 | 检查 ACL |
| 42 | `INVALID_PRODUCER_ID_MAPPING` | Producer ID 无效 | 重置 Producer |
| 43 | `INVALID_TXN_STATE` | 事务状态无效 | 检查事务 |
| 44 | `INVALID_PRODUCER_EPOCH` | Producer Epoch 无效 | 重建 Producer |

## 服务端错误

这些错误需要等待 Broker 恢复或调整配置。

| 错误码 | 名称 | 说明 | 解决方案 |
|--------|------|------|----------|
| 5 | `LEADER_NOT_AVAILABLE` | Leader 不可用 | 等待选举完成 |
| 6 | `NOT_LEADER_FOR_PARTITION` | 非 Leader | 重试或重定向 |
| 7 | `REQUEST_TIMED_OUT` | 请求超时 | 检查网络或增加超时 |
| 9 | `REPLICA_NOT_AVAILABLE` | 副本不可用 | 等待同步 |
| 10 | `MESSAGE_SIZE_TOO_LARGE` | 消息过大 | 压缩或分割消息 |
| 11 | `STALE_CONTROLLER_EPOCH` | Controller Epoch 过期 | 重试 |
| 12 | `OFFSET_METADATA_TOO_LARGE` | 偏移量元数据过大 | 减少元数据大小 |

## 致命错误

这些错误需要应用层处理。

| 错误码 | 名称 | 说明 | 处理建议 |
|--------|------|------|----------|
| 2 | `CORRUPT_MESSAGE` | 消息损坏 | 跳过或重新生产 |
| 3 | `UNKNOWN_TOPIC_OR_PARTITION` | Topic 或分区不存在 | 创建 Topic |
| 4 | `INVALID_FETCH_SIZE` | 拉取大小无效 | 调整配置 |
| 8 | `NETWORK_EXCEPTION` | 网络异常 | 检查连接 |
| 13 | `OFFSET_OUT_OF_RANGE` | 偏移量越界 | 重置偏移量 |
| 24 | `CONCURRENT_TRANSACTIONS` | 并发事务冲突 | 等待事务完成 |

## 常见异常类

### Producer 异常

```java
// 发送超时
org.apache.kafka.common.errors.TimeoutException

// 缓冲区满
org.apache.kafka.clients.producer.BufferExhaustedException

// 序列化失败
org.apache.kafka.common.errors.SerializationException

// 授权失败
org.apache.kafka.common.errors.TopicAuthorizationException

// 事务异常
org.apache.kafka.common.errors.ProducerFencedException
```

### Consumer 异常

```java
// 提交失败
org.apache.kafka.clients.consumer.CommitFailedException

// 偏移量越界
org.apache.kafka.clients.consumer.NoOffsetForPartitionException

// Rebalance 异常
org.apache.kafka.common.errors.WakeupException
org.apache.kafka.common.errors.InterruptException

// 认证失败
org.apache.kafka.common.errors.AuthenticationException
```

### Broker 异常

```java
// 非 Leader
org.apache.kafka.common.errors.NotLeaderForPartitionException

// 副本不可用
org.apache.kafka.common.errors.ReplicaNotAvailableException

// Controller 异常
org.apache.kafka.common.errors.ControllerMovedException

// 集群授权失败
org.apache.kafka.common.errors.ClusterAuthorizationException
```

## 错误码映射表

### HTTP 状态码映射

| Kafka 错误 | HTTP 状态码 | 说明 |
|------------|-------------|------|
| `UNKNOWN_TOPIC_OR_PARTITION` | 404 | Not Found |
| `TOPIC_AUTHORIZATION_FAILED` | 403 | Forbidden |
| `INVALID_TOPIC_EXCEPTION` | 400 | Bad Request |
| `REQUEST_TIMED_OUT` | 504 | Gateway Timeout |
| `LEADER_NOT_AVAILABLE` | 503 | Service Unavailable |

### 重试策略映射

| 错误类型 | 重试次数 | 退避策略 |
|----------|----------|----------|
| 可重试错误 | 3 次 | 指数退避 |
| 网络错误 | 5 次 | 固定间隔 |
| 授权错误 | 0 次 | 立即失败 |
| 配置错误 | 0 次 | 立即失败 |

## 错误处理最佳实践

### Producer 错误处理

```java
producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        if (exception instanceof RetriableException) {
            // 可重试错误，加入重试队列
            retryQueue.add(record);
        } else if (exception instanceof AuthorizationException) {
            // 授权错误，检查配置
            log.error("Authorization failed: {}", exception.getMessage());
        } else if (exception instanceof ProducerFencedException) {
            // 事务冲突，需要重建 Producer
            producer.close();
            createNewProducer();
        }
    }
});
```

### Consumer 错误处理

```java
try {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(1000));
    // 处理记录
    consumer.commitSync();
} catch (CommitFailedException e) {
    // Rebalance 导致提交失败
    log.warn("Commit failed, will retry on next poll");
} catch (WakeupException e) {
    // 正常退出信号
    log.info("Consumer wakeup called");
} catch (AuthenticationException e) {
    // 认证失败，需要重新认证
    log.error("Authentication failed: {}", e.getMessage());
}
```

### Broker 错误处理

```bash
# 监控关键指标
kafka-run-class.sh kafka.tools.JmxTool \
  --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec \
  --attributes OneMinuteRate

# 检查 Broker 健康状态
kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```
