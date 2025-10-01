#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 패턴 생성 모듈
Test Pattern Generator Module

다양한 테스트 패턴 생성
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import math


class TestPatternGenerator:
    def __init__(self):
        """테스트 패턴 생성기 초기화"""
        self.patterns = {
            'solid_red': self.generate_solid_red,
            'solid_green': self.generate_solid_green,
            'solid_blue': self.generate_solid_blue,
            'solid_white': self.generate_solid_white,
            'solid_black': self.generate_solid_black,
            'checkerboard': self.generate_checkerboard,
            'gradient': self.generate_gradient,
            'color_bars': self.generate_color_bars,
            'grid': self.generate_grid,
            'crosshatch': self.generate_crosshatch,
            'dots': self.generate_dots,
            'lines': self.generate_lines
        }
        
    def generate_pattern(self, width: int, height: int, pattern_type: str = 'solid_red') -> Optional[np.ndarray]:
        """
        테스트 패턴 생성
        
        Args:
            width: 패턴 너비
            height: 패턴 높이
            pattern_type: 패턴 타입
            
        Returns:
            np.ndarray: 생성된 패턴 이미지
        """
        if pattern_type not in self.patterns:
            pattern_type = 'solid_red'
            
        try:
            return self.patterns[pattern_type](width, height)
        except Exception as e:
            print(f"패턴 생성 오류: {e}")
            return None
            
    def generate_solid_red(self, width: int, height: int) -> np.ndarray:
        """빨간색 단색 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        pattern[:, :] = [255, 0, 0]  # RGB 형식 (빨간색)
        return pattern
        
    def generate_solid_green(self, width: int, height: int) -> np.ndarray:
        """초록색 단색 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        pattern[:, :] = [0, 255, 0]  # RGB 형식 (초록색)
        return pattern
        
    def generate_solid_blue(self, width: int, height: int) -> np.ndarray:
        """파란색 단색 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        pattern[:, :] = [0, 0, 255]  # RGB 형식 (파란색)
        return pattern
        
    def generate_solid_white(self, width: int, height: int) -> np.ndarray:
        """흰색 단색 패턴"""
        pattern = np.ones((height, width, 3), dtype=np.uint8) * 255
        return pattern
        
    def generate_solid_black(self, width: int, height: int) -> np.ndarray:
        """검은색 단색 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        return pattern
        
    def generate_checkerboard(self, width: int, height: int, square_size: int = 50) -> np.ndarray:
        """체스보드 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(0, height, square_size):
            for x in range(0, width, square_size):
                if (x // square_size + y // square_size) % 2 == 0:
                    pattern[y:y+square_size, x:x+square_size] = [255, 255, 255]
                else:
                    pattern[y:y+square_size, x:x+square_size] = [0, 0, 0]
                    
        return pattern
        
    def generate_gradient(self, width: int, height: int, direction: str = 'horizontal') -> np.ndarray:
        """그라디언트 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        if direction == 'horizontal':
            for x in range(width):
                intensity = int(255 * x / width)
                pattern[:, x] = [intensity, intensity, intensity]
        elif direction == 'vertical':
            for y in range(height):
                intensity = int(255 * y / height)
                pattern[y, :] = [intensity, intensity, intensity]
        elif direction == 'radial':
            center_x, center_y = width // 2, height // 2
            max_distance = math.sqrt(center_x**2 + center_y**2)
            
            for y in range(height):
                for x in range(width):
                    distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                    intensity = int(255 * (1 - distance / max_distance))
                    pattern[y, x] = [intensity, intensity, intensity]
                    
        return pattern
        
    def generate_color_bars(self, width: int, height: int) -> np.ndarray:
        """컬러 바 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        colors = [
            [255, 0, 0],    # 빨강 (RGB)
            [255, 255, 0],  # 노랑 (RGB)
            [0, 255, 0],    # 초록 (RGB)
            [255, 0, 255],  # 마젠타 (RGB)
            [0, 0, 255],    # 파랑 (RGB)
            [0, 255, 255],  # 시안 (RGB)
            [255, 255, 255], # 흰색 (RGB)
            [0, 0, 0]       # 검정 (RGB)
        ]
        
        bar_width = width // len(colors)
        
        for i, color in enumerate(colors):
            start_x = i * bar_width
            end_x = min((i + 1) * bar_width, width)
            pattern[:, start_x:end_x] = color
            
        return pattern
        
    def generate_grid(self, width: int, height: int, grid_size: int = 50) -> np.ndarray:
        """그리드 패턴"""
        pattern = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # 수직선
        for x in range(0, width, grid_size):
            cv2.line(pattern, (x, 0), (x, height), (0, 0, 0), 1)
            
        # 수평선
        for y in range(0, height, grid_size):
            cv2.line(pattern, (0, y), (width, y), (0, 0, 0), 1)
            
        return pattern
        
    def generate_crosshatch(self, width: int, height: int, line_spacing: int = 20) -> np.ndarray:
        """크로스해치 패턴"""
        pattern = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # 대각선 패턴
        for i in range(0, width + height, line_spacing):
            cv2.line(pattern, (i, 0), (0, i), (0, 0, 0), 1)
            cv2.line(pattern, (width - i, 0), (width, i), (0, 0, 0), 1)
            
        return pattern
        
    def generate_dots(self, width: int, height: int, dot_size: int = 10, spacing: int = 50) -> np.ndarray:
        """점 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(spacing, height, spacing):
            for x in range(spacing, width, spacing):
                cv2.circle(pattern, (x, y), dot_size, (255, 255, 255), -1)
                
        return pattern
        
    def generate_lines(self, width: int, height: int, line_width: int = 2, spacing: int = 20) -> np.ndarray:
        """선 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 수직선
        for x in range(0, width, spacing):
            cv2.line(pattern, (x, 0), (x, height), (255, 255, 255), line_width)
            
        # 수평선
        for y in range(0, height, spacing):
            cv2.line(pattern, (0, y), (width, y), (255, 255, 255), line_width)
            
        return pattern
        
    def generate_pixel_defect_test(self, width: int, height: int) -> np.ndarray:
        """픽셀 결함 테스트 패턴"""
        pattern = np.zeros((height, width, 3), dtype=np.uint8)
        
        # 다양한 밝기 레벨
        brightness_levels = [0, 32, 64, 96, 128, 160, 192, 224, 255]
        section_height = height // len(brightness_levels)
        
        for i, brightness in enumerate(brightness_levels):
            start_y = i * section_height
            end_y = min((i + 1) * section_height, height)
            pattern[start_y:end_y, :] = [brightness, brightness, brightness]
            
        return pattern
        
    def generate_mura_test(self, width: int, height: int) -> np.ndarray:
        """무라(Mura) 테스트 패턴"""
        pattern = np.ones((height, width, 3), dtype=np.uint8) * 128
        
        # 중앙에 어두운 영역
        center_x, center_y = width // 2, height // 2
        cv2.circle(pattern, (center_x, center_y), min(width, height) // 4, (64, 64, 64), -1)
        
        return pattern
        
    def get_available_patterns(self) -> list:
        """사용 가능한 패턴 목록 반환"""
        return list(self.patterns.keys())
        
    def generate_custom_pattern(self, width: int, height: int, pattern_data: np.ndarray) -> np.ndarray:
        """
        사용자 정의 패턴 생성
        
        Args:
            width: 패턴 너비
            height: 패턴 높이
            pattern_data: 패턴 데이터
            
        Returns:
            np.ndarray: 리사이즈된 패턴
        """
        if pattern_data is None:
            return self.generate_solid_red(width, height)
            
        # 패턴을 지정된 크기로 리사이즈
        resized = cv2.resize(pattern_data, (width, height))
        return resized
        
    def save_pattern(self, pattern: np.ndarray, filename: str) -> bool:
        """
        패턴을 파일로 저장
        
        Args:
            pattern: 저장할 패턴
            filename: 파일명
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            cv2.imwrite(filename, pattern)
            return True
        except Exception as e:
            print(f"패턴 저장 오류: {e}")
            return False
