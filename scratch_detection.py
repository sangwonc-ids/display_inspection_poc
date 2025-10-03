#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스크래치 검사 모듈
Scratch Detection Module

디스플레이 스크래치 검출 및 분석
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from skimage import filters, morphology, measure
# peak_local_maxima는 현재 사용하지 않으므로 import 제거


class ScratchDetection:
    def __init__(self):
        """스크래치 검사 모듈 초기화"""
        self.min_length = 20  # 최소 스크래치 길이
        self.max_width = 5    # 최대 스크래치 폭
        self.min_contrast = 30  # 최소 대비
        self.sensitivity = 0.5  # 민감도 (0.0 ~ 1.0)
        
    def detect_scratches(self, frame: np.ndarray, display_region: np.ndarray) -> List[dict]:
        """
        스크래치 검출
        
        Args:
            frame: 입력 프레임
            display_region: 디스플레이 영역 (x, y, w, h)
            
        Returns:
            List[dict]: 검출된 스크래치 정보 리스트
        """
        if frame is None or display_region is None:
            return []
            
        try:
            # 디스플레이 영역 추출
            x, y, w, h = display_region
            roi = frame[y:y+h, x:x+w]
            
            if roi.size == 0:
                return []
                
            # 그레이스케일 변환
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # 스크래치 검출
            scratches = self._detect_line_defects(gray)
            
            # 결과를 원본 좌표계로 변환
            for scratch in scratches:
                scratch['bbox'] = (
                    scratch['bbox'][0] + x,
                    scratch['bbox'][1] + y,
                    scratch['bbox'][2],
                    scratch['bbox'][3]
                )
                scratch['line'] = [
                    (p[0] + x, p[1] + y) for p in scratch['line']
                ]
                
            return scratches
            
        except Exception as e:
            print(f"스크래치 검출 오류: {e}")
            return []
            
    def _detect_line_defects(self, gray_image: np.ndarray) -> List[dict]:
        """
        선형 결함 검출
        
        Args:
            gray_image: 그레이스케일 이미지
            
        Returns:
            List[dict]: 검출된 선형 결함 정보
        """
        scratches = []
        
        # 1. 엣지 검출
        edges = self._detect_edges(gray_image)
        
        # 2. 선형 구조 검출
        lines = self._detect_lines(edges)
        
        # 3. 스크래치 후보 필터링
        for line in lines:
            if self._is_valid_scratch(line, gray_image):
                scratch_info = self._analyze_scratch(line, gray_image)
                if scratch_info:
                    scratches.append(scratch_info)
                    
        return scratches
        
    def _detect_edges(self, gray_image: np.ndarray) -> np.ndarray:
        """엣지 검출"""
        # 가우시안 블러로 노이즈 제거
        blurred = cv2.GaussianBlur(gray_image, (3, 3), 0)
        
        # Canny 엣지 검출
        edges = cv2.Canny(blurred, 50, 150)
        
        # 모폴로지 연산으로 엣지 강화
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        return edges
        
    def _detect_lines(self, edges: np.ndarray) -> List[np.ndarray]:
        """선 검출"""
        lines = []
        
        # Hough 변환으로 직선 검출
        detected_lines = cv2.HoughLinesP(
            edges, 
            rho=1, 
            theta=np.pi/180, 
            threshold=int(50 * self.sensitivity),
            minLineLength=self.min_length,
            maxLineGap=10
        )
        
        if detected_lines is not None:
            for line in detected_lines:
                x1, y1, x2, y2 = line[0]
                lines.append(np.array([[x1, y1], [x2, y2]]))
                
        return lines
        
    def _is_valid_scratch(self, line: np.ndarray, gray_image: np.ndarray) -> bool:
        """스크래치 유효성 검사"""
        x1, y1 = line[0]
        x2, y2 = line[1]
        
        # 길이 확인
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        if length < self.min_length:
            return False
            
        # 폭 확인 (선 주변의 밝기 변화)
        width = self._measure_line_width(line, gray_image)
        if width > self.max_width:
            return False
            
        # 대비 확인
        contrast = self._measure_contrast(line, gray_image)
        if contrast < self.min_contrast:
            return False
            
        return True
        
    def _measure_line_width(self, line: np.ndarray, gray_image: np.ndarray) -> float:
        """선의 폭 측정"""
        x1, y1 = line[0]
        x2, y2 = line[1]
        
        # 선의 수직 방향으로 프로파일 측정
        length = int(np.sqrt((x2 - x1)**2 + (y2 - y1)**2))
        if length == 0:
            return 0
            
        # 선을 따라 샘플링
        x_coords = np.linspace(x1, x2, length)
        y_coords = np.linspace(y1, y2, length)
        
        # 수직 방향으로 프로파일 측정
        profiles = []
        for i in range(length):
            x, y = int(x_coords[i]), int(y_coords[i])
            if 0 <= x < gray_image.shape[1] and 0 <= y < gray_image.shape[0]:
                # 수직 방향으로 프로파일 추출
                profile = self._extract_perpendicular_profile(
                    (x, y), line, gray_image, max_width=10
                )
                if len(profile) > 0:
                    profiles.append(profile)
                    
        if not profiles:
            return 0
            
        # 평균 폭 계산
        widths = [self._calculate_profile_width(p) for p in profiles]
        return np.mean(widths) if widths else 0
        
    def _extract_perpendicular_profile(self, point: Tuple[int, int], line: np.ndarray, 
                                    gray_image: np.ndarray, max_width: int = 10) -> np.ndarray:
        """점에서 선에 수직인 방향으로 프로파일 추출"""
        x, y = point
        x1, y1 = line[0]
        x2, y2 = line[1]
        
        # 선의 방향 벡터
        dx = x2 - x1
        dy = y2 - y1
        length = np.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return np.array([])
            
        # 수직 방향 벡터
        perp_x = -dy / length
        perp_y = dx / length
        
        # 프로파일 추출
        profile = []
        for i in range(-max_width, max_width + 1):
            px = int(x + i * perp_x)
            py = int(y + i * perp_y)
            
            if 0 <= px < gray_image.shape[1] and 0 <= py < gray_image.shape[0]:
                profile.append(gray_image[py, px])
            else:
                profile.append(0)
                
        return np.array(profile)
        
    def _calculate_profile_width(self, profile: np.ndarray) -> float:
        """프로파일에서 선의 폭 계산"""
        if len(profile) == 0:
            return 0
            
        # 중앙값 기준으로 임계값 설정
        center = len(profile) // 2
        threshold = np.mean(profile) * 0.8
        
        # 엣지 찾기
        left_edge = center
        right_edge = center
        
        for i in range(center, -1, -1):
            if profile[i] < threshold:
                left_edge = i
                break
                
        for i in range(center, len(profile)):
            if profile[i] < threshold:
                right_edge = i
                break
                
        return right_edge - left_edge
        
    def _measure_contrast(self, line: np.ndarray, gray_image: np.ndarray) -> float:
        """선의 대비 측정"""
        x1, y1 = line[0]
        x2, y2 = line[1]
        
        # 선을 따라 샘플링
        length = int(np.sqrt((x2 - x1)**2 + (y2 - y1)**2))
        if length == 0:
            return 0
            
        x_coords = np.linspace(x1, x2, length)
        y_coords = np.linspace(y1, y2, length)
        
        # 선상의 픽셀 값들
        line_pixels = []
        for i in range(length):
            x, y = int(x_coords[i]), int(y_coords[i])
            if 0 <= x < gray_image.shape[1] and 0 <= y < gray_image.shape[0]:
                line_pixels.append(gray_image[y, x])
                
        if len(line_pixels) < 2:
            return 0
            
        # 선 주변의 배경 픽셀들
        background_pixels = []
        for i in range(0, length, max(1, length // 10)):
            x, y = int(x_coords[i]), int(y_coords[i])
            # 선에서 수직으로 떨어진 픽셀들
            for offset in [-3, -2, -1, 1, 2, 3]:
                px = x + offset
                py = y + offset
                if 0 <= px < gray_image.shape[1] and 0 <= py < gray_image.shape[0]:
                    background_pixels.append(gray_image[py, px])
                    
        if len(background_pixels) == 0:
            return 0
            
        # 대비 계산
        line_mean = np.mean(line_pixels)
        background_mean = np.mean(background_pixels)
        contrast = abs(line_mean - background_mean)
        
        return contrast
        
    def _analyze_scratch(self, line: np.ndarray, gray_image: np.ndarray) -> Optional[dict]:
        """스크래치 분석"""
        x1, y1 = line[0]
        x2, y2 = line[1]
        
        # 바운딩 박스 계산
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        
        # 여유 공간 추가
        margin = 5
        bbox = (
            max(0, min_x - margin),
            max(0, min_y - margin),
            min(gray_image.shape[1], max_x + margin) - max(0, min_x - margin),
            min(gray_image.shape[0], max_y + margin) - max(0, min_y - margin)
        )
        
        # 길이 계산
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # 폭 계산
        width = self._measure_line_width(line, gray_image)
        
        # 대비 계산
        contrast = self._measure_contrast(line, gray_image)
        
        # 심각도 평가
        severity = self._calculate_severity(length, width, contrast)
        
        return {
            'type': 'scratch',
            'line': [(x1, y1), (x2, y2)],
            'bbox': bbox,
            'length': length,
            'width': width,
            'contrast': contrast,
            'severity': severity
        }
        
    def _calculate_severity(self, length: float, width: float, contrast: float) -> str:
        """스크래치 심각도 계산"""
        score = 0
        
        # 길이 점수 (0-3)
        if length > 100:
            score += 3
        elif length > 50:
            score += 2
        elif length > 20:
            score += 1
            
        # 폭 점수 (0-2)
        if width > 3:
            score += 2
        elif width > 1:
            score += 1
            
        # 대비 점수 (0-2)
        if contrast > 100:
            score += 2
        elif contrast > 50:
            score += 1
            
        # 심각도 결정
        if score >= 6:
            return 'critical'
        elif score >= 4:
            return 'major'
        elif score >= 2:
            return 'minor'
        else:
            return 'trivial'
            
    def draw_scratches(self, frame: np.ndarray, scratches: List[dict]) -> np.ndarray:
        """검출된 스크래치를 프레임에 그리기"""
        result_frame = frame.copy()
        
        for scratch in scratches:
            line = scratch['line']
            severity = scratch['severity']
            
            # 심각도에 따른 색상 결정
            if severity == 'critical':
                color = (0, 0, 255)  # 빨강
                thickness = 3
            elif severity == 'major':
                color = (0, 165, 255)  # 주황
                thickness = 2
            elif severity == 'minor':
                color = (0, 255, 255)  # 노랑
                thickness = 2
            else:
                color = (0, 255, 0)  # 초록
                thickness = 1
                
            # 스크래치 그리기
            cv2.line(result_frame, line[0], line[1], color, thickness)
            
            # 바운딩 박스 그리기
            bbox = scratch['bbox']
            cv2.rectangle(result_frame, 
                         (bbox[0], bbox[1]), 
                         (bbox[0] + bbox[2], bbox[1] + bbox[3]), 
                         color, 1)
            
            # 정보 텍스트
            info = f"L:{scratch['length']:.1f} W:{scratch['width']:.1f}"
            cv2.putText(result_frame, info, 
                       (bbox[0], bbox[1] - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                       
        return result_frame
        
    def set_detection_parameters(self, min_length: int = None, max_width: int = None,
                                min_contrast: int = None, sensitivity: float = None):
        """검출 파라미터 설정"""
        if min_length is not None:
            self.min_length = min_length
        if max_width is not None:
            self.max_width = max_width
        if min_contrast is not None:
            self.min_contrast = min_contrast
        if sensitivity is not None:
            self.sensitivity = max(0.0, min(1.0, sensitivity))
