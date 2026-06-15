# Kafka 常见日志模式

本文档整理了 Kafka Producer、Consumer、Broker 的常见日志模式及其解决方案。

## Producer 问题

### 发送超时

**日志模式**：
```
[ERROR] Failed to send record to topic <topic>: TimeoutException
[WARN] Batch for topic-partition <topic>-<partition> is complete, but metadata may have changed
```

**原因分析**：
- 网络延迟过高
- Broker 负载高，处理慢
- `request.timeout.ms` 配置过小

**解决方案**：
```properties
# 增加超时时间
request.timeout.ms=30000
delivery.timeout.ms=120000

# 增加重试次数
retries=3
retry.backoff.ms=100
```

### 缓冲区满

**日志模式**：
```
[ERROR] BufferExhaustedException: Buffer is full, blocking for <ms>ms
[WARN] Failed to allocate memory for batch, blocking for <ms>ms
```

**原因分析**：
- 发送速度超过网络传输速度
- `buffer.memory` 配置不足
- `linger.ms` 过大导致批量发送慢

**解决方案**：
```properties
# 增加缓冲区大小
buffer.memory=67108864  # 64MB

# 减少linger时间
linger.ms=5

# 启用压缩
compression.type=lz4
```

### 权限拒绝

**日志模式**：
```
[ERROR] TopicAuthorizationException: Not authorized to access topics: [<topic>]
[WARN] Authorization failed for topic <topic>
```

**原因分析**：
- ACL 配置未包含该用户
- 用户凭证过期
- Super user 配置缺失

**解决方案**：
```bash
# 检查 ACL 配置
kafka-acls.sh --bootstrap-server localhost:9092 --list

# 添加权限
kafka-acls.sh --bootstrap-server localhost:9092 \
  --add --allow-principal User:<user> \
  --operation Read --operation Write \
  --topic <topic>
```

### 序列化失败

**日志模式**：
```
[ERROR] SerializationException: Error serializing key/value for topic <topic>
[ERROR] Caused by: org.apache.kafka.common.errors.SerializationException
```

**原因分析**：
- Schema 不匹配
- Serializer 配置错误
- 数据格式变更

**解决方案**：
```properties
# 检查 Serializer 配置
key.serializer=org.apache.kafka.common.serialization.StringSerializer
value.serializer=org.apache.kafka.common.serialization.StringSerializer

# 或使用 JSON Schema Registry
value.serializer=io.confluent.kafka.serializers.KafkaJsonSerializer
```

---

## Consumer 问题

### 提交失败

**日志模式**：
```
[ERROR] CommitFailedException: Commit cannot be completed due to group rebalance
[WARN] Offset commit failed, rejoining group
```

**原因分析**：
- Rebalance 中断了提交
- `max.poll.interval.ms` 过小
- `session.timeout.ms` 过小

**解决方案**：
```properties
# 增加处理间隔
max.poll.interval.ms=300000  # 5分钟

# 增加会话超时
session.timeout.ms=30000

# 减少单次拉取数量
max.poll.records=500
```

### 偏移量越界

**日志模式**：
```
[ERROR] OffsetOutOfRange: No offset for topic-partition <topic>-<partition>
[WARN] Fetch offset <offset> is out of range for partition <topic>-<partition>
```

**原因分析**：
- 消息已过期被删除
- Consumer 从不存在的偏移量开始
- `auto.offset.reset` 配置错误

**解决方案**：
```properties
# 设置自动重置策略
auto.offset.reset=earliest  # 或 latest

# 手动重置偏移量
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group <group> --reset-offsets --to-earliest --topic <topic> --execute
```

### Rebalance 频繁

**日志模式**：
```
[INFO] Revoking previously assigned partitions [<topic>-<partition>]
[INFO] (Re-)joining group <group>
[INFO] Successfully joined group <group> with generation <gen>
```

**原因分析**：
- Consumer 心跳超时
- 处理时间过长
- Coordinator 故障

**解决方案**：
```properties
# 增加心跳间隔
heartbeat.interval.ms=5000

# 增加会话超时
session.timeout.ms=60000

# 增加最大处理间隔
max.poll.interval.ms=600000

# 使用静态成员
group.instance.id=<unique-id>
```

### 消费积压

**日志模式**：
```
[WARN] Consumer group <group>: lag exceeded threshold (<count> messages)
[INFO] Current lag for topic <topic> partition <partition>: <lag>
```

**原因分析**：
- 消费速度慢于生产速度
- Consumer 实例不足
- 处理逻辑耗时

