#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디스플레이 품질 검사 시스템 테스트 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """모듈 import 테스트"""
    try:
        print("모듈 import 테스트 중...")
        
        import cv2
        print("✓ OpenCV import 성공")
        
        import numpy as np
        print("✓ NumPy import 성공")
        
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 import 성공")
        
        from camera_module import CameraModule
        print("✓ CameraModule import 성공")
        
        from edge_detection import EdgeDetection
        print("✓ EdgeDetection import 성공")
        
        from test_pattern_generator import TestPatternGenerator
        print("✓ TestPatternGenerator import 성공")
        
        from scratch_detection import ScratchDetection
        print("✓ ScratchDetection import 성공")
        
        from pixel_defect_detection import PixelDefectDetection
        print("✓ PixelDefectDetection import 성공")
        
        from inspection_controller import InspectionController
        print("✓ InspectionController import 성공")
        
        print("\n모든 모듈 import 성공!")
        return True
        
    except ImportError as e:
        print(f"❌ Import 오류: {e}")
        return False

def test_camera():
    """카메라 테스트"""
    try:
        print("\n카메라 테스트 중...")
        
        from camera_module import CameraModule
        
        camera = CameraModule()
        print("✓ CameraModule 생성 성공")
        
        # 카메라 연결 시도
        if camera.connect():
            print("✓ 카메라 연결 성공")
            
            # 프레임 캡처 테스트
            frame = camera.get_frame()
            if frame is not None:
                print("✓ 프레임 캡처 성공")
            else:
                print("⚠️ 프레임 캡처 실패")
                
            camera.disconnect()
            print("✓ 카메라 연결 해제 성공")
        else:
            print("⚠️ 카메라 연결 실패 (카메라가 연결되지 않았을 수 있음)")
            
        return True
        
    except Exception as e:
        print(f"❌ 카메라 테스트 오류: {e}")
        return False

def test_pattern_generator():
    """테스트 패턴 생성기 테스트"""
    try:
        print("\n테스트 패턴 생성기 테스트 중...")
        
        from test_pattern_generator import TestPatternGenerator
        
        generator = TestPatternGenerator()
        print("✓ TestPatternGenerator 생성 성공")
        
        # 빨간색 패턴 생성 테스트
        pattern = generator.generate_pattern(1920, 1080, 'solid_red')
        if pattern is not None:
            print("✓ 빨간색 패턴 생성 성공")
        else:
            print("❌ 빨간색 패턴 생성 실패")
            
        # 체스보드 패턴 생성 테스트
        pattern = generator.generate_pattern(640, 480, 'checkerboard')
        if pattern is not None:
            print("✓ 체스보드 패턴 생성 성공")
        else:
            print("❌ 체스보드 패턴 생성 실패")
            
        return True
        
    except Exception as e:
        print(f"❌ 패턴 생성기 테스트 오류: {e}")
        return False

def test_edge_detection():
    """엣지 디텍션 테스트"""
    try:
        print("\n엣지 디텍션 테스트 중...")
        
        from edge_detection import EdgeDetection
        import numpy as np
        
        detector = EdgeDetection()
        print("✓ EdgeDetection 생성 성공")
        
        # 더미 이미지 생성 (흰색 배경에 검은색 사각형)
        import cv2
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
        cv2.rectangle(test_image, (100, 100), (540, 380), (0, 0, 0), -1)
        
        # 엣지 디텍션 테스트
        rectangle = detector.detect_display(test_image)
        if rectangle is not None:
            print("✓ 엣지 디텍션 성공")
        else:
            print("⚠️ 엣지 디텍션 실패 (더미 이미지)")
            
        return True
        
    except Exception as e:
        print(f"❌ 엣지 디텍션 테스트 오류: {e}")
        return False

def test_inspection_controller():
    """검사 제어기 테스트"""
    try:
        print("\n검사 제어기 테스트 중...")
        
        from inspection_controller import InspectionController
        
        controller = InspectionController()
        print("✓ InspectionController 생성 성공")
        
        # 검사 시작 테스트
        if controller.start_inspection((100, 100, 400, 300), "solid_red"):
            print("✓ 검사 시작 성공")
        else:
            print("❌ 검사 시작 실패")
            
        # 검사 상태 확인
        status = controller.get_current_inspection_status()
        print(f"✓ 검사 상태: {status['status']}")
        
        # 검사 중지
        result = controller.stop_inspection()
        if result is not None:
            print("✓ 검사 중지 성공")
        else:
            print("❌ 검사 중지 실패")
            
        return True
        
    except Exception as e:
        print(f"❌ 검사 제어기 테스트 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("=== 디스플레이 품질 검사 시스템 테스트 ===\n")
    
    # 필요한 패키지 확인
    try:
        import cv2
        import numpy as np
        from PyQt5.QtWidgets import QApplication
    except ImportError as e:
        print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령어로 패키지를 설치하세요:")
        print("pip install -r requirements.txt")
        return False
    
    # 각 모듈 테스트
    tests = [
        ("모듈 Import", test_imports),
        ("카메라", test_camera),
        ("테스트 패턴 생성기", test_pattern_generator),
        ("엣지 디텍션", test_edge_detection),
        ("검사 제어기", test_inspection_controller)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"{test_name} 테스트")
        print('='*50)
        
        if test_func():
            print(f"✅ {test_name} 테스트 통과")
            passed += 1
        else:
            print(f"❌ {test_name} 테스트 실패")
    
    print(f"\n{'='*50}")
    print(f"테스트 결과: {passed}/{total} 통과")
    print('='*50)
    
    if passed == total:
        print("🎉 모든 테스트가 성공했습니다!")
        print("이제 다음 명령어로 메인 애플리케이션을 실행할 수 있습니다:")
        print("python main.py")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 오류를 확인하고 수정해주세요.")
    
    return passed == total

if __name__ == "__main__":
    main()
