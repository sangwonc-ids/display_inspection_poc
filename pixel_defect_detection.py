#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
픽셀 결함 검사 모듈
Pixel Defect Detection Module

데드픽셀, 핫픽셀, 스티킹픽셀 검출 및 분석
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
from scipy import ndimage
from skimage import filters, morphology, measure
# peak_local_maxima는 현재 사용하지 않으므로 import 제거


class PixelDefectDetection:
    def __init__(self):
        """픽셀 결함 검사 모듈 초기화"""
        self.dead_pixel_threshold = 10      # 데드픽셀 임계값
        self.hot_pixel_threshold = 245      # 핫픽셀 임계값
        self.stuck_pixel_threshold = 0.95   # 스티킹픽셀 임계값
        self.min_cluster_size = 2           # 최소 클러스터 크기
        self.max_defect_density = 0.01      # 최대 결함 밀도
        
    def detect_defects(self, frame: np.ndarray, display_region: np.ndarray) -> Dict[str, List[dict]]:
        """
        픽셀 결함 검출
        
        Args:
            frame: 입력 프레임
            display_region: 디스플레이 영역 (x, y, w, h)
            
        Returns:
            Dict[str, List[dict]]: 검출된 결함 정보
        """
        if frame is None or display_region is None:
            return {'dead_pixels': [], 'hot_pixels': [], 'stuck_pixels': []}
            
        try:
            # 디스플레이 영역 추출
            x, y, w, h = display_region
            roi = frame[y:y+h, x:x+w]
            
            if roi.size == 0:
                return {'dead_pixels': [], 'hot_pixels': [], 'stuck_pixels': []}
                
            # 그레이스케일 변환
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # 각종 결함 검출
            dead_pixels = self._detect_dead_pixels(gray)
            hot_pixels = self._detect_hot_pixels(gray)
            stuck_pixels = self._detect_stuck_pixels(gray)
            
            # 결과를 원본 좌표계로 변환
            for defect in dead_pixels + hot_pixels + stuck_pixels:
                defect['position'] = (defect['position'][0] + x, defect['position'][1] + y)
                if 'bbox' in defect:
                    bbox = defect['bbox']
                    defect['bbox'] = (bbox[0] + x, bbox[1] + y, bbox[2], bbox[3])
                    
            return {
                'dead_pixels': dead_pixels,
                'hot_pixels': hot_pixels,
                'stuck_pixels': stuck_pixels
            }
            
        except Exception as e:
            print(f"픽셀 결함 검출 오류: {e}")
            return {'dead_pixels': [], 'hot_pixels': [], 'stuck_pixels': []}
            
    def _detect_dead_pixels(self, gray_image: np.ndarray) -> List[dict]:
        """데드픽셀 검출"""
        dead_pixels = []
        
        # 임계값 이하 픽셀 찾기
        dead_mask = gray_image < self.dead_pixel_threshold
        
        # 노이즈 제거
        dead_mask = morphology.remove_small_objects(dead_mask, min_size=self.min_cluster_size)
        
        # 연결된 영역 찾기
        labeled = measure.label(dead_mask)
        regions = measure.regionprops(labeled)
        
        for region in regions:
            # 영역 중심점
            center_y, center_x = region.centroid
            center_x, center_y = int(center_x), int(center_y)
            
            # 바운딩 박스
            min_row, min_col, max_row, max_col = region.bbox
            bbox = (min_col, min_row, max_col - min_col, max_row - min_row)
            
            # 픽셀 값 분석
            pixel_value = gray_image[center_y, center_x]
            
            # 심각도 평가
            severity = self._evaluate_dead_pixel_severity(region.area, pixel_value)
            
            dead_pixels.append({
                'type': 'dead_pixel',
                'position': (center_x, center_y),
                'bbox': bbox,
                'area': region.area,
                'pixel_value': pixel_value,
                'severity': severity
            })
            
        return dead_pixels
        
    def _detect_hot_pixels(self, gray_image: np.ndarray) -> List[dict]:
        """핫픽셀 검출"""
        hot_pixels = []
        
        # 임계값 이상 픽셀 찾기
        hot_mask = gray_image > self.hot_pixel_threshold
        
        # 노이즈 제거
        hot_mask = morphology.remove_small_objects(hot_mask, min_size=self.min_cluster_size)
        
        # 연결된 영역 찾기
        labeled = measure.label(hot_mask)
        regions = measure.regionprops(labeled)
        
        for region in regions:
            # 영역 중심점
            center_y, center_x = region.centroid
            center_x, center_y = int(center_x), int(center_y)
            
            # 바운딩 박스
            min_row, min_col, max_row, max_col = region.bbox
            bbox = (min_col, min_row, max_col - min_col, max_row - min_row)
            
            # 픽셀 값 분석
            pixel_value = gray_image[center_y, center_x]
            
            # 심각도 평가
            severity = self._evaluate_hot_pixel_severity(region.area, pixel_value)
            
            hot_pixels.append({
                'type': 'hot_pixel',
                'position': (center_x, center_y),
                'bbox': bbox,
                'area': region.area,
                'pixel_value': pixel_value,
                'severity': severity
            })
            
        return hot_pixels
        
    def _detect_stuck_pixels(self, gray_image: np.ndarray) -> List[dict]:
        """스티킹픽셀 검출"""
        stuck_pixels = []
        
        try:
            # 간단한 방법으로 밝은 픽셀 찾기
            # 임계값 이상의 픽셀들을 찾아서 주변과 비교
            bright_pixels = gray_image > 200
            
            # 연결된 영역 찾기
            labeled = measure.label(bright_pixels)
            regions = measure.regionprops(labeled)
            
            for region in regions:
                if region.area < 5:  # 너무 작은 영역은 제외
                    continue
                    
                # 영역 중심점
                center_y, center_x = region.centroid
                center_x, center_y = int(center_x), int(center_y)
                
                # 주변 픽셀과의 차이 계산
                neighborhood = gray_image[max(0, center_y-2):min(gray_image.shape[0], center_y+3),
                                       max(0, center_x-2):min(gray_image.shape[1], center_x+3)]
                
                if neighborhood.size == 0:
                    continue
                    
                center_value = gray_image[center_y, center_x]
                neighborhood_mean = np.mean(neighborhood)
                
                # 스티킹픽셀 조건 확인
                if center_value > neighborhood_mean * 1.5:
                    # 심각도 평가
                    severity = self._evaluate_stuck_pixel_severity(center_value, neighborhood_mean)
                    
                    # 바운딩 박스
                    min_row, min_col, max_row, max_col = region.bbox
                    bbox = (min_col, min_row, max_col - min_col, max_row - min_row)
                    
                    stuck_pixels.append({
                        'type': 'stuck_pixel',
                        'position': (center_x, center_y),
                        'bbox': bbox,
                        'pixel_value': center_value,
                        'neighborhood_mean': neighborhood_mean,
                        'severity': severity
                    })
        except Exception as e:
            print(f"스티킹픽셀 검출 오류: {e}")
                    
        return stuck_pixels
        
    def _evaluate_dead_pixel_severity(self, area: int, pixel_value: int) -> str:
        """데드픽셀 심각도 평가"""
        if area > 10:
            return 'critical'
        elif area > 5:
            return 'major'
        elif area > 2:
            return 'minor'
        else:
            return 'trivial'
            
    def _evaluate_hot_pixel_severity(self, area: int, pixel_value: int) -> str:
        """핫픽셀 심각도 평가"""
        if area > 10:
            return 'critical'
        elif area > 5:
            return 'major'
        elif area > 2:
            return 'minor'
        else:
            return 'trivial'
            
    def _evaluate_stuck_pixel_severity(self, pixel_value: int, neighborhood_mean: float) -> str:
        """스티킹픽셀 심각도 평가"""
        ratio = pixel_value / neighborhood_mean if neighborhood_mean > 0 else 0
        
        if ratio > 3.0:
            return 'critical'
        elif ratio > 2.0:
            return 'major'
        elif ratio > 1.5:
            return 'minor'
        else:
            return 'trivial'
            
    def draw_defects(self, frame: np.ndarray, defects: Dict[str, List[dict]]) -> np.ndarray:
        """검출된 결함을 프레임에 그리기"""
        result_frame = frame.copy()
        
        # 데드픽셀 그리기
        for defect in defects.get('dead_pixels', []):
            pos = defect['position']
            severity = defect['severity']
            
            color = self._get_severity_color(severity)
            cv2.circle(result_frame, pos, 3, color, -1)
            cv2.putText(result_frame, 'D', (pos[0]-5, pos[1]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                       
        # 핫픽셀 그리기
        for defect in defects.get('hot_pixels', []):
            pos = defect['position']
            severity = defect['severity']
            
            color = self._get_severity_color(severity)
            cv2.circle(result_frame, pos, 3, color, -1)
            cv2.putText(result_frame, 'H', (pos[0]-5, pos[1]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                       
        # 스티킹픽셀 그리기
        for defect in defects.get('stuck_pixels', []):
            pos = defect['position']
            severity = defect['severity']
            
            color = self._get_severity_color(severity)
            cv2.circle(result_frame, pos, 3, color, -1)
            cv2.putText(result_frame, 'S', (pos[0]-5, pos[1]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                       
        return result_frame
        
    def _get_severity_color(self, severity: str) -> Tuple[int, int, int]:
        """심각도에 따른 색상 반환"""
        color_map = {
            'critical': (0, 0, 255),    # 빨강
            'major': (0, 165, 255),     # 주황
            'minor': (0, 255, 255),    # 노랑
            'trivial': (0, 255, 0)      # 초록
        }
        return color_map.get(severity, (128, 128, 128))
        
    def calculate_quality_grade(self, defects: Dict[str, List[dict]], 
                              display_area: int) -> Dict[str, any]:
        """품질 등급 계산"""
        dead_count = len(defects.get('dead_pixels', []))
        hot_count = len(defects.get('hot_pixels', []))
        stuck_count = len(defects.get('stuck_pixels', []))
        
        total_defects = dead_count + hot_count + stuck_count
        defect_density = total_defects / display_area if display_area > 0 else 0
        
        # 등급 계산
        if dead_count <= 1 and hot_count <= 1 and total_defects <= 2:
            grade = 'A'
            score = 90 + (10 * (1 - defect_density))
        elif dead_count <= 3 and hot_count <= 3 and total_defects <= 6:
            grade = 'B'
            score = 80 + (10 * (1 - defect_density))
        elif dead_count <= 5 and hot_count <= 5 and total_defects <= 10:
            grade = 'C'
            score = 70 + (10 * (1 - defect_density))
        elif dead_count <= 10 and hot_count <= 10 and total_defects <= 20:
            grade = 'D'
            score = 60 + (10 * (1 - defect_density))
        else:
            grade = 'F'
            score = 50 + (10 * (1 - defect_density))
            
        return {
            'grade': grade,
            'score': max(0, min(100, score)),
            'dead_pixels': dead_count,
            'hot_pixels': hot_count,
            'stuck_pixels': stuck_count,
            'total_defects': total_defects,
            'defect_density': defect_density
        }
        
    def generate_defect_report(self, defects: Dict[str, List[dict]], 
                              quality_grade: Dict[str, any]) -> str:
        """결함 보고서 생성"""
        report = f"""
=== 픽셀 결함 검사 보고서 ===

품질 등급: {quality_grade['grade']}급
점수: {quality_grade['score']:.1f}점

결함 통계:
- 데드픽셀: {quality_grade['dead_pixels']}개
- 핫픽셀: {quality_grade['hot_pixels']}개
- 스티킹픽셀: {quality_grade['stuck_pixels']}개
- 총 결함: {quality_grade['total_defects']}개
- 결함 밀도: {quality_grade['defect_density']:.6f}

상세 결함 정보:
"""
        
        # 데드픽셀 상세 정보
        if defects.get('dead_pixels'):
            report += "\n데드픽셀:\n"
            for i, defect in enumerate(defects['dead_pixels'], 1):
                report += f"  {i}. 위치: {defect['position']}, 심각도: {defect['severity']}\n"
                
        # 핫픽셀 상세 정보
        if defects.get('hot_pixels'):
            report += "\n핫픽셀:\n"
            for i, defect in enumerate(defects['hot_pixels'], 1):
                report += f"  {i}. 위치: {defect['position']}, 심각도: {defect['severity']}\n"
                
        # 스티킹픽셀 상세 정보
        if defects.get('stuck_pixels'):
            report += "\n스티킹픽셀:\n"
            for i, defect in enumerate(defects['stuck_pixels'], 1):
                report += f"  {i}. 위치: {defect['position']}, 심각도: {defect['severity']}\n"
                
        return report
        
    def set_detection_parameters(self, dead_threshold: int = None, hot_threshold: int = None,
                                stuck_threshold: float = None, min_cluster_size: int = None):
        """검출 파라미터 설정"""
        if dead_threshold is not None:
            self.dead_pixel_threshold = dead_threshold
        if hot_threshold is not None:
            self.hot_pixel_threshold = hot_threshold
        if stuck_threshold is not None:
            self.stuck_pixel_threshold = stuck_threshold
        if min_cluster_size is not None:
            self.min_cluster_size = min_cluster_size
