#!/usr/bin/env python3
"""
GitHub 업로드 스크립트
GitHub API를 사용하여 저장소에 파일을 업로드합니다.
"""

import os
import base64
import requests
import json
from pathlib import Path

def upload_file_to_github(file_path, repo_owner, repo_name, branch="main", token=None):
    """
    GitHub에 파일을 업로드합니다.
    """
    # GitHub API URL
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    # 파일 읽기
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Base64 인코딩
    content_b64 = base64.b64encode(content).decode('utf-8')
    
    # 헤더 설정
    headers = {
        'Authorization': f'token {token}' if token else None,
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # 요청 데이터
    data = {
        'message': f'Add {file_path}',
        'content': content_b64,
        'branch': branch
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
        print(response.text)
        return False

def main():
    """
    메인 함수
    """
    # 설정
    repo_owner = "sangwonc-ids"
    repo_name = "display_inspection_poc"
    branch = "main"
    
    # GitHub 토큰 (환경변수에서 가져오기)
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GITHUB_TOKEN 환경변수가 설정되지 않았습니다.")
        print("GitHub Personal Access Token을 설정해주세요:")
        print("export GITHUB_TOKEN=your_token_here")
        return
    
    # 업로드할 파일 목록
    files_to_upload = [
        'README.md',
        'PRD.md',
        'INSTALLATION_GUIDE.md',
        'GITHUB_SETUP.md',
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
    
    print(f"🚀 {repo_owner}/{repo_name} 저장소에 파일 업로드 시작...")
    
    success_count = 0
    total_count = len(files_to_upload)
    
    for file_path in files_to_upload:
        if os.path.exists(file_path):
            if upload_file_to_github(file_path, repo_owner, repo_name, branch, token):
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
