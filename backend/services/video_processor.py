# -*- coding: utf-8 -*-
"""MelodyClaw V2 视频处理服务

功能：
- WebM 转 MP4（H.264 + AAC）
- 生成缩略图
- 视频压缩优化
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, Dict


class VideoProcessor:
    """视频处理服务"""
    
    def __init__(self, output_dir: Optional[str] = None):
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.output_dir = None
    
    def convert_to_mp4(
        self, 
        input_path: str, 
        output_filename: Optional[str] = None,
        quality: str = 'medium'
    ) -> str:
        """
        将 WebM 转换为 MP4（H.264 + AAC）
        
        Args:
            input_path: 输入文件路径
            output_filename: 输出文件名（可选）
            quality: 质量级别 ('low', 'medium', 'high')
        
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        
        if not output_filename:
            output_filename = f"{input_path.stem}.mp4"
        
        if self.output_dir:
            output_path = self.output_dir / output_filename
        else:
            output_path = input_path.parent / output_filename
        
        # 质量配置
        quality_settings = {
            'low': {'crf': '28', 'preset': 'fast', 'audio_bitrate': '96k'},
            'medium': {'crf': '23', 'preset': 'medium', 'audio_bitrate': '128k'},
            'high': {'crf': '18', 'preset': 'slow', 'audio_bitrate': '192k'}
        }
        
        settings = quality_settings.get(quality, quality_settings['medium'])
        
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-preset', settings['preset'],
            '-crf', settings['crf'],
            '-c:a', 'aac',
            '-b:a', settings['audio_bitrate'],
            '-movflags', '+faststart',  # 支持边下载边播放
            '-y',  # 覆盖已存在文件
            str(output_path)
        ]
        
        try:
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True,
                timeout=300  # 5 分钟超时
            )
            return str(output_path)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"视频转码超时：{input_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"视频转码失败：{e.stderr}")
    
    def generate_thumbnail(
        self, 
        video_path: str, 
        output_filename: Optional[str] = None,
        timestamp: str = '00:00:01'
    ) -> str:
        """
        生成视频缩略图
        
        Args:
            video_path: 视频文件路径
            output_filename: 输出文件名（可选）
            timestamp: 截图时间点（默认第 1 秒）
        
        Returns:
            缩略图文件路径
        """
        video_path = Path(video_path)
        
        if not output_filename:
            output_filename = f"{video_path.stem}.jpg"
        
        if self.output_dir:
            output_path = self.output_dir / output_filename
        else:
            output_path = video_path.parent / output_filename
        
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-ss', timestamp,
            '-vframes', '1',
            '-vf', 'scale=320:-1',  # 宽度 320px，高度自动
            '-y',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            return str(output_path)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"生成缩略图超时：{video_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"生成缩略图失败：{e.stderr}")
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        获取视频信息
        
        Returns:
            视频信息字典（时长、分辨率、码率等）
        """
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    
    def compress_video(
        self,
        input_path: str,
        output_filename: Optional[str] = None,
        max_size_mb: Optional[float] = None
    ) -> str:
        """
        压缩视频到指定大小
        
        Args:
            input_path: 输入文件路径
            output_filename: 输出文件名（可选）
            max_size_mb: 最大文件大小（MB）
        
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        
        # 获取视频信息
        info = self.get_video_info(str(input_path))
        duration = float(info['format']['duration'])
        
        # 计算目标码率
        if max_size_mb:
            # 目标大小（bits）= 码率（bits/s）× 时长（s）
            # 码率 = 目标大小 / 时长
            target_size_bits = max_size_mb * 1024 * 1024 * 8
            audio_bitrate = 128 * 1000  # 音频 128kbps
            video_bitrate = (target_size_bits / duration) - audio_bitrate
            video_bitrate = max(video_bitrate, 500 * 1000)  # 最低 500kbps
        else:
            video_bitrate = 2500 * 1000  # 默认 2.5Mbps
        
        if not output_filename:
            output_filename = f"{input_path.stem}_compressed.mp4"
        
        if self.output_dir:
            output_path = self.output_dir / output_filename
        else:
            output_path = input_path.parent / output_filename
        
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-c:v', 'libx264',
            '-b:v', str(int(video_bitrate)),
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            '-y',
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            return str(output_path)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"视频压缩超时：{input_path}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"视频压缩失败：{e.stderr}")


# 便捷函数
def process_upload(video_path: str, output_dir: str) -> Dict[str, str]:
    """
    处理上传的视频（转码 + 生成缩略图）
    
    Returns:
        包含输出文件路径的字典
    """
    processor = VideoProcessor(output_dir)
    
    # 转码为 MP4
    mp4_path = processor.convert_to_mp4(video_path, quality='medium')
    
    # 生成缩略图
    thumbnail_path = processor.generate_thumbnail(mp4_path)
    
    return {
        'video': mp4_path,
        'thumbnail': thumbnail_path
    }
