# GitHub 업로드 가이드

## 1. GitHub 저장소 생성

1. [GitHub](https://github.com)에 로그인
2. "New repository" 클릭
3. Repository name: `display_inspection_poc`
4. Description: `USB 카메라를 활용한 실시간 디스플레이 품질 검사 시스템`
5. Public 또는 Private 선택
6. "Create repository" 클릭

## 2. 로컬 Git 저장소 설정

### 2.1 Git 초기화
```bash
cd /Users/sangwonchae/Library/CloudStorage/OneDrive-InteractiveDisplaySolutions,Inc/Programming/display_inspection
git init
```

### 2.2 파일 추가
```bash
git add .
git commit -m "Initial commit: Display Inspection POC v1.0.0"
```

### 2.3 원격 저장소 연결
```bash
git remote add origin https://github.com/sangwonc-ids/display_inspection_poc.git
```

### 2.4 브랜치 설정
```bash
git branch -M main
```

### 2.5 업로드
```bash
git push -u origin main
```

## 3. 대안 방법 (GitHub Desktop 사용)

1. [GitHub Desktop](https://desktop.github.com/) 다운로드 및 설치
2. "Clone a repository from the Internet" 선택
3. URL: `https://github.com/sangwonc-ids/display_inspection_poc.git`
4. 로컬 경로 설정
5. 프로젝트 파일들을 복사
6. "Commit to main" → "Push origin"

## 4. 파일 구조 확인

업로드 전 다음 파일들이 포함되어 있는지 확인:

```
display_inspection_poc/
├── .gitignore
├── README.md
├── PRD.md
├── requirements.txt
├── main.py
├── camera_module.py
├── edge_detection.py
├── scratch_detection.py
├── pixel_defect_detection.py
├── test_pattern_generator.py
├── inspection_controller.py
├── test_app.py
├── install.py
├── run.py
└── inspection_results/ (폴더)
```

## 5. 업로드 후 설정

### 5.1 저장소 설정
- Description 업데이트
- Topics 추가: `display-inspection`, `computer-vision`, `quality-control`, `opencv`, `python`
- README.md가 제대로 표시되는지 확인

### 5.2 이슈 템플릿 생성 (선택사항)
- Bug report 템플릿
- Feature request 템플릿

### 5.3 Wiki 활성화 (선택사항)
- 상세한 문서화를 위한 Wiki 페이지 생성

## 6. 문제 해결

### 6.1 Xcode 라이선스 문제
```bash
sudo xcodebuild -license accept
```

### 6.2 Git 인증 문제
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 6.3 권한 문제
- GitHub에서 저장소 권한 확인
- Personal Access Token 사용

## 7. 추가 설정

### 7.1 GitHub Actions (CI/CD)
- 자동 테스트 설정
- 코드 품질 검사

### 7.2 보안 설정
- Dependabot 활성화
- 보안 알림 설정

### 7.3 협업 설정
- Collaborators 추가
- Branch protection rules 설정

---

**참고**: 이 가이드는 macOS 환경을 기준으로 작성되었습니다. Windows나 Linux 환경에서는 일부 명령어가 다를 수 있습니다.
