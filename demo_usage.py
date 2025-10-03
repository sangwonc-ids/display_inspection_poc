#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
패널 검사 시스템 데모 및 사용법
Panel Inspection System Demo and Usage Guide
"""

import cv2
import numpy as np
import time

def create_demo_panel():
    """데모용 패널 이미지 생성"""
    # 1920x1080 크기의 패널 시뮬레이션
    width, height = 1920, 1080
    panel = np.ones((height, width, 3), dtype=np.uint8) * 128  # 회색 배경
    
    # 테스트 패턴 추가
    # 1. 스크래치 시뮬레이션
    cv2.line(panel, (100, 100), (300, 200), (0, 0, 0), 3)
    cv2.line(panel, (500, 300), (800, 400), (0, 0, 0), 2)
    
    # 2. 데드 픽셀 시뮬레이션
    for i in range(5):
        for j in range(5):
            x = 200 + i * 50
            y = 200 + j * 50
            cv2.circle(panel, (x, y), 2, (0, 0, 0), -1)
    
    # 3. 밝은 점 시뮬레이션
    for i in range(3):
        for j in range(3):
            x = 1000 + i * 100
            y = 200 + j * 100
            cv2.circle(panel, (x, y), 3, (255, 255, 255), -1)
    
    # 4. 색상 불균일성 시뮬레이션
    cv2.rectangle(panel, (1500, 100), (1700, 300), (200, 100, 100), -1)
    cv2.rectangle(panel, (1500, 400), (1700, 600), (100, 100, 200), -1)
    
    # 5. 밝기 불균일성 시뮬레이션
    for i in range(4):
        for j in range(4):
            x = 200 + i * 200
            y = 600 + j * 100
            brightness = 100 + (i + j) * 20
            cv2.rectangle(panel, (x, y), (x+150, y+80), (brightness, brightness, brightness), -1)
    
    return panel

def demo_basic_inspection():
    """기본 검사 데모"""
    print("=== 기본 패널 검사 데모 ===")
    
    # 데모 패널 생성
    panel = create_demo_panel()
    print("✓ 데모 패널 생성 완료")
    
    # 기본 검사 수행
    from advanced_analysis import AdvancedDisplayAnalyzer
    
    analyzer = AdvancedDisplayAnalyzer()
    
    # 스크래치 감지
    scratches = analyzer.detect_scratches(panel)
    print(f"✓ 스크래치 감지: {scratches['count']}개")
    
    # 데드 픽셀 감지
    dead_pixels = analyzer.detect_dead_pixels(panel)
    print(f"✓ 데드 픽셀 감지: {dead_pixels['count']}개")
    
    # 밝은 점 감지
    bright_spots = analyzer.detect_bright_spots(panel)
    print(f"✓ 밝은 점 감지: {bright_spots['count']}개")
    
    # 색상 균일성 분석
    color_uniformity = analyzer.analyze_color_uniformity(panel)
    print(f"✓ 색상 균일성: {color_uniformity['uniformity_score']:.2f}")
    
    # 무라 결함 감지
    mura_defects = analyzer.detect_mura_defects(panel)
    print(f"✓ 무라 결함 감지: {mura_defects['count']}개")
    
    # 종합 분석
    report = analyzer.create_analysis_report(panel)
    print(f"✓ 종합 품질 점수: {report['overall_quality_score']:.1f}/100")
    
    return report

def demo_camera_inspection():
    """카메라 검사 데모"""
    print("\n=== 카메라 검사 데모 ===")
    
    # 카메라 연결 테스트
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("✗ 카메라를 찾을 수 없습니다.")
        return False
    
    print("✓ 카메라 연결 성공")
    
    # 카메라 설정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    print("✓ 카메라 설정 완료")
    
    # 몇 프레임 캡처
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"✓ 프레임 {i+1} 캡처 성공")
            
            # 간단한 분석
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            print(f"  평균 밝기: {brightness:.1f}")
        else:
            print(f"✗ 프레임 {i+1} 캡처 실패")
        
        time.sleep(0.5)
    
    cap.release()
    print("✓ 카메라 해제 완료")
    
    return True

def print_usage_guide():
    """사용법 가이드 출력"""
    print("\n" + "="*60)
    print("패널 검사 시스템 사용법")
    print("="*60)
    
    print("\n1. 기본 패널 검사 시스템:")
    print("   python panel_inspector.py")
    print("   - 실시간 카메라 뷰")
    print("   - 디스플레이 타입 선택")
    print("   - 가이드 박스 표시")
    print("   - 실시간 검사")
    
    print("\n2. 고급 패널 검사 시스템:")
    print("   python advanced_panel_detector.py")
    print("   - 자동 패널 감지")
    print("   - 캘리브레이션 기능")
    print("   - 고급 분석 알고리즘")
    print("   - 정확한 패널 영역 추출")
    
    print("\n3. 오프라인 분석:")
    print("   python advanced_analysis.py")
    print("   - 이미지 파일 분석")
    print("   - 상세한 결과 시각화")
    print("   - 종합 품질 평가")
    
    print("\n4. 시스템 테스트:")
    print("   python test_system.py")
    print("   - 전체 시스템 테스트")
    print("   - 성능 벤치마크")
    print("   - 기능 검증")
    
    print("\n" + "="*60)
    print("주요 기능:")
    print("="*60)
    
    print("✓ 스크래치 감지: Canny 엣지 + Hough 변환")
    print("✓ 데드 픽셀 감지: 로컬 평균 비교")
    print("✓ 핫 픽셀 감지: 적응적 임계값")
    print("✓ 색상 균일성: 그리드 기반 분석")
    print("✓ 무라 결함: 가우시안 필터 기반")
    print("✓ 실시간 검사: 30 FPS 카메라 지원")
    print("✓ 자동 패널 감지: 윤곽선 기반")
    print("✓ 캘리브레이션: 패널 위치 저장/로드")
    
    print("\n" + "="*60)
    print("권장 사용 시나리오:")
    print("="*60)
    
    print("1. 빠른 검사: panel_inspector.py")
    print("   - 간단한 UI")
    print("   - 실시간 피드백")
    print("   - 기본 검사 기능")
    
    print("\n2. 정밀 검사: advanced_panel_detector.py")
    print("   - 정확한 패널 감지")
    print("   - 캘리브레이션 지원")
    print("   - 고급 분석 알고리즘")
    
    print("\n3. 배치 처리: advanced_analysis.py")
    print("   - 대량 이미지 처리")
    print("   - 상세한 보고서 생성")
    print("   - 결과 시각화")

def main():
    """메인 함수"""
    print("패널 검사 시스템 데모 시작")
    print("="*50)
    
    # 기본 검사 데모
    try:
        report = demo_basic_inspection()
        print(f"\n✓ 기본 검사 데모 완료 - 품질 점수: {report['overall_quality_score']:.1f}/100")
    except Exception as e:
        print(f"✗ 기본 검사 데모 실패: {str(e)}")
    
    # 카메라 검사 데모
    try:
        camera_success = demo_camera_inspection()
        if camera_success:
            print("\n✓ 카메라 검사 데모 완료")
        else:
            print("\n⚠️  카메라 검사 데모 건너뜀 (카메라 없음)")
    except Exception as e:
        print(f"✗ 카메라 검사 데모 실패: {str(e)}")
    
    # 사용법 가이드
    print_usage_guide()
    
    print("\n" + "="*50)
    print("데모 완료! 위의 사용법을 참고하여 시스템을 사용하세요.")
    print("="*50)

if __name__ == "__main__":
    main()
