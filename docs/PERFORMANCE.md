# MelodyClaw 性能优化指南

## 内存优化

### 1. 模型分步加载

```python
# 懒加载模式
class ModelManager:
    def __init__(self):
        self._model = None
    
    def process(self, audio):
        model = self.load()  # 首次加载
        result = model(audio)
        self.unload()  # 处理完释放
        return result
```

### 2. 内存监控

```python
import psutil
import os

def check_memory():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    print(f"当前内存：{mem_mb:.1f} MB")
    return mem_mb
```

### 3. 推荐配置

| 场景 | 内存占用 | 建议 |
|------|----------|------|
| 空闲 | ~500 MB | - |
| Demucs 推理 | ~1.2 GB | 串行处理 |
| Silero 推理 | ~100 MB | 可常驻 |
| RVC 推理 | ~1.5 GB | 串行处理 |
| 全模型常驻 | ~4 GB | 不推荐 |

## 推理优化

### 1. 批量处理

```python
# 将音频分块处理，避免一次性加载
def process_in_chunks(audio, chunk_size=30):
    results = []
    for i in range(0, len(audio), chunk_size * sr):
        chunk = audio[i:i + chunk_size * sr]
        result = model(chunk)
        results.append(result)
    return concatenate(results)
```

### 2. 模型量化

```bash
# int8 量化 (减少 50% 内存)
python -m torch.quantization.quantize_dynamic \
    model.py \
    --dtype qint8 \
    --output model_int8.pt
```

### 3. 多进程并行

```python
from multiprocessing import Pool

def parallel_process(audio_files, num_workers=4):
    with Pool(num_workers) as p:
        results = p.map(process_single, audio_files)
    return results
```

## 缓存策略

### 1. 结果缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_inference(audio_hash, model_params):
    return model(audio_hash)
```

### 2. 文件缓存

```python
import hashlib
from pathlib import Path

def get_cached_result(audio_path, params):
    cache_key = hashlib.md5(f"{audio_path}{params}".encode()).hexdigest()
    cache_file = Path(f"cache/{cache_key}.wav")
    if cache_file.exists():
        return cache_file
    return None
```

## 性能基准

### 测试环境
- CPU: 4 核
- 内存：16GB
- 存储：SSD

### 处理时间

| 操作 | 1 分钟音频 | 3 分钟音频 | 5 分钟音频 |
|------|-----------|-----------|-----------|
| 人声分离 | ~60s | ~180s | ~300s |
| 歌词对齐 | ~10s | ~30s | ~50s |
| 音色克隆 | ~90s | ~270s | ~450s |
| **总计** | ~160s | ~480s | ~800s |

### 优化效果

| 优化项 | 内存节省 | 速度提升 |
|--------|----------|----------|
| 模型分步加载 | 60% | - |
| 批量处理 | 30% | 20% |
| 结果缓存 | - | 100% (命中) |
| 多进程 | - | 2-3x |

## 生产建议

1. **内存限制:** 设置 `ulimit -v` 防止 OOM
2. **超时设置:** API 请求超时 300s
3. **并发限制:** 同时处理 ≤2 个任务
4. **监控告警:** 内存 > 80% 时告警
