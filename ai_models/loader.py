"""
AI 模型管理器 - 负责模型的加载、卸载和内存管理
支持分步加载，避免内存峰值
"""
import torch
import gc
import psutil
import os
from typing import Optional, Dict, Any
from pathlib import Path


class ModelManager:
    """
    AI 模型管理器
    
    特性:
    - 分步加载模型，避免内存峰值
    - 支持模型卸载释放内存
    - 内存使用监控
    - CPU 推理优化
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = models_dir or Path(__file__).parent.parent.parent / "ai_models"
        self.demucs_model = None
        self.silero_model = None
        self.rvc_model = None
        self.hubert_model = None
        self._loaded_models: Dict[str, Any] = {}
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        获取当前内存使用情况
        
        Returns:
            包含内存使用信息的字典 (MB)
        """
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # 常驻内存
            "vms_mb": memory_info.vms / 1024 / 1024,  # 虚拟内存
            "percent": process.memory_percent()
        }
    
    def load_demucs(self, model_name: str = "htdemucs_ft") -> Any:
        """
        加载 Demucs 人声分离模型
        
        Args:
            model_name: 模型名称，默认 htdemucs_ft
            
        Returns:
            加载的 Demucs 模型
        """
        if self.demucs_model is not None:
            print("✅ Demucs 模型已加载")
            return self.demucs_model
        
        print(f"📥 加载 Demucs 模型 ({model_name})...")
        mem_before = self.get_memory_usage()
        
        try:
            from demucs.pretrained import get_model
            self.demucs_model = get_model(model_name)
            
            mem_after = self.get_memory_usage()
            print(f"✅ Demucs 加载完成，内存增加：{mem_after['rss_mb'] - mem_before['rss_mb']:.1f} MB")
            
            self._loaded_models['demucs'] = self.demucs_model
            return self.demucs_model
            
        except Exception as e:
            print(f"❌ Demucs 加载失败：{e}")
            raise
    
    def load_silero(self) -> Any:
        """
        加载 Silero VAD (语音活动检测) 模型
        
        Returns:
            加载的 Silero 模型
        """
        if self.silero_model is not None:
            print("✅ Silero VAD 已加载")
            return self.silero_model
        
        print("📥 加载 Silero VAD 模型...")
        mem_before = self.get_memory_usage()
        
        try:
            # 使用 torch.hub 加载 Silero VAD
            self.silero_model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True
            )
            self.silero_utils = utils
            
            mem_after = self.get_memory_usage()
            print(f"✅ Silero VAD 加载完成，内存增加：{mem_after['rss_mb'] - mem_before['rss_mb']:.1f} MB")
            
            self._loaded_models['silero'] = self.silero_model
            return self.silero_model
            
        except Exception as e:
            print(f"❌ Silero VAD 加载失败：{e}")
            raise
    
    def load_rvc(self, model_path: Optional[Path] = None) -> Any:
        """
        加载 RVC v2 音色克隆模型
        
        Args:
            model_path: RVC 模型路径
            
        Returns:
            加载的 RVC 模型
        """
        if self.rvc_model is not None:
            print("✅ RVC 模型已加载")
            return self.rvc_model
        
        print("📥 加载 RVC v2 模型...")
        mem_before = self.get_memory_usage()
        
        try:
            # RVC 模型加载逻辑 (实际实现需要根据 RVC 库的 API)
            # 这里是占位实现
            model_path = model_path or self.models_dir / "rvc"
            
            # TODO: 实现 RVC 实际加载逻辑
            # from rvc.infer import RVCInference
            # self.rvc_model = RVCInference(model_path)
            
            self.rvc_model = {"status": "placeholder", "path": str(model_path)}
            
            mem_after = self.get_memory_usage()
            print(f"✅ RVC 加载完成，内存增加：{mem_after['rss_mb'] - mem_before['rss_mb']:.1f} MB")
            
            self._loaded_models['rvc'] = self.rvc_model
            return self.rvc_model
            
        except Exception as e:
            print(f"❌ RVC 加载失败：{e}")
            raise
    
    def unload_demucs(self):
        """卸载 Demucs 模型释放内存"""
        if self.demucs_model is not None:
            print("🗑️  卸载 Demucs 模型...")
            del self.demucs_model
            self.demucs_model = None
            self._loaded_models.pop('demucs', None)
            self._clear_memory()
            print("✅ Demucs 已卸载")
    
    def unload_silero(self):
        """卸载 Silero 模型释放内存"""
        if self.silero_model is not None:
            print("🗑️  卸载 Silero VAD 模型...")
            del self.silero_model
            self.silero_model = None
            self._loaded_models.pop('silero', None)
            self._clear_memory()
            print("✅ Silero VAD 已卸载")
    
    def unload_rvc(self):
        """卸载 RVC 模型释放内存"""
        if self.rvc_model is not None:
            print("🗑️  卸载 RVC 模型...")
            del self.rvc_model
            self.rvc_model = None
            self._loaded_models.pop('rvc', None)
            self._clear_memory()
            print("✅ RVC 已卸载")
    
    def unload_all(self):
        """卸载所有模型释放内存"""
        print("🗑️  卸载所有模型...")
        mem_before = self.get_memory_usage()
        
        self.unload_demucs()
        self.unload_silero()
        self.unload_rvc()
        
        mem_after = self.get_memory_usage()
        print(f"✅ 所有模型已卸载，释放内存：{mem_before['rss_mb'] - mem_after['rss_mb']:.1f} MB")
    
    def _clear_memory(self):
        """清理内存"""
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_loaded_models(self) -> list:
        """获取已加载的模型列表"""
        return list(self._loaded_models.keys())
    
    def check_memory_limit(self, limit_mb: int = 14000) -> bool:
        """
        检查内存使用是否超过限制
        
        Args:
            limit_mb: 内存限制 (MB)
            
        Returns:
            True 如果内存使用正常，False 如果超过限制
        """
        current = self.get_memory_usage()
        if current['rss_mb'] > limit_mb:
            print(f"⚠️  内存警告：当前 {current['rss_mb']:.1f} MB > 限制 {limit_mb} MB")
            return False
        return True


# 全局模型管理器实例
model_manager = ModelManager()
