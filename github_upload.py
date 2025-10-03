#!/usr/bin/env python3
"""
GitHub 직접 업로드 스크립트
GitHub API를 사용하여 저장소에 파일을 업로드합니다.
"""

import os
import base64
import requests
import json
from pathlib import Path

def create_repository():
    """GitHub 저장소 생성"""
    url = "https://api.github.com/user/repos"
    
    data = {
        "name": "display_inspection_poc",
        "description": "USB 카메라를 활용한 실시간 디스플레이 품질 검사 시스템",
        "private": False,
        "auto_init": True
    }
    
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print("✅ 저장소 생성 성공")
            return True
        elif response.status_code == 422:
            print("⚠️ 저장소가 이미 존재합니다")
            return True
        else:
            print(f"❌ 저장소 생성 실패: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 저장소 생성 오류: {e}")
        return False

def upload_file_to_github(file_path, repo_owner, repo_name, branch="main"):
    """GitHub에 파일 업로드"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    try:
        # 파일 읽기
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Base64 인코딩
        content_b64 = base64.b64encode(content).decode('utf-8')
        
        # 요청 데이터
        data = {
            'message': f'Add {file_path}',
            'content': content_b64,
            'branch': branch
        }
        
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # API 호출
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"✅ {file_path} 업로드 성공")
            return True
        elif response.status_code == 422:
            print(f"⚠️ {file_path} 이미 존재함")
            return True
        else:
            print(f"❌ {file_path} 업로드 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {file_path} 업로드 오류: {e}")
        return False

def main():
    """메인 함수"""
    repo_owner = "sangwonc-ids"
    repo_name = "display_inspection_poc"
    branch = "main"
    
    print(f"🚀 {repo_owner}/{repo_name} 저장소에 파일 업로드 시작...")
    
    # 저장소 생성
    if not create_repository():
        print("❌ 저장소 생성에 실패했습니다.")
        return
    
    # 업로드할 파일 목록
    files_to_upload = [
        'README.md',
        'PRD.md',
        'INSTALLATION_GUIDE.md',
        'GITHUB_SETUP.md',
        'FINAL_UPLOAD_GUIDE.md',
        'QUICK_UPLOAD.md',
        'requirements.txt',
        '.gitignore',
        'main.py',
        'camera_module.py',
        'edge_detection.py',
        'scratch_detection.py',
        'pixel_defect_detection.py',
        'test_pattern_generator.py',
        'inspection_controller.py',
        'test_app.py',
        'install.py',
        'run.py'
    ]
    
    success_count = 0
    total_count = len(files_to_upload)
    
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            if upload_file_to_github(file_path, repo_owner, repo_name, branch):
                success_count += 1
        else:
            print(f"⚠️ {file_path} 파일을 찾을 수 없습니다.")
    
    print(f"\n📊 업로드 완료: {success_count}/{total_count} 파일")
    
    if success_count == total_count:
        print("🎉 모든 파일이 성공적으로 업로드되었습니다!")
        print(f"📁 저장소 URL: https://github.com/{repo_owner}/{repo_name}")
    else:
        print("⚠️ 일부 파일 업로드에 실패했습니다.")

if __name__ == "__main__":
    main()
