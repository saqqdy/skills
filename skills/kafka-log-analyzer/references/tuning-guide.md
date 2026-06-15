# Kafka 性能调优指南

本文档提供 Kafka Producer、Consumer、Broker 的性能调优建议。

## Producer 调优

### 批量发送

```properties
batch.size=32768
linger.ms=10
buffer.memory=67108864
```

### 压缩配置

```properties
compression.type=lz4
```

### 重试配置

```properties
retries=3
retry.backoff.ms=100
request.timeout.ms=30000
delivery.timeout.ms=120000
```

### 吞吐量优化

```properties
max.block.ms=60000
enable.idempotence=true
transactional.id=producer-1
```

---

## Consumer 调优

### 拉取配置

```properties
max.poll.records=1000
max.partition.fetch.bytes=1048576
fetch.min.bytes=1024
fetch.max.wait.ms=500
```

### 心跳配置

```properties
heartbeat.interval.ms=3000
session.timeout.ms=30000
max.poll.interval.ms=600000
```

### 偏移量提交

```properties
# 自动提交
enable.auto.commit=true
auto.commit.interval.ms=5000

# 或手动提交
enable.auto.commit=false
```

### 静态成员

```properties
group.instance.id=consumer-instance-1
max.poll.interval.ms=1800000
```

---

## Broker 调优

### 线程配置

```properties
num.network.threads=8
num.io.threads=8
background.threads=10
```

### 日志配置

```properties
log.dirs=/data1/kafka,/data2/kafka,/data3/kafka
log.flush.interval.messages=10000
log.flush.interval.ms=1000
log.retention.hours=168
log.retention.bytes=1073741824
```

### 副本配置

```properties
default.replication.factor=3
min.insync.replicas=2
num.replica.fetchers=4
replica.fetch.max.bytes=1048576
```

### JVM 配置

```bash
export KAFKA_HEAP_OPTS="-Xms4g -Xmx4g"
export KAFKA_JVM_PERFORMANCE_OPTS="-XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:MaxDirectMemorySize=2g"
```

---

## 网络调优

```properties
# Producer
max.request.size=1048576
send.buffer.bytes=131072
receive.buffer.bytes=32768

# Consumer
fetch.max.bytes=52428800
send.buffer.bytes=131072
receive.buffer.bytes=65536

# Broker
socket.request.max.bytes=104857600
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
max.connections=10000
```

---

## 监控指标

### Producer 监控

| 指标 | 说明 | 警戒值 |
|------|------|--------|
| `record-send-rate` | 发送速率 | - |
| `record-error-rate` | 错误率 | > 0.01 |
| `request-latency-avg` | 平均延迟 | > 100ms |
| `buffer-available-bytes` | 可用缓冲区 | < 10% |

### Consumer 监控

| 指标 | 说明 | 警戒值 |
|------|------|--------|
| `records-consumed-rate` | 消费速率 | - |
| `records-lag-max` | 最大积压 | > 10000 |
| `join-rate` | Rebalance 速率 | > 10/min |

### Broker 监控

| 指标 | 说明 | 警戒值 |
|------|------|--------|
| `UnderReplicatedPartitions` | 副本不足分区 | > 0 |
| `OfflinePartitionsCount` | 离线分区 | > 0 |
| `ActiveControllerCount` | 活跃 Controller | != 1 |

---

## 性能测试

```bash
# Producer 测试
kafka-producer-perf-test.sh \
  --topic test-topic --num-records 1000000 \
  --record-size 1024 --throughput 100000 \
  --producer-props bootstrap.servers=localhost:9092

# Consumer 测试
kafka-consumer-perf-test.sh \
  --topic test-topic --messages 1000000 \
  --bootstrap-server localhost:9092
```
