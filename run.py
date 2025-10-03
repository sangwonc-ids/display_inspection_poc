#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디스플레이 품질 검사 시스템 실행 스크립트
"""

import sys
import os

def main():
    """메인 실행 함수"""
    print("디스플레이 품질 검사 시스템을 시작합니다...")
    
    try:
        # 메인 애플리케이션 실행
        from main import main as run_main
        run_main()
        
    except ImportError as e:
        print(f"❌ 모듈 import 오류: {e}")
        print("다음 명령어로 필요한 패키지를 설치하세요:")
        print("python install.py")
        
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        print("문제가 지속되면 test_app.py를 실행하여 테스트해보세요.")

if __name__ == "__main__":
    main()
