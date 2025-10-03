#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
검사 제어 모듈
Inspection Controller Module

전체 검사 프로세스 제어 및 결과 관리
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import os
from dataclasses import dataclass


@dataclass
class InspectionResult:
    """검사 결과 데이터 클래스"""
    timestamp: datetime
    display_region: Tuple[int, int, int, int]
    scratches: List[dict]
    pixel_defects: Dict[str, List[dict]]
    quality_grade: Dict[str, any]
    test_pattern: str
    inspection_time: float


class InspectionController:
    def __init__(self):
        """검사 제어 모듈 초기화"""
        self.current_inspection = None
        self.inspection_history = []
        self.results_directory = "inspection_results"
        
        # 결과 디렉토리 생성
        if not os.path.exists(self.results_directory):
            os.makedirs(self.results_directory)
            
    def start_inspection(self, display_region: Tuple[int, int, int, int], 
                        test_pattern: str = "solid_red") -> bool:
        """
        검사 시작
        
        Args:
            display_region: 디스플레이 영역 (x, y, w, h)
            test_pattern: 테스트 패턴 타입
            
        Returns:
            bool: 검사 시작 성공 여부
        """
        try:
            self.current_inspection = {
                'start_time': datetime.now(),
                'display_region': display_region,
                'test_pattern': test_pattern,
                'status': 'running'
            }
            return True
        except Exception as e:
            print(f"검사 시작 오류: {e}")
            return False
            
    def stop_inspection(self) -> Optional[InspectionResult]:
        """
        검사 중지
        
        Returns:
            InspectionResult: 검사 결과
        """
        if self.current_inspection is None:
            return None
            
        try:
            end_time = datetime.now()
            start_time = self.current_inspection['start_time']
            inspection_time = (end_time - start_time).total_seconds()
            
            # 검사 결과 생성
            result = InspectionResult(
                timestamp=end_time,
                display_region=self.current_inspection['display_region'],
                scratches=self.current_inspection.get('scratches', []),
                pixel_defects=self.current_inspection.get('pixel_defects', {}),
                quality_grade=self.current_inspection.get('quality_grade', {}),
                test_pattern=self.current_inspection['test_pattern'],
                inspection_time=inspection_time
            )
            
            # 검사 기록에 추가
            self.inspection_history.append(result)
            
            # 현재 검사 초기화
            self.current_inspection = None
            
            return result
            
        except Exception as e:
            print(f"검사 중지 오류: {e}")
            return None
            
    def update_inspection_results(self, scratches: List[dict] = None,
                                 pixel_defects: Dict[str, List[dict]] = None,
                                 quality_grade: Dict[str, any] = None):
        """검사 결과 업데이트"""
        if self.current_inspection is None:
            return
            
        if scratches is not None:
            self.current_inspection['scratches'] = scratches
        if pixel_defects is not None:
            self.current_inspection['pixel_defects'] = pixel_defects
        if quality_grade is not None:
            self.current_inspection['quality_grade'] = quality_grade
            
    def get_current_inspection_status(self) -> Dict[str, any]:
        """현재 검사 상태 반환"""
        if self.current_inspection is None:
            return {'status': 'idle'}
            
        return {
            'status': self.current_inspection['status'],
            'start_time': self.current_inspection['start_time'],
            'elapsed_time': (datetime.now() - self.current_inspection['start_time']).total_seconds(),
            'display_region': self.current_inspection['display_region'],
            'test_pattern': self.current_inspection['test_pattern']
        }
        
    def get_inspection_history(self) -> List[InspectionResult]:
        """검사 기록 반환"""
        return self.inspection_history
        
    def save_inspection_result(self, result: InspectionResult, filename: str = None) -> bool:
        """
        검사 결과 저장
        
        Args:
            result: 검사 결과
            filename: 저장할 파일명 (None이면 자동 생성)
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            if filename is None:
                timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
                filename = f"inspection_{timestamp}.json"
                
            filepath = os.path.join(self.results_directory, filename)
            
            # 결과를 딕셔너리로 변환
            result_dict = {
                'timestamp': result.timestamp.isoformat(),
                'display_region': result.display_region,
                'scratches': result.scratches,
                'pixel_defects': result.pixel_defects,
                'quality_grade': result.quality_grade,
                'test_pattern': result.test_pattern,
                'inspection_time': result.inspection_time
            }
            
            # JSON 파일로 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, ensure_ascii=False, indent=2)
                
            return True
            
        except Exception as e:
            print(f"검사 결과 저장 오류: {e}")
            return False
            
    def load_inspection_result(self, filename: str) -> Optional[InspectionResult]:
        """
        검사 결과 로드
        
        Args:
            filename: 로드할 파일명
            
        Returns:
            InspectionResult: 검사 결과
        """
        try:
            filepath = os.path.join(self.results_directory, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                result_dict = json.load(f)
                
            # 딕셔너리를 InspectionResult로 변환
            result = InspectionResult(
                timestamp=datetime.fromisoformat(result_dict['timestamp']),
                display_region=tuple(result_dict['display_region']),
                scratches=result_dict['scratches'],
                pixel_defects=result_dict['pixel_defects'],
                quality_grade=result_dict['quality_grade'],
                test_pattern=result_dict['test_pattern'],
                inspection_time=result_dict['inspection_time']
            )
            
            return result
            
        except Exception as e:
            print(f"검사 결과 로드 오류: {e}")
            return None
            
    def get_quality_statistics(self) -> Dict[str, any]:
        """품질 통계 반환"""
        if not self.inspection_history:
            return {}
            
        grades = [result.quality_grade.get('grade', 'F') for result in self.inspection_history]
        scores = [result.quality_grade.get('score', 0) for result in self.inspection_history]
        
        grade_counts = {}
        for grade in ['A', 'B', 'C', 'D', 'F']:
            grade_counts[grade] = grades.count(grade)
            
        return {
            'total_inspections': len(self.inspection_history),
            'grade_distribution': grade_counts,
            'average_score': np.mean(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'max_score': max(scores) if scores else 0
        }
        
    def generate_inspection_report(self, result: InspectionResult) -> str:
        """검사 보고서 생성"""
        report = f"""
