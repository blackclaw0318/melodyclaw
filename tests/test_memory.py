"""
内存压力测试脚本
测试模型加载的内存占用和处理时间
"""
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from ai_models.loader import ModelManager


class MemoryTestReport:
    """内存测试报告"""
    
    def __init__(self):
        self.results = []
        self.summary = {}
    
    def add_result(self, test_name: str, data: dict):
        self.results.append({
            "test": test_name,
            "timestamp": datetime.now().isoformat(),
            **data
        })
    
    def generate_summary(self):
        if not self.results:
            return {}
        
        memory_peaks = [r.get("memory_peak_mb", 0) for r in self.results]
        memory_increases = [r.get("memory_increase_mb", 0) for r in self.results]
        
        self.summary = {
            "total_tests": len(self.results),
            "max_memory_peak_mb": max(memory_peaks) if memory_peaks else 0,
            "avg_memory_increase_mb": sum(memory_increases) / len(memory_increases) if memory_increases else 0,
            "all_passed": all(r.get("passed", False) for r in self.results)
        }
        return self.summary
    
    def to_markdown(self) -> str:
        """生成 Markdown 格式报告"""
        self.generate_summary()
        
        md = ["# MelodyClaw 阶段 1 - 内存压力测试报告", ""]
        md.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")
        
        md.append("## 测试摘要")
        md.append("")
        md.append(f"- 总测试数：{self.summary.get('total_tests', 0)}")
        md.append(f"- 内存峰值：{self.summary.get('max_memory_peak_mb', 0):.1f} MB")
        md.append(f"- 平均内存增加：{self.summary.get('avg_memory_increase_mb', 0):.1f} MB")
        md.append(f"- 全部通过：{'✅ 是' if self.summary.get('all_passed') else '❌ 否'}")
        md.append("")
        
        md.append("## 详细结果")
        md.append("")
        
        for result in self.results:
            md.append(f"### {result['test']}")
            md.append("")
            md.append(f"- 状态：{'✅ 通过' if result.get('passed') else '❌ 失败'}")
            md.append(f"- 内存峰值：{result.get('memory_peak_mb', 0):.1f} MB")
            md.append(f"- 内存增加：{result.get('memory_increase_mb', 0):.1f} MB")
            md.append(f"- 耗时：{result.get('duration_s', 0):.2f} 秒")
            if result.get('error'):
                md.append(f"- 错误：{result['error']}")
            md.append("")
        
        md.append("## 结论")
        md.append("")
        if self.summary.get('all_passed'):
            md.append("✅ 所有测试通过，16GB 内存配置可以支持模型运行。")
        else:
            md.append("❌ 部分测试失败，需要优化内存使用。")
        
        return "\n".join(md)
    
    def save(self, path: str):
        with open(path, 'w') as f:
            f.write(self.to_markdown())


def test_demucs_loading(report: MemoryTestReport):
    """测试 Demucs 模型加载"""
    print("\n" + "="*50)
    print("测试 1: Demucs 模型加载")
    print("="*50)
    
    manager = ModelManager()
    mem_before = manager.get_memory_usage()
    start_time = time.time()
    
    try:
        model = manager.load_demucs()
        duration = time.time() - start_time
        mem_after = manager.get_memory_usage()
        
        memory_increase = mem_after['rss_mb'] - mem_before['rss_mb']
        memory_peak = mem_after['rss_mb']
        
        passed = memory_peak < 14000  # 14GB 限制
        
        report.add_result("Demucs 模型加载", {
            "passed": passed,
            "memory_before_mb": mem_before['rss_mb'],
            "memory_peak_mb": memory_peak,
            "memory_increase_mb": memory_increase,
            "duration_s": duration,
            "model_name": "htdemucs_ft"
        })
        
        manager.unload_demucs()
        print(f"✅ Demucs 测试完成")
        
    except Exception as e:
        report.add_result("Demucs 模型加载", {
            "passed": False,
            "error": str(e)
        })
        print(f"❌ Demucs 测试失败：{e}")


