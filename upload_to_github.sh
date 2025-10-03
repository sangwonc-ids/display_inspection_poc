#!/bin/bash
# GitHub 업로드 자동화 스크립트

echo "🚀 Display Inspection POC GitHub 업로드 시작..."

# 저장소 URL
REPO_URL="https://github.com/sangwonc-ids/display_inspection_poc.git"

# Git 초기화 (Xcode 라이선스 문제 해결 후)
echo "Git 초기화 중..."
git init
git config user.name "Display Inspection Team"
git config user.email "team@ids.com"

# 파일 추가
echo "파일 추가 중..."
git add .

# 커밋
echo "커밋 중..."
git commit -m "Initial commit: Display Inspection POC v1.0.0"

# 원격 저장소 추가
echo "원격 저장소 설정 중..."
git remote add origin $REPO_URL

# 브랜치 설정
git branch -M main

# 업로드
echo "GitHub에 업로드 중..."
git push -u origin main

echo "✅ 업로드 완료!"
echo "📁 저장소 URL: $REPO_URL"