=== 디스플레이 품질 검사 보고서 ===

검사 일시: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
검사 시간: {result.inspection_time:.2f}초
테스트 패턴: {result.test_pattern}
디스플레이 영역: {result.display_region}

=== 품질 등급 ===
등급: {result.quality_grade.get('grade', 'N/A')}급
점수: {result.quality_grade.get('score', 0):.1f}점

=== 결함 통계 ===
데드픽셀: {result.quality_grade.get('dead_pixels', 0)}개
핫픽셀: {result.quality_grade.get('hot_pixels', 0)}개
스티킹픽셀: {result.quality_grade.get('stuck_pixels', 0)}개
총 결함: {result.quality_grade.get('total_defects', 0)}개
결함 밀도: {result.quality_grade.get('defect_density', 0):.6f}

=== 스크래치 검사 ===
검출된 스크래치: {len(result.scratches)}개
"""
        
        # 스크래치 상세 정보
        if result.scratches:
            report += "\n스크래치 상세:\n"
            for i, scratch in enumerate(result.scratches, 1):
                report += f"  {i}. 길이: {scratch.get('length', 0):.1f}px, "
                report += f"폭: {scratch.get('width', 0):.1f}px, "
                report += f"심각도: {scratch.get('severity', 'N/A')}\n"
        else:
            report += "스크래치 없음\n"
            
        # 픽셀 결함 상세 정보
        if result.pixel_defects:
            report += "\n=== 픽셀 결함 상세 ===\n"
            
            for defect_type, defects in result.pixel_defects.items():
                if defects:
                    report += f"\n{defect_type}:\n"
                    for i, defect in enumerate(defects, 1):
                        report += f"  {i}. 위치: {defect.get('position', 'N/A')}, "
                        report += f"심각도: {defect.get('severity', 'N/A')}\n"
                        
        return report
        
    def export_results_to_csv(self, filename: str = None) -> bool:
        """
        결과를 CSV 파일로 내보내기
        
        Args:
            filename: 저장할 파일명
            
        Returns:
            bool: 내보내기 성공 여부
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"inspection_results_{timestamp}.csv"
                
            filepath = os.path.join(self.results_directory, filename)
            
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 헤더 작성
                writer.writerow([
                    'Timestamp', 'Grade', 'Score', 'Dead Pixels', 'Hot Pixels',
                    'Stuck Pixels', 'Total Defects', 'Scratches', 'Inspection Time'
                ])
                
                # 데이터 작성
                for result in self.inspection_history:
                    writer.writerow([
                        result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        result.quality_grade.get('grade', ''),
                        result.quality_grade.get('score', 0),
                        result.quality_grade.get('dead_pixels', 0),
                        result.quality_grade.get('hot_pixels', 0),
                        result.quality_grade.get('stuck_pixels', 0),
                        result.quality_grade.get('total_defects', 0),
                        len(result.scratches),
                        result.inspection_time
                    ])
                    
            return True
            
        except Exception as e:
            print(f"CSV 내보내기 오류: {e}")
            return False
            
    def clear_inspection_history(self):
        """검사 기록 초기화"""
        self.inspection_history.clear()
        
    def is_inspection_running(self) -> bool:
        """검사 실행 중인지 확인"""
        return self.current_inspection is not None and self.current_inspection['status'] == 'running'
