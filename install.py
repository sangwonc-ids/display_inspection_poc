#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디스플레이 품질 검사 시스템 설치 스크립트
"""

import subprocess
import sys
import os

def install_requirements():
    """필요한 패키지 설치"""
    print("필요한 패키지를 설치하는 중...")
    
    try:
        # pip 업그레이드
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("✓ pip 업그레이드 완료")
        
        # requirements.txt 설치
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 필요한 패키지 설치 완료")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 실패: {e}")
        return False

def create_directories():
    """필요한 디렉토리 생성"""
    print("필요한 디렉토리를 생성하는 중...")
    
    directories = [
        "inspection_results",
        "test_images",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✓ {directory} 디렉토리 생성")
        else:
            print(f"✓ {directory} 디렉토리 이미 존재")

def check_camera():
    """카메라 연결 확인"""
    print("카메라 연결을 확인하는 중...")
    
    try:
        import cv2
        
        # 카메라 인덱스 0부터 5까지 확인
        for i in range(6):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"✓ 카메라 {i} 연결됨")
                cap.release()
                return True
            cap.release()
            
        print("⚠️ 연결된 카메라를 찾을 수 없습니다")
        return False
        
    except ImportError:
        print("❌ OpenCV가 설치되지 않았습니다")
        return False

def main():
    """메인 설치 함수"""
    print("=== 디스플레이 품질 검사 시스템 설치 ===\n")
    
    # 1. 패키지 설치
    if not install_requirements():
        print("❌ 설치 실패")
        return False
    
    # 2. 디렉토리 생성
    create_directories()
    
    # 3. 카메라 확인
    check_camera()
    
    print("\n" + "="*50)
    print("설치 완료!")
    print("="*50)
    print("다음 명령어로 테스트를 실행하세요:")
    print("python test_app.py")
    print("\n다음 명령어로 메인 애플리케이션을 실행하세요:")
    print("python main.py")
    
    return True

if __name__ == "__main__":
    main()
