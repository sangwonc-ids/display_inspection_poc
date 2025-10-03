#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디스플레이 검사 시스템 테스트 스크립트
Display Inspection System Test Script
"""

import cv2
import numpy as np
import os
import sys
from advanced_analysis import AdvancedDisplayAnalyzer
from display_inspector import DisplayInspector

def create_test_image():
    """테스트용 디스플레이 이미지 생성"""
    # 기본 이미지 생성 (1920x1080)
    width, height = 1920, 1080
    image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 배경을 회색으로 설정
    image.fill(128)
    
    # 테스트 패턴 추가
    # 1. 스크래치 시뮬레이션 (검은 선)
    cv2.line(image, (100, 100), (300, 200), (0, 0, 0), 3)
    cv2.line(image, (500, 300), (800, 400), (0, 0, 0), 2)
    
    # 2. 데드 픽셀 시뮬레이션 (검은 점)
    cv2.circle(image, (150, 150), 2, (0, 0, 0), -1)
    cv2.circle(image, (200, 200), 1, (0, 0, 0), -1)
    cv2.circle(image, (250, 250), 2, (0, 0, 0), -1)
    
    # 3. 핫 픽셀 시뮬레이션 (밝은 점)
    cv2.circle(image, (400, 400), 3, (255, 255, 255), -1)
    cv2.circle(image, (450, 450), 2, (255, 255, 255), -1)
    
    # 4. 색상 불균일성 시뮬레이션
    # 빨간색 영역
    cv2.rectangle(image, (600, 100), (800, 300), (200, 100, 100), -1)
    # 파란색 영역
    cv2.rectangle(image, (1000, 200), (1200, 400), (100, 100, 200), -1)
    
    # 5. 무라 결함 시뮬레이션 (불균일한 밝기)
    for i in range(5):
        for j in range(5):
            x = 1300 + i * 20
            y = 500 + j * 20
            brightness = 100 + (i + j) * 10
            cv2.rectangle(image, (x, y), (x+15, y+15), (brightness, brightness, brightness), -1)
    
    # 6. 그라데이션 패턴
    for i in range(width):
        intensity = int(128 + 50 * np.sin(i * 0.01))
        cv2.line(image, (i, 800), (i, 900), (intensity, intensity, intensity), 1)
    
    return image

def test_basic_functionality():
    """기본 기능 테스트"""
    print("=== 기본 기능 테스트 ===")
    
    # 테스트 이미지 생성
    test_image = create_test_image()
    
    # 이미지 저장
    cv2.imwrite("test_display.jpg", test_image)
    print("✓ 테스트 이미지 생성 완료: test_display.jpg")
    
    # 기본 분석 테스트
    analyzer = AdvancedDisplayAnalyzer()
    
    try:
        # 데드 픽셀 감지 테스트
        dead_pixels = analyzer.detect_dead_pixels(test_image)
        print(f"✓ 데드 픽셀 감지: {dead_pixels['count']}개 감지")
        
        # 밝은 점 감지 테스트
        bright_spots = analyzer.detect_bright_spots(test_image)
        print(f"✓ 밝은 점 감지: {bright_spots['count']}개 감지")
        
        # 색상 균일성 분석 테스트
        color_uniformity = analyzer.analyze_color_uniformity(test_image)
        print(f"✓ 색상 균일성 분석: 점수 {color_uniformity['uniformity_score']:.2f}")
        
        # 무라 결함 감지 테스트
        mura_defects = analyzer.detect_mura_defects(test_image)
        print(f"✓ 무라 결함 감지: {mura_defects['count']}개 감지")
        
        # 픽셀 응답 분석 테스트
        pixel_response = analyzer.analyze_pixel_response(test_image)
        print(f"✓ 픽셀 응답 분석: 동적 범위 {pixel_response['dynamic_range']}")
        
        # 종합 분석 테스트
        report = analyzer.create_analysis_report(test_image)
        print(f"✓ 종합 분석 완료: 품질 점수 {report['overall_quality_score']:.1f}/100")
        
        return True
        
    except Exception as e:
        print(f"✗ 테스트 실패: {str(e)}")
        return False

def test_camera_functionality():
    """카메라 기능 테스트"""
    print("\n=== 카메라 기능 테스트 ===")
    
    try:
        # 카메라 연결 테스트
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("✗ 카메라를 찾을 수 없습니다. 카메라가 연결되어 있는지 확인하세요.")
            return False
        
        print("✓ 카메라 연결 성공")
        
        # 카메라 설정 테스트
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(camera.get(cv2.CAP_PROP_FPS))
        
        print(f"✓ 카메라 설정: {width}x{height} @ {fps}fps")
        
        # 이미지 캡처 테스트
        ret, frame = camera.read()
        if ret:
            print("✓ 이미지 캡처 성공")
            cv2.imwrite("camera_test.jpg", frame)
            print("✓ 캡처된 이미지 저장: camera_test.jpg")
        else:
            print("✗ 이미지 캡처 실패")
            camera.release()
            return False
        
        camera.release()
        return True
        
    except Exception as e:
        print(f"✗ 카메라 테스트 실패: {str(e)}")
        return False

def test_ui_functionality():
    """UI 기능 테스트"""
    print("\n=== UI 기능 테스트 ===")
    
    try:
        # tkinter 가용성 테스트
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 창을 숨김
        print("✓ tkinter 사용 가능")
        
        # 기본 위젯 테스트
        label = tk.Label(root, text="테스트")
        button = tk.Button(root, text="테스트")
        print("✓ 기본 위젯 생성 성공")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ UI 테스트 실패: {str(e)}")
        return False

def run_performance_test():
    """성능 테스트"""
    print("\n=== 성능 테스트 ===")
    
    import time
    
    # 다양한 해상도에서 테스트
    resolutions = [(640, 480), (1280, 720), (1920, 1080)]
    
    for width, height in resolutions:
        print(f"\n해상도 {width}x{height} 테스트:")
        
        # 테스트 이미지 생성
        test_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        
        analyzer = AdvancedDisplayAnalyzer()
        
        # 분석 시간 측정
        start_time = time.time()
        report = analyzer.create_analysis_report(test_image)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        print(f"  분석 시간: {analysis_time:.2f}초")
        print(f"  품질 점수: {report['overall_quality_score']:.1f}/100")

def cleanup_test_files():
    """테스트 파일 정리"""
    test_files = ["test_display.jpg", "camera_test.jpg"]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ 테스트 파일 삭제: {file}")

def main():
    """메인 테스트 함수"""
    print("디스플레이 검사 시스템 테스트 시작")
    print("=" * 50)
    
    # 테스트 실행
    tests = [
        ("기본 기능", test_basic_functionality),
        ("카메라 기능", test_camera_functionality),
        ("UI 기능", test_ui_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} 테스트 중 예외 발생: {str(e)}")
    
    # 성능 테스트 (선택사항)
    if len(sys.argv) > 1 and sys.argv[1] == "--performance":
        run_performance_test()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print(f"테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("\n시스템 사용 방법:")
        print("1. python display_inspector.py  # GUI 실행")
        print("2. python advanced_analysis.py  # 고급 분석")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 문제를 해결한 후 다시 시도하세요.")
    
    # 테스트 파일 정리
    cleanup_test_files()

if __name__ == "__main__":
    main()
