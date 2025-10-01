#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엣지 디텍션 모듈
Edge Detection Module

디스플레이 패널의 사각형 엣지 감지
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
import math


class EdgeDetection:
    def __init__(self):
        """엣지 디텍션 모듈 초기화"""
        self.min_area = 10000  # 최소 면적
        self.max_area = 2000000  # 최대 면적
        self.approx_epsilon = 0.02  # 근사화 정확도
        self.min_aspect_ratio = 0.5  # 최소 종횡비
        self.max_aspect_ratio = 3.0  # 최대 종횡비
        
    def detect_display(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        디스플레이 패널 감지 (패턴이 표시된 영역 감지)
        
        Args:
            frame: 입력 프레임
            
        Returns:
            np.ndarray: 감지된 사각형 좌표 (x, y, w, h) 또는 None
        """
        if frame is None:
            return None
            
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 노이즈 제거
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 밝은 영역 찾기 (패턴이 표시된 영역)
            # 임계값을 높여서 밝은 영역만 감지
            _, bright_mask = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)
            
            # 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((5, 5), np.uint8)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
            
            # 컨투어 찾기
            contours, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            print(f"감지된 컨투어 개수: {len(contours)}")
            
            # 가장 큰 밝은 영역 찾기
            if contours:
                # 면적이 큰 순으로 정렬
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                # 상위 5개 컨투어 중에서 가장 사각형에 가까운 것 선택
                best_rectangle = None
                best_score = 0
                
                for i, contour in enumerate(contours[:5]):
                    area = cv2.contourArea(contour)
                    if area < 10000:  # 너무 작은 영역 제외
                        continue
                        
                    # 바운딩 박스
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # 종횡비 확인 (디스플레이에 적합한 비율)
                    aspect_ratio = w / h if h > 0 else 0
                    if 0.5 <= aspect_ratio <= 2.0:  # 디스플레이 비율
                        # 사각형에 가까운 정도 계산
                        rect_area = w * h
                        extent = area / rect_area if rect_area > 0 else 0
                        
                        # 점수 계산 (면적 + 사각형 정도)
                        score = area * extent
                        
                        if score > best_score:
                            best_score = score
                            best_rectangle = (x, y, w, h)
                            
                if best_rectangle:
                    print(f"선택된 패널 영역: {best_rectangle}")
                    return best_rectangle
                    
            # 대안: 중앙 영역 사용
            h, w = frame.shape[:2]
            center_x, center_y = w // 2, h // 2
            panel_w, panel_h = min(w * 0.8, h * 0.8), min(w * 0.8, h * 0.8)
            fallback_rectangle = (
                int(center_x - panel_w // 2),
                int(center_y - panel_h // 2),
                int(panel_w),
                int(panel_h)
            )
            print(f"중앙 영역 사용: {fallback_rectangle}")
            return fallback_rectangle
                
        except Exception as e:
            print(f"디스플레이 감지 오류: {e}")
            return None
            
    def _find_rectangles(self, contours: List[np.ndarray]) -> List[Tuple[int, int, int, int]]:
        """
        컨투어에서 사각형 찾기
        
        Args:
            contours: 컨투어 리스트
            
        Returns:
            List[Tuple[int, int, int, int]]: 사각형 좌표 리스트 (x, y, w, h)
        """
        rectangles = []
        
        for i, contour in enumerate(contours):
            # 면적 필터링 (더 관대하게)
            area = cv2.contourArea(contour)
            print(f"컨투어 {i}: 면적 = {area}")
            
            if area < 1000:  # 최소 면적을 낮춤
                continue
                
            # 근사화 (더 관대하게)
            epsilon = 0.05 * cv2.arcLength(contour, True)  # 더 관대한 근사화
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            print(f"컨투어 {i}: 근사 꼭짓점 개수 = {len(approx)}")
            
            # 사각형인지 확인 (4개 꼭짓점 또는 3-6개 꼭짓점 허용)
            if 3 <= len(approx) <= 6:
                # 바운딩 박스 계산
                x, y, w, h = cv2.boundingRect(contour)
                
                # 종횡비 확인 (더 관대하게)
                aspect_ratio = w / h if h > 0 else 0
                print(f"컨투어 {i}: 종횡비 = {aspect_ratio:.2f}, 크기 = {w}x{h}")
                
                if 0.3 <= aspect_ratio <= 5.0:  # 더 관대한 종횡비
                    rectangles.append((x, y, w, h))
                    print(f"컨투어 {i}: 사각형으로 인식됨")
                    
        return rectangles
        
    def draw_detection_result(self, frame: np.ndarray, rectangle: np.ndarray) -> np.ndarray:
        """
        감지 결과를 프레임에 그리기
        
        Args:
            frame: 원본 프레임
            rectangle: 감지된 사각형 (x, y, w, h)
            
        Returns:
            np.ndarray: 결과가 그려진 프레임
        """
        if rectangle is None or len(rectangle) != 4:
            return frame
            
        x, y, w, h = rectangle
        
        # 사각형 그리기
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # 모서리 표시
        corner_size = 20
        corners = [
            (x, y), (x + w, y), (x, y + h), (x + w, y + h)
        ]
        
        for corner in corners:
            cv2.circle(frame, corner, corner_size, (0, 255, 0), 2)
            
        # 중앙점 표시
        center_x = x + w // 2
        center_y = y + h // 2
        cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
        
        # 텍스트 정보 표시
        info_text = f"Panel {w}x{h}"
        cv2.putText(frame, info_text, (x, y - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
        
    def refine_detection(self, frame: np.ndarray, initial_rectangle: np.ndarray) -> Optional[np.ndarray]:
        """
        감지 결과 정밀화
        
        Args:
            frame: 입력 프레임
            initial_rectangle: 초기 감지된 사각형
            
        Returns:
            np.ndarray: 정밀화된 사각형 좌표
        """
        if initial_rectangle is None:
            return None
            
        x, y, w, h = initial_rectangle
        
        # ROI 추출
        roi = frame[y:y+h, x:x+w]
        
        # 그레이스케일 변환
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 적응형 임계값
        thresh = cv2.adaptiveThreshold(gray_roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        # 엣지 검출
        edges = cv2.Canny(thresh, 50, 150)
        
        # 컨투어 찾기
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # 가장 큰 컨투어 선택
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 바운딩 박스 계산
            x_new, y_new, w_new, h_new = cv2.boundingRect(largest_contour)
            
            # 원본 좌표로 변환
            return (x + x_new, y + y_new, w_new, h_new)
            
        return initial_rectangle
        
    def get_display_center(self, rectangle: np.ndarray) -> Tuple[int, int]:
        """
        디스플레이 중심점 계산
        
        Args:
            rectangle: 사각형 좌표 (x, y, w, h)
            
        Returns:
            Tuple[int, int]: 중심점 좌표 (x, y)
        """
        if rectangle is None or len(rectangle) != 4:
            return (0, 0)
            
        x, y, w, h = rectangle
        center_x = x + w // 2
        center_y = y + h // 2
        
        return (center_x, center_y)
        
    def get_display_area(self, rectangle: np.ndarray) -> int:
        """
        디스플레이 면적 계산
        
        Args:
            rectangle: 사각형 좌표 (x, y, w, h)
            
        Returns:
            int: 면적
        """
        if rectangle is None or len(rectangle) != 4:
            return 0
            
        x, y, w, h = rectangle
        return w * h
        
    def is_valid_display(self, rectangle: np.ndarray, frame_shape: Tuple[int, int]) -> bool:
        """
        감지된 사각형이 유효한 디스플레이인지 확인
        
        Args:
            rectangle: 사각형 좌표 (x, y, w, h)
            frame_shape: 프레임 크기 (height, width)
            
        Returns:
            bool: 유효성 여부
        """
        if rectangle is None or len(rectangle) != 4:
            return False
            
        x, y, w, h = rectangle
        frame_height, frame_width = frame_shape[:2]
        
        # 경계 확인
        if x < 0 or y < 0 or x + w > frame_width or y + h > frame_height:
            return False
            
        # 크기 확인
        area = w * h
        if area < self.min_area or area > self.max_area:
            return False
            
        # 종횡비 확인
        aspect_ratio = w / h
        if aspect_ratio < self.min_aspect_ratio or aspect_ratio > self.max_aspect_ratio:
            return False
            
        return True
        
    def set_detection_parameters(self, min_area: int = None, max_area: int = None,
                                min_aspect_ratio: float = None, max_aspect_ratio: float = None):
        """
        감지 파라미터 설정
        
        Args:
            min_area: 최소 면적
            max_area: 최대 면적
            min_aspect_ratio: 최소 종횡비
            max_aspect_ratio: 최대 종횡비
        """
        if min_area is not None:
            self.min_area = min_area
        if max_area is not None:
            self.max_area = max_area
        if min_aspect_ratio is not None:
            self.min_aspect_ratio = min_aspect_ratio
        if max_aspect_ratio is not None:
            self.max_aspect_ratio = max_aspect_ratio