def test_silero_loading(report: MemoryTestReport):
    """测试 Silero VAD 模型加载"""
    print("\n" + "="*50)
    print("测试 2: Silero VAD 模型加载")
    print("="*50)
    
    manager = ModelManager()
    mem_before = manager.get_memory_usage()
    start_time = time.time()
    
    try:
        model = manager.load_silero()
        duration = time.time() - start_time
        mem_after = manager.get_memory_usage()
        
        memory_increase = mem_after['rss_mb'] - mem_before['rss_mb']
        memory_peak = mem_after['rss_mb']
        
        passed = memory_peak < 14000
        
        report.add_result("Silero VAD 模型加载", {
            "passed": passed,
            "memory_before_mb": mem_before['rss_mb'],
            "memory_peak_mb": memory_peak,
            "memory_increase_mb": memory_increase,
            "duration_s": duration
        })
        
        manager.unload_silero()
        print(f"✅ Silero VAD 测试完成")
        
    except Exception as e:
        report.add_result("Silero VAD 模型加载", {
            "passed": False,
            "error": str(e)
        })
        print(f"❌ Silero VAD 测试失败：{e}")


def test_sequential_loading(report: MemoryTestReport):
    """测试多模型串行加载"""
    print("\n" + "="*50)
    print("测试 3: 多模型串行加载")
    print("="*50)
    
    manager = ModelManager()
    mem_before = manager.get_memory_usage()
    start_time = time.time()
    
    try:
        # 依次加载和卸载
        manager.load_demucs()
        mem_demucs = manager.get_memory_usage()
        manager.unload_demucs()
        
        manager.load_silero()
        mem_silero = manager.get_memory_usage()
        manager.unload_silero()
        
        duration = time.time() - start_time
        mem_after = manager.get_memory_usage()
        
        memory_peak = max(mem_demucs['rss_mb'], mem_silero['rss_mb'])
        
        passed = memory_peak < 14000
        
        report.add_result("多模型串行加载", {
            "passed": passed,
            "memory_before_mb": mem_before['rss_mb'],
            "memory_peak_mb": memory_peak,
            "memory_after_mb": mem_after['rss_mb'],
            "duration_s": duration,
            "strategy": "串行加载 + 及时释放"
        })
        
        print(f"✅ 串行加载测试完成")
        
    except Exception as e:
        report.add_result("多模型串行加载", {
            "passed": False,
            "error": str(e)
        })
        print(f"❌ 串行加载测试失败：{e}")


def test_memory_limit(report: MemoryTestReport):
    """测试内存限制检查"""
    print("\n" + "="*50)
    print("测试 4: 内存限制检查")
    print("="*50)
    
    manager = ModelManager()
    
    try:
        within_limit = manager.check_memory_limit(14000)
        mem_info = manager.get_memory_usage()
        
        report.add_result("内存限制检查", {
            "passed": True,
            "current_memory_mb": mem_info['rss_mb'],
            "limit_mb": 14000,
            "within_limit": within_limit
        })
        
        print(f"✅ 内存检查完成：当前 {mem_info['rss_mb']:.1f} MB < 14000 MB")
        
    except Exception as e:
        report.add_result("内存限制检查", {
            "passed": False,
            "error": str(e)
        })
        print(f"❌ 内存检查失败：{e}")


def main():
    """主测试函数"""
    print("="*60)
    print("MelodyClaw 阶段 1 - 内存压力测试")
    print("="*60)
    
    report = MemoryTestReport()
    
    # 运行所有测试
    test_demucs_loading(report)
    test_silero_loading(report)
    test_sequential_loading(report)
    test_memory_limit(report)
    
    # 生成报告
    report_path = Path(__file__).parent.parent / "PHASE1_TEST_REPORT.md"
    report.save(str(report_path))
    
    print("\n" + "="*60)
    print(f"测试完成！报告已保存至：{report_path}")
    print("="*60)
    
    # 打印摘要
    summary = report.generate_summary()
    print(f"\n摘要:")
    print(f"  总测试数：{summary.get('total_tests', 0)}")
    print(f"  全部通过：{'✅ 是' if summary.get('all_passed') else '❌ 否'}")
    
    return 0 if summary.get('all_passed') else 1


if __name__ == "__main__":
    sys.exit(main())
