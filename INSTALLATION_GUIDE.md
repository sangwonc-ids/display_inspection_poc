# Display Inspection POC 설치 및 사용 가이드

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 과정](#설치-과정)
3. [사용 방법](#사용-방법)
4. [문제 해결](#문제-해결)
5. [고급 설정](#고급-설정)

## 🖥️ 시스템 요구사항

### 최소 요구사항
- **운영체제**: macOS 10.15+, Windows 10+, Ubuntu 18.04+
- **Python**: 3.13+
- **메모리**: 4GB RAM
- **저장공간**: 1GB 여유 공간
- **카메라**: USB 연결 외부 카메라
- **디스플레이**: 검사 대상 디스플레이

### 권장 사양
- **메모리**: 8GB RAM
- **저장공간**: 2GB 여유 공간
- **카메라**: 1080p 이상 해상도 지원
- **그래픽**: OpenGL 3.0+ 지원

## 🚀 설치 과정

### 1단계: Python 환경 설정

#### macOS
```bash
# Homebrew를 사용한 Python 설치
brew install python@3.13

# 또는 공식 Python 다운로드
# https://www.python.org/downloads/
```

#### Windows
```bash
# Microsoft Store에서 Python 설치
# 또는 공식 Python 다운로드
# https://www.python.org/downloads/
```

#### Ubuntu/Linux
```bash
# Python 3.13 설치
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-pip
```

### 2단계: 프로젝트 다운로드

```bash
# GitHub에서 클론
git clone https://github.com/sangwonc-ids/display_inspection_poc.git
cd display_inspection_poc

# 또는 ZIP 파일 다운로드 후 압축 해제
```

### 3단계: 가상환경 생성 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4단계: 의존성 설치

```bash
# 모든 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
pip install PyQt5>=5.15.0
pip install Pillow>=10.0.0
pip install scikit-image>=0.21.0
pip install matplotlib>=3.7.0
```

### 5단계: 설치 확인

```bash
# 테스트 실행
python test_app.py

# 메인 애플리케이션 실행
python main.py
```

## 📖 사용 방법

### 기본 워크플로우

#### 1. 카메라 연결
1. USB 카메라를 컴퓨터에 연결
2. 애플리케이션 실행: `python main.py`
3. "카메라" 탭 클릭
4. "카메라 연결" 버튼 클릭
5. 카메라 프리뷰가 표시되는지 확인

#### 2. 패널 감지
1. "테스트 패턴" 탭 클릭
2. "패널 감지" 버튼 클릭
3. 터미널에서 감지 과정 확인
4. 감지된 패널 영역이 표시되는지 확인

#### 3. 테스트 패턴 생성
1. 원하는 패턴 선택 (단색, 컬러바, 체크보드 등)
2. 크기 및 비율 설정
3. "패턴 생성" 버튼 클릭
4. 생성된 패턴이 표시되는지 확인

#### 4. 품질 검사 실행
1. "검사 제어" 탭 클릭
2. "검사 시작" 버튼 클릭
3. 실시간 검사 결과 확인
4. 품질 등급 및 결함 통계 확인

#### 5. 결과 저장
1. "결과 저장" 버튼 클릭
2. `inspection_results/` 폴더에 결과 파일 생성 확인
3. JSON 및 텍스트 형식으로 저장됨

### 고급 사용법

#### 검사 파라미터 조정
```python
# edge_detection.py에서 패널 감지 민감도 조정
self.min_area = 10000  # 최소 면적
self.threshold = 100   # 밝기 임계값

# scratch_detection.py에서 스크래치 감지 민감도 조정
self.min_length = 50   # 최소 스크래치 길이
self.max_gap = 10      # 최대 간격

# pixel_defect_detection.py에서 픽셀 결함 감지 민감도 조정
self.dead_threshold = 30    # 데드픽셀 임계값
self.hot_threshold = 200    # 핫픽셀 임계값
```

#### 사용자 정의 패턴 생성
```python
# test_pattern_generator.py에 새로운 패턴 추가
def generate_custom_pattern(self, width: int, height: int) -> np.ndarray:
    """사용자 정의 패턴"""
    pattern = np.zeros((height, width, 3), dtype=np.uint8)
    # 패턴 로직 구현
    return pattern
```

## 🔧 문제 해결

### 일반적인 문제

#### 1. 카메라 연결 실패
**증상**: "카메라 연결 실패" 메시지
**해결방법**:
- 카메라 드라이버 설치 확인
- 다른 USB 포트 사용
- 카메라가 다른 프로그램에서 사용 중인지 확인

#### 2. 패널 감지 실패
**증상**: "패널 감지 실패" 메시지
**해결방법**:
- 조명 조건 개선
- 카메라 각도 조정
- 패턴의 대비 향상

#### 3. 픽셀 결함 검출 오류
**증상**: "too many values to unpack" 오류
**해결방법**:
- 애플리케이션 재시작
- 검사 영역 조정
- 카메라 해상도 변경

#### 4. 색상 반전 문제
**증상**: 파란색이 빨간색으로, 빨간색이 파란색으로 표시
**해결방법**:
- BGR → RGB 변환이 자동으로 적용됨
- `camera_module.py`의 `convert_to_rgb=True` 확인

### 성능 문제

#### 1. 느린 검사 속도
**해결방법**:
- 카메라 해상도 낮추기
- 검사 영역 축소
- 불필요한 모듈 비활성화

#### 2. 높은 메모리 사용량
**해결방법**:
- 프레임 버퍼 크기 조정
- 가비지 컬렉션 강제 실행
- 불필요한 이미지 데이터 정리

### 설치 문제

#### 1. 패키지 설치 실패
**해결방법**:
```bash
# pip 업그레이드
pip install --upgrade pip

# 개별 패키지 설치
pip install opencv-python --no-cache-dir

# 가상환경 재생성
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. PyQt5 설치 실패
**해결방법**:
```bash
# macOS
brew install pyqt5

# Ubuntu
sudo apt install python3-pyqt5

# Windows
pip install PyQt5 --no-cache-dir
```

## ⚙️ 고급 설정

### 환경 변수 설정
```bash
# 카메라 해상도 설정
export CAMERA_WIDTH=1920
export CAMERA_HEIGHT=1080

# 검사 모드 설정
export INSPECTION_MODE=standard  # standard, fast, detailed

# 로그 레벨 설정
export LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### 설정 파일 생성
```python
# config.py
class Config:
    CAMERA_WIDTH = 1920
    CAMERA_HEIGHT = 1080
    INSPECTION_MODE = 'standard'
    LOG_LEVEL = 'INFO'
    SAVE_RESULTS = True
    AUTO_DETECT_PANEL = True
```

### 자동화 스크립트
```bash
#!/bin/bash
# auto_inspection.sh

# 가상환경 활성화
source venv/bin/activate

# 애플리케이션 실행
python main.py

# 결과 백업
cp -r inspection_results/ backup/$(date +%Y%m%d_%H%M%S)/
```

## 📊 모니터링 및 로깅

### 로그 파일 확인
```bash
# 애플리케이션 로그
tail -f logs/app.log

# 검사 결과 로그
tail -f logs/inspection.log

# 오류 로그
tail -f logs/error.log
```

### 성능 모니터링
```bash
# 메모리 사용량 확인
ps aux | grep python

# CPU 사용률 확인
top -p $(pgrep -f "python main.py")
```

## 🔄 업데이트 및 유지보수

### 정기 업데이트
```bash
# 패키지 업데이트
pip install --upgrade -r requirements.txt

# 코드 업데이트
git pull origin main

# 의존성 확인
pip check
```

### 백업 및 복구
```bash
# 프로젝트 백업
tar -czf display_inspection_backup_$(date +%Y%m%d).tar.gz .

# 설정 백업
cp -r inspection_results/ backup/
```

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-01-01  
**작성자**: Display Inspection Team
