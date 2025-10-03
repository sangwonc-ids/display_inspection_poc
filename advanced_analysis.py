#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 디스플레이 분석 모듈
Advanced Display Analysis Module
"""

import cv2
import numpy as np
from scipy import ndimage
from skimage import measure, morphology, filters
from typing import Tuple, List, Dict, Optional
import matplotlib.pyplot as plt

class AdvancedDisplayAnalyzer:
    """고급 디스플레이 분석 클래스"""
    
    def __init__(self):
        self.debug_mode = False
    
    def detect_dead_pixels(self, image: np.ndarray, threshold: float = 0.1) -> Dict:
        """
        데드 픽셀 감지
        
        Args:
            image: 입력 이미지 (BGR)
            threshold: 데드 픽셀 임계값 (0-1)
        
        Returns:
            데드 픽셀 정보 딕셔너리
        """
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 로컬 평균 계산
        kernel = np.ones((5, 5), np.float32) / 25
        local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
        
        # 데드 픽셀 후보 찾기 (로컬 평균과의 차이가 큰 픽셀)
        diff = np.abs(gray.astype(np.float32) - local_mean)
        dead_pixel_mask = diff > (threshold * 255)
        
        # 데드 픽셀 좌표 추출
        dead_pixels = np.where(dead_pixel_mask)
        dead_pixel_coords = list(zip(dead_pixels[1], dead_pixels[0]))  # (x, y)
        
        return {
            'count': len(dead_pixel_coords),
            'coordinates': dead_pixel_coords,
            'mask': dead_pixel_mask,
            'threshold': threshold
        }
    
    def detect_bright_spots(self, image: np.ndarray, min_area: int = 10) -> Dict:
        """
        밝은 점(핫 픽셀) 감지
        
        Args:
            image: 입력 이미지 (BGR)
            min_area: 최소 영역 크기
        
        Returns:
            밝은 점 정보 딕셔너리
        """
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 적응적 임계값 적용
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)
        
        # 연결된 구성 요소 찾기
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
        
        bright_spots = []
        for i in range(1, num_labels):  # 0은 배경
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                x, y = centroids[i]
                bright_spots.append({
                    'center': (int(x), int(y)),
                    'area': int(area),
                    'label': i
                })
        
        return {
            'count': len(bright_spots),
            'spots': bright_spots,
            'labels': labels
        }
    
    def analyze_color_uniformity(self, image: np.ndarray, grid_size: int = 10) -> Dict:
        """
        색상 균일성 분석
        
        Args:
            image: 입력 이미지 (BGR)
            grid_size: 그리드 크기
        
        Returns:
            색상 균일성 분석 결과
        """
        height, width = image.shape[:2]
        
        # 그리드 생성
        grid_h = height // grid_size
        grid_w = width // grid_size
        
        grid_colors = []
        grid_positions = []
        
        for i in range(grid_size):
            for j in range(grid_size):
                # 그리드 영역 추출
                y1 = i * grid_h
                y2 = min((i + 1) * grid_h, height)
                x1 = j * grid_w
                x2 = min((j + 1) * grid_w, width)
                
                grid_region = image[y1:y2, x1:x2]
                
                # 평균 색상 계산
                mean_color = np.mean(grid_region.reshape(-1, 3), axis=0)
                grid_colors.append(mean_color)
                grid_positions.append((x1, y1, x2, y2))
        
        grid_colors = np.array(grid_colors)
        
        # 색상 분산 계산
        color_variance = np.var(grid_colors, axis=0)
        
        # 최대/최소 색상 차이
        max_color = np.max(grid_colors, axis=0)
        min_color = np.min(grid_colors, axis=0)
        color_range = max_color - min_color
        
        return {
            'grid_colors': grid_colors.tolist(),
            'grid_positions': grid_positions,
            'color_variance': color_variance.tolist(),
            'color_range': color_range.tolist(),
            'uniformity_score': 1.0 - (np.mean(color_variance) / 255.0)
        }
    
    def detect_mura_defects(self, image: np.ndarray, sigma: float = 1.0) -> Dict:
        """
        무라(Mura) 결함 감지 (불균일한 밝기 영역)
        
        Args:
            image: 입력 이미지 (BGR)
            sigma: 가우시안 필터 시그마
        
        Returns:
            무라 결함 정보
        """
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
        
        # 가우시안 필터 적용 (배경 제거)
        background = cv2.GaussianBlur(gray, (0, 0), sigma)
        mura_image = gray - background
        
        # 임계값 적용
        threshold = np.std(mura_image) * 2
        mura_mask = np.abs(mura_image) > threshold
        
        # 모폴로지 연산으로 노이즈 제거
        kernel = np.ones((5, 5), np.uint8)
        mura_mask = cv2.morphologyEx(mura_mask.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        mura_mask = cv2.morphologyEx(mura_mask, cv2.MORPH_OPEN, kernel)
        
        # 연결된 구성 요소 분석
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mura_mask, connectivity=8)
        
        mura_defects = []
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area > 50:  # 최소 영역 크기
                x, y = centroids[i]
                mura_defects.append({
                    'center': (int(x), int(y)),
                    'area': int(area),
                    'intensity': float(np.mean(mura_image[labels == i]))
                })
        
        return {
            'count': len(mura_defects),
            'defects': mura_defects,
            'mask': mura_mask,
            'mura_image': mura_image
        }
    
    def analyze_pixel_response(self, image: np.ndarray, test_pattern: Optional[np.ndarray] = None) -> Dict:
        """
        픽셀 응답 분석
        
        Args:
            image: 입력 이미지 (BGR)
            test_pattern: 테스트 패턴 (선택사항)
        
        Returns:
            픽셀 응답 분석 결과
        """
        # 그레이스케일 변환
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 히스토그램 분석
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # 픽셀 강도 분포 통계
        pixel_intensities = gray.flatten()
        
        # 응답 곡선 분석 (선형성)
        if test_pattern is not None:
            # 테스트 패턴과의 상관관계 분석
            correlation = cv2.matchTemplate(gray, test_pattern, cv2.TM_CCOEFF_NORMED)
            response_quality = np.max(correlation)
        else:
            response_quality = None
        
        return {
            'histogram': hist.flatten().tolist(),
            'mean_intensity': float(np.mean(pixel_intensities)),
            'std_intensity': float(np.std(pixel_intensities)),
            'min_intensity': int(np.min(pixel_intensities)),
            'max_intensity': int(np.max(pixel_intensities)),
            'response_quality': response_quality,
            'dynamic_range': int(np.max(pixel_intensities)) - int(np.min(pixel_intensities))
        }
    
    def create_analysis_report(self, image: np.ndarray) -> Dict:
        """
        종합 분석 보고서 생성
        
        Args:
            image: 입력 이미지 (BGR)
        
        Returns:
            종합 분석 결과
        """
        report = {
            'timestamp': None,  # 호출 시점에서 설정
            'image_info': {
                'shape': image.shape,
                'dtype': str(image.dtype)
            },
            'dead_pixels': self.detect_dead_pixels(image),
            'bright_spots': self.detect_bright_spots(image),
            'color_uniformity': self.analyze_color_uniformity(image),
            'mura_defects': self.detect_mura_defects(image),
            'pixel_response': self.analyze_pixel_response(image)
        }
        
        # 전체 품질 점수 계산
        quality_score = self.calculate_quality_score(report)
        report['overall_quality_score'] = quality_score
        
        return report
    
    def calculate_quality_score(self, report: Dict) -> float:
        """
        전체 품질 점수 계산 (0-100)
        
        Args:
            report: 분석 보고서
        
        Returns:
            품질 점수 (0-100)
        """
        score = 100.0
        
        # 데드 픽셀 감점
        dead_pixel_count = report['dead_pixels']['count']
        score -= min(dead_pixel_count * 0.1, 20)  # 최대 20점 감점
        
        # 밝은 점 감점
        bright_spot_count = report['bright_spots']['count']
        score -= min(bright_spot_count * 0.5, 15)  # 최대 15점 감점
        
        # 색상 균일성 감점
        uniformity_score = report['color_uniformity']['uniformity_score']
        score -= (1 - uniformity_score) * 20  # 최대 20점 감점
        
        # 무라 결함 감점
        mura_count = report['mura_defects']['count']
        score -= min(mura_count * 1.0, 25)  # 최대 25점 감점
        
        # 동적 범위 감점
        dynamic_range = report['pixel_response']['dynamic_range']
        if dynamic_range < 200:
            score -= (200 - dynamic_range) * 0.1  # 최대 20점 감점
        
        return max(0, score)
    
    def visualize_results(self, image: np.ndarray, report: Dict, save_path: Optional[str] = None):
        """
        분석 결과 시각화
        
        Args:
            image: 원본 이미지
            report: 분석 보고서
            save_path: 저장 경로 (선택사항)
        """
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle('디스플레이 분석 결과', fontsize=16)
        
        # 원본 이미지
        axes[0, 0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title('원본 이미지')
        axes[0, 0].axis('off')
        
        # 데드 픽셀
        dead_pixel_mask = report['dead_pixels']['mask']
        axes[0, 1].imshow(dead_pixel_mask, cmap='hot')
        axes[0, 1].set_title(f'데드 픽셀 ({report["dead_pixels"]["count"]}개)')
        axes[0, 1].axis('off')
        
        # 밝은 점
        bright_labels = report['bright_spots']['labels']
        axes[0, 2].imshow(bright_labels, cmap='viridis')
        axes[0, 2].set_title(f'밝은 점 ({report["bright_spots"]["count"]}개)')
        axes[0, 2].axis('off')
        
        # 색상 균일성
        grid_colors = np.array(report['color_uniformity']['grid_colors'])
        grid_image = grid_colors.reshape(10, 10, 3) / 255.0
        axes[1, 0].imshow(grid_image)
        axes[1, 0].set_title(f'색상 균일성 ({report["color_uniformity"]["uniformity_score"]:.2f})')
        axes[1, 0].axis('off')
        
        # 무라 결함
        mura_mask = report['mura_defects']['mask']
        axes[1, 1].imshow(mura_mask, cmap='gray')
        axes[1, 1].set_title(f'무라 결함 ({report["mura_defects"]["count"]}개)')
        axes[1, 1].axis('off')
        
        # 픽셀 응답 히스토그램
        hist = report['pixel_response']['histogram']
        axes[1, 2].plot(hist)
        axes[1, 2].set_title('픽셀 강도 분포')
        axes[1, 2].set_xlabel('픽셀 강도')
        axes[1, 2].set_ylabel('빈도')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()

# 사용 예제
if __name__ == "__main__":
    # 테스트 이미지 로드
    test_image = cv2.imread("test_display.jpg")
    
    if test_image is not None:
        analyzer = AdvancedDisplayAnalyzer()
        report = analyzer.create_analysis_report(test_image)
        
        print(f"전체 품질 점수: {report['overall_quality_score']:.1f}/100")
        print(f"데드 픽셀: {report['dead_pixels']['count']}개")
        print(f"밝은 점: {report['bright_spots']['count']}개")
        print(f"무라 결함: {report['mura_defects']['count']}개")
        
        # 결과 시각화
        analyzer.visualize_results(test_image, report)
    else:
        print("테스트 이미지를 찾을 수 없습니다.")