**解决方案**：
```properties
# 增加分区数
kafka-topics.sh --alter --topic <topic> --partitions 12

# 增加 Consumer 实例（同组）

# 优化处理逻辑，使用批处理
max.poll.records=1000
```

---

## Broker 问题

### Leader 切换

**日志模式**：
```
[INFO] Partition <topic>-<partition>: leader changed from <broker1> to <broker2>
[WARN] Leader not local for partition <topic>-<partition>
```

**原因分析**：
- Broker 宕机或重启
- Controller 重新分配 Leader
- Preferred Leader 选举

**解决方案**：
```bash
# 检查 Broker 状态
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# 触发 Preferred Leader 选举
kafka-leader-election.sh --bootstrap-server localhost:9092 \
  --all-topic-partitions --election-type preferred
```

### 副本不可用

**日志模式**：
```
[WARN] Replica not available for partition <topic>-<partition>
[ERROR] ReplicaFetcherThread failed to fetch from broker <broker>
```

**原因分析**：
- ISR 同步中
- Follower 副本落后
- 网络分区

**解决方案**：
```properties
# 检查 ISR 状态
kafka-topics.sh --describe --topic <topic> --bootstrap-server localhost:9092

# 调整 ISR 配置
num.io.threads=8
num.replica.fetchers=4
replica.fetch.max.bytes=1048576
```

### 磁盘满

**日志模式**：
```
[ERROR] Log segment allocation failed due to disk full
[FATAL] Shutdown broker because disk full
```

**原因分析**：
- 日志文件未清理
- `log.retention` 配置不当
- 磁盘空间不足

**解决方案**：
```properties
# 设置日志保留策略
log.retention.hours=168  # 7天
log.retention.bytes=1073741824  # 1GB

# 启用压缩
compression.type=producer

# 清理日志
kafka-delete-records.sh --bootstrap-server localhost:9092 \
  --offset-json-file offsets.json
```

### 内存不足

**日志模式**：
```
[ERROR] OutOfMemoryError: Java heap space
[FATAL] OutOfMemoryError: Direct buffer memory
```

**原因分析**：
- Heap 配置不足
- 内存泄漏
- 页缓存占用过多

**解决方案**：
```bash
# 增加 Heap 大小
export KAFKA_HEAP_OPTS="-Xms4g -Xmx4g"

# 调整 JVM 参数
export KAFKA_JVM_PERFORMANCE_OPTS="-XX:+UseG1GC -XX:MaxGCPauseMillis=20"
```

---

## 网络问题

### 连接拒绝

**日志模式**：
```
[ERROR] Connection to <broker> failed: java.net.ConnectException: Connection refused
[WARN] Failed to connect to broker <broker>, retrying...
```

**原因分析**：
- Broker 未启动
- 防火墙阻止
- 端口错误

**解决方案**：
```bash
# 检查 Broker 状态
systemctl status kafka

# 检查端口
netstat -tlnp | grep 9092

# 测试连接
telnet localhost 9092
```

### SSL 握手失败

**日志模式**：
```
[ERROR] SSL handshake failed: sun.security.validator.ValidatorException
[WARN] Failed to establish SSL connection to <broker>
```

**原因分析**：
- 证书过期
- 证书不受信任
- 协议版本不匹配

**解决方案**：
```properties
# 检查证书有效期
keytool -list -v -keystore kafka.server.keystore.jks

# 更新证书
keytool -importcert -alias <alias> -file <cert> \
  -keystore kafka.server.truststore.jks

# 配置 SSL
security.inter.broker.protocol=SSL
ssl.enabled.protocols=TLSv1.2,TLSv1.3
```

---

## 最佳实践

### 日志配置

```properties
# Producer 日志
log4j.logger.org.apache.kafka.clients.producer=INFO, producer
log4j.appender.producer=org.apache.log4j.RollingFileAppender
log4j.appender.producer.File=${kafka.logs.dir}/producer.log

# Consumer 日志
log4j.logger.org.apache.kafka.clients.consumer=INFO, consumer
log4j.appender.consumer=org.apache.log4j.RollingFileAppender
log4j.appender.consumer.File=${kafka.logs.dir}/consumer.log
```

### 监控指标

| 组件 | 关键指标 |
|------|----------|
| Producer | `record-send-rate`, `record-error-rate`, `request-latency-avg` |
| Consumer | `records-consumed-rate`, `records-lag-max`, `commit-rate` |
| Broker | `MessagesInPerSec`, `BytesInPerSec`, `UnderReplicatedPartitions` |

### 故障排查流程

```
1. 确认问题范围（Producer/Consumer/Broker）
2. 收集相关日志
3. 识别错误类型
4. 查找根本原因
5. 应用解决方案
6. 验证问题解决
```
