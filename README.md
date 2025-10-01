# Display Inspection POC

![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.0+-green.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

USB 카메라를 활용한 실시간 디스플레이 품질 검사 시스템의 프로토타입입니다.

## 🎯 주요 기능

### 📷 카메라 연동
- USB 카메라 실시간 연결 및 프리뷰
- BGR → RGB 색상 변환 지원
- 실시간 프레임 캡처

### 🔍 스마트 패널 감지
- 엣지 디텍션 기반 패널 영역 자동 감지
- 밝은 영역 우선 감지 알고리즘
- 스마트 영역 선택 (면적 + 사각형 정도 점수)
- 대안 감지 방법 (중앙 영역 80% 사용)

### 🔬 품질 검사 모듈
- **스크래치 검출**: 엣지 기반 스크래치 감지 및 심각도 평가
- **픽셀 결함 검출**: 데드픽셀, 핫픽셀, 스티킹픽셀 검출
- **실시간 결과 표시**: 품질 등급 (A, B, C, D급) 및 결함 통계

### 🎨 테스트 패턴 생성
- 단색 패턴 (빨강, 초록, 파랑, 흰색, 검정)
- 컬러 바 패턴
- 체크보드 패턴
- 그라데이션 패턴
- 사용자 정의 크기 및 비율 설정

### 💾 결과 저장
- JSON 형식 구조화 데이터 저장
- 인간이 읽기 쉬운 텍스트 보고서 생성
- 타임스탬프 포함 자동 파일명 생성

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/sangwonc-ids/display_inspection_poc.git
cd display_inspection_poc
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행
```bash
python main.py
```

## 📋 시스템 요구사항

- **Python**: 3.13+
- **운영체제**: macOS, Windows, Linux
- **메모리**: 최소 4GB RAM
- **카메라**: USB 연결 외부 카메라
- **디스플레이**: 검사 대상 디스플레이

## 🛠️ 설치 가이드

### 1. Python 환경 설정
```bash
# Python 3.13+ 설치 확인
python --version

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate    # Windows
```

### 2. 패키지 설치
```bash
# 의존성 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install opencv-python>=4.8.0
pip install numpy>=1.24.0
pip install PyQt5>=5.15.0
pip install Pillow>=10.0.0
pip install scikit-image>=0.21.0
pip install matplotlib>=3.7.0
```

### 3. 카메라 설정
1. USB 카메라를 컴퓨터에 연결
2. 카메라 드라이버가 설치되어 있는지 확인
3. 애플리케이션에서 "카메라" 탭 → "카메라 연결" 클릭

## 📖 사용 방법

### 1. 기본 워크플로우
1. **카메라 연결**: "카메라" 탭에서 USB 카메라 연결
2. **패널 감지**: "테스트 패턴" 탭에서 "패널 감지" 클릭
3. **테스트 패턴 생성**: 원하는 패턴을 선택하고 생성
4. **품질 검사**: "검사 제어" 탭에서 "검사 시작" 클릭
5. **결과 확인**: 실시간으로 검사 결과 확인
6. **결과 저장**: "결과 저장" 버튼으로 검사 결과 저장

### 2. 고급 설정
- **검사 영역 조정**: 패널 감지 후 수동으로 영역 조정 가능
- **검사 파라미터**: 각 검사 모듈의 민감도 조정
- **결과 필터링**: 특정 결함 유형만 검사하도록 설정

## 🏗️ 프로젝트 구조

```
display_inspection/
├── main.py                      # 메인 애플리케이션
├── camera_module.py             # 카메라 제어 모듈
├── edge_detection.py            # 패널 감지 모듈
├── scratch_detection.py         # 스크래치 검출 모듈
├── pixel_defect_detection.py    # 픽셀 결함 검출 모듈
├── test_pattern_generator.py    # 테스트 패턴 생성 모듈
├── inspection_controller.py     # 검사 제어 모듈
├── test_app.py                 # 테스트 모듈
├── requirements.txt            # 의존성 패키지
├── PRD.md                      # 제품 요구사항 문서
├── README.md                   # 프로젝트 문서
└── inspection_results/          # 검사 결과 저장 폴더
    ├── inspection_results_*.json
    └── inspection_report_*.txt
```

## 🔧 기술 스택

- **Python 3.13+**: 메인 개발 언어
- **OpenCV 4.8.0+**: 컴퓨터 비전 및 이미지 처리
- **PyQt5 5.15.0+**: GUI 프레임워크
- **NumPy 1.24.0+**: 수치 계산
- **scikit-image 0.21.0+**: 이미지 처리 알고리즘
- **Pillow 10.0.0+**: 이미지 파일 처리
- **matplotlib 3.7.0+**: 데이터 시각화

## 📊 성능 지표

- **프레임 레이트**: 최소 15 FPS
- **검사 지연시간**: 1초 이내
- **메모리 사용량**: 500MB 이하
- **패널 감지 정확도**: 95% 이상
- **결함 검출 정확도**: 90% 이상

## 🧪 테스트

### 단위 테스트 실행
```bash
python test_app.py
```

### 통합 테스트
1. 카메라 연결 테스트
2. 패널 감지 테스트
3. 검사 모듈 테스트
4. 결과 저장 테스트

## 🐛 알려진 이슈

- **픽셀 결함 검출 오류**: `too many values to unpack` 오류 발생 시 재시작 필요
- **카메라 색상 반전**: BGR → RGB 변환으로 해결됨
- **패널 감지 실패**: 밝은 영역 기반 감지로 개선됨

## 🔄 업데이트 로그

### v1.0.0 (2025-01-01)
- ✅ 기본 프레임워크 구축
- ✅ 카메라 연동 구현
- ✅ 패널 감지 알고리즘 개발
- ✅ 기본 검사 모듈 구현
- ✅ UI/UX 개선
- ✅ 성능 최적화

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/sangwonc-ids/display_inspection_poc/issues)
- **문서**: [Wiki](https://github.com/sangwonc-ids/display_inspection_poc/wiki)
- **이메일**: support@ids.com

## 🚀 로드맵

### Phase 1 (완료)
- ✅ 기본 프레임워크 구축
- ✅ 카메라 연동 구현
- ✅ 패널 감지 알고리즘 개발
- ✅ 기본 검사 모듈 구현

### Phase 2 (진행 중)
- 🔄 UI/UX 개선
- 🔄 성능 최적화
- 🔄 테스트 케이스 확장

### Phase 3 (계획)
- 📋 AI 모델 통합
- 📋 클라우드 연동
- 📋 모바일 지원

---

**개발팀**: Display Inspection Team  
**문서 버전**: 1.0  
**최종 업데이트**: 2025-01-01