#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디스플레이 품질 검사 시스템
Display Quality Inspection System

외부 카메라를 통한 실시간 디스플레이 검사

주요 기능:
- 엣지 디텍션 (Rectangle): 디스플레이 패널 자동 감지
- 테스트 패턴 생성: 다양한 색상 및 패턴 테스트
- 스크래치 검사: 선형 결함 검출 및 분석
- 불량화소 검사: 데드픽셀, 핫픽셀, 스티킹픽셀 검출
- 품질 등급 평가: A~F 등급 시스템
- 실시간 결과 표시: 검사 진행 상황 모니터링
- 결과 저장: JSON 및 텍스트 형식으로 저장

기술 스택:
- OpenCV: 컴퓨터 비전 및 이미지 처리
- PyQt5: GUI 프레임워크
- NumPy: 수치 계산
- scikit-image: 이미지 분석
- SciPy: 과학 계산

작성자: Display Inspection Team
버전: 1.0.0
날짜: 2024-10-01
"""

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                           QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit,
                           QGroupBox, QGridLayout, QSlider, QCheckBox)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
import time
from datetime import datetime

from camera_module import CameraModule
from edge_detection import EdgeDetection
from test_pattern_generator import TestPatternGenerator
from scratch_detection import ScratchDetection
from pixel_defect_detection import PixelDefectDetection
from inspection_controller import InspectionController


class DisplayInspectionApp(QMainWindow):
    """
    디스플레이 품질 검사 메인 애플리케이션 클래스
    
    이 클래스는 PyQt5를 사용하여 GUI를 제공하고, 
    카메라 연결, 검사 실행, 결과 표시 등의 기능을 담당합니다.
    
    주요 구성 요소:
    - 카메라 모듈: USB 카메라 연결 및 프레임 캡처
    - 엣지 디텍션: 디스플레이 패널 자동 감지
    - 스크래치 검사: 선형 결함 검출
    - 픽셀 결함 검사: 데드픽셀, 핫픽셀, 스티킹픽셀 검출
    - 테스트 패턴 생성: 다양한 색상 및 패턴 생성
    - 품질 평가: A~F 등급 시스템
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("디스플레이 품질 검사 시스템 v1.0.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 모듈 초기화
        self.camera_module = CameraModule()
        self.edge_detection = EdgeDetection()
        self.pattern_generator = TestPatternGenerator()
        self.scratch_detection = ScratchDetection()
        self.pixel_defect_detection = PixelDefectDetection()
        self.inspection_controller = InspectionController()
        
        # 상태 변수
        self.is_inspecting = False
        self.detected_panel = None
        self.inspection_results = {}
        
        self.init_ui()
        self.setup_timer()
        
    def init_ui(self):
        """UI 초기화"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout(central_widget)
        
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        
        # 각 탭 생성
        self.create_camera_tab()
        self.create_polarizing_filter_tab()
        self.create_test_pattern_tab()
        self.create_inspection_control_tab()
        
        main_layout.addWidget(self.tab_widget)
        
    def create_camera_tab(self):
        """카메라 탭 생성"""
        camera_widget = QWidget()
        layout = QVBoxLayout(camera_widget)
        
        # 카메라 제어
        control_group = QGroupBox("카메라 제어")
        control_layout = QHBoxLayout(control_group)
        
        self.camera_connect_btn = QPushButton("카메라 연결")
        self.camera_disconnect_btn = QPushButton("카메라 연결 해제")
        self.camera_calibrate_btn = QPushButton("카메라 보정")
        
        control_layout.addWidget(self.camera_connect_btn)
        control_layout.addWidget(self.camera_disconnect_btn)
        control_layout.addWidget(self.camera_calibrate_btn)
        
        # 카메라 뷰
        self.camera_view = QLabel("카메라 뷰")
        self.camera_view.setMinimumSize(640, 480)
        self.camera_view.setStyleSheet("border: 1px solid black; background-color: black;")
        self.camera_view.setAlignment(Qt.AlignCenter)
        
        # 카메라 설정
        settings_group = QGroupBox("카메라 설정")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("해상도:"), 0, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1920x1080", "1280x720", "640x480"])
        settings_layout.addWidget(self.resolution_combo, 0, 1)
        
        settings_layout.addWidget(QLabel("FPS:"), 1, 0)
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(30)
        settings_layout.addWidget(self.fps_spin, 1, 1)
        
        layout.addWidget(control_group)
        layout.addWidget(self.camera_view)
        layout.addWidget(settings_group)
        
        # 버튼 연결
        self.camera_connect_btn.clicked.connect(self.connect_camera)
        self.camera_disconnect_btn.clicked.connect(self.disconnect_camera)
        self.camera_calibrate_btn.clicked.connect(self.calibrate_camera)
        
        self.tab_widget.addTab(camera_widget, "카메라")
        
    def create_polarizing_filter_tab(self):
        """편광필터 탭 생성"""
        filter_widget = QWidget()
        layout = QVBoxLayout(filter_widget)
        
        # 편광필터 제어
        filter_group = QGroupBox("편광필터 제어")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_angle_slider = QSlider(Qt.Horizontal)
        self.filter_angle_slider.setRange(0, 180)
        self.filter_angle_slider.setValue(0)
        self.filter_angle_label = QLabel("각도: 0°")
        
        self.filter_enable_check = QCheckBox("편광필터 활성화")
        
        filter_layout.addWidget(QLabel("편광필터 각도:"))
        filter_layout.addWidget(self.filter_angle_slider)
        filter_layout.addWidget(self.filter_angle_label)
        filter_layout.addWidget(self.filter_enable_check)
        
        layout.addWidget(filter_group)
        
        # 슬라이더 연결
        self.filter_angle_slider.valueChanged.connect(self.update_filter_angle)
        self.filter_enable_check.toggled.connect(self.toggle_filter)
        
        self.tab_widget.addTab(filter_widget, "편광필터")
        
    def create_test_pattern_tab(self):
        """테스트 패턴 탭 생성"""
        pattern_widget = QWidget()
        main_layout = QHBoxLayout(pattern_widget)
        
        # 왼쪽 패널: 패턴 생성
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 제어 버튼
        control_group = QGroupBox("검사 제어")
        control_layout = QGridLayout(control_group)
        
        self.panel_detect_btn = QPushButton("패널 감지")
        self.inspection_start_btn = QPushButton("검사 시작")
        self.inspection_stop_btn = QPushButton("검사 중지")
        self.save_results_btn = QPushButton("결과 저장")
        
        control_layout.addWidget(self.panel_detect_btn, 0, 0)
        control_layout.addWidget(self.inspection_start_btn, 0, 1)
        control_layout.addWidget(self.inspection_stop_btn, 1, 0)
        control_layout.addWidget(self.save_results_btn, 1, 1)
        
        # 크기 설정
        size_group = QGroupBox("크기 설정")
        size_layout = QGridLayout(size_group)
        
        size_layout.addWidget(QLabel("가로:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 4096)
        self.width_spin.setValue(1920)
        size_layout.addWidget(self.width_spin, 0, 1)
        
        size_layout.addWidget(QLabel("세로:"), 0, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 4096)
        self.height_spin.setValue(1080)
        size_layout.addWidget(self.height_spin, 0, 3)
        
        # 인치 설정
        inch_group = QGroupBox("인치 설정")
        inch_layout = QGridLayout(inch_group)
        
        inch_layout.addWidget(QLabel("가로:"), 0, 0)
        self.width_inch_spin = QDoubleSpinBox()
        self.width_inch_spin.setRange(1.0, 100.0)
        self.width_inch_spin.setValue(20.0)
        self.width_inch_spin.setDecimals(2)
        inch_layout.addWidget(self.width_inch_spin, 0, 1)
        
        inch_layout.addWidget(QLabel("세로:"), 0, 2)
        self.height_inch_spin = QDoubleSpinBox()
        self.height_inch_spin.setRange(1.0, 100.0)
        self.height_inch_spin.setValue(11.25)
        self.height_inch_spin.setDecimals(2)
        inch_layout.addWidget(self.height_inch_spin, 0, 3)
        
        inch_layout.addWidget(QLabel("DPI:"), 1, 0)
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 300)
        self.dpi_spin.setValue(96)
        inch_layout.addWidget(self.dpi_spin, 1, 1)
        
        # 비율 설정
        ratio_group = QGroupBox("비율 설정")
        ratio_layout = QHBoxLayout(ratio_group)
        
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItems(["16:9", "4:3", "21:9", "1:1", "사용자 정의"])
        ratio_layout.addWidget(self.ratio_combo)
        
        self.apply_ratio_btn = QPushButton("비율 적용")
        ratio_layout.addWidget(self.apply_ratio_btn)
        
        # 생성된 패턴 표시
        self.pattern_display = QLabel()
        self.pattern_display.setMinimumSize(300, 200)
        self.pattern_display.setStyleSheet("border: 1px solid black; background-color: red;")
        self.pattern_display.setAlignment(Qt.AlignCenter)
        
        left_layout.addWidget(control_group)
        left_layout.addWidget(size_group)
        left_layout.addWidget(inch_group)
        left_layout.addWidget(ratio_group)
        left_layout.addWidget(self.pattern_display)
        
        # 오른쪽 패널: 카메라 뷰 및 검사 결과
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 카메라 뷰
        self.inspection_camera_view = QLabel("카메라 뷰 (검사 대상)")
        self.inspection_camera_view.setMinimumSize(640, 480)
        self.inspection_camera_view.setStyleSheet("border: 1px solid black; background-color: black;")
        self.inspection_camera_view.setAlignment(Qt.AlignCenter)
        
        # 검사 결과
        results_group = QGroupBox("검사 결과")
        results_layout = QVBoxLayout(results_group)
        
        self.quality_guide = QTextEdit()
        self.quality_guide.setMaximumHeight(150)
        self.quality_guide.setPlainText(
            "품질 기준 안내:\n"
            "A급 (90-100점): 데드픽셀 0-1개, 핫픽셀 0-1개\n"
            "B급 (80-89점): 데드픽셀 2-3개, 핫픽셀 2-3개\n"
            "C급 (70-79점): 데드픽셀 4-5개, 핫픽셀 4-5개\n"
            "D급 (60-69점): 데드픽셀 6-10개, 핫픽셀 6-10개\n"
            "F급 (60점 미만): 데드픽셀 11개 이상, 핫픽셀 11개 이상"
        )
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setPlainText("[시스템] 검사 시스템이 준비되었습니다.")
        
        results_layout.addWidget(self.quality_guide)
        results_layout.addWidget(self.status_text)
        
        right_layout.addWidget(self.inspection_camera_view)
        right_layout.addWidget(results_group)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # 버튼 연결
        self.panel_detect_btn.clicked.connect(self.detect_panel)
        self.inspection_start_btn.clicked.connect(self.start_inspection)
        self.inspection_stop_btn.clicked.connect(self.stop_inspection)
        self.save_results_btn.clicked.connect(self.save_results)
        self.apply_ratio_btn.clicked.connect(self.apply_aspect_ratio)
        
        self.tab_widget.addTab(pattern_widget, "테스트 패턴")
        
    def create_inspection_control_tab(self):
        """검사 제어 탭 생성"""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # 검사 설정
        settings_group = QGroupBox("검사 설정")
        settings_layout = QGridLayout(settings_group)
        
        settings_layout.addWidget(QLabel("검사 모드:"), 0, 0)
        self.inspection_mode_combo = QComboBox()
        self.inspection_mode_combo.addItems(["전체 검사", "픽셀 검사만", "스크래치 검사만"])
        settings_layout.addWidget(self.inspection_mode_combo, 0, 1)
        
        settings_layout.addWidget(QLabel("민감도:"), 1, 0)
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setRange(1, 10)
        self.sensitivity_slider.setValue(5)
        settings_layout.addWidget(self.sensitivity_slider, 1, 1)
        
        # 검사 결과 표시
        results_group = QGroupBox("검사 결과")
        results_layout = QVBoxLayout(results_group)
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setMinimumHeight(300)
        
        # 실시간 업데이트 버튼
        self.refresh_results_btn = QPushButton("결과 새로고침")
        self.refresh_results_btn.clicked.connect(self.update_inspection_display)
        
        results_layout.addWidget(self.results_display)
        results_layout.addWidget(self.refresh_results_btn)
        
        layout.addWidget(settings_group)
        layout.addWidget(results_group)
        
        self.tab_widget.addTab(control_widget, "검사 제어")
        
    def setup_timer(self):
        """타이머 설정"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_view)
        self.timer.start(33)  # 약 30 FPS
        
    def connect_camera(self):
        """카메라 연결"""
        if self.camera_module.connect():
            self.add_status_message("카메라가 연결되었습니다.")
            self.camera_connect_btn.setEnabled(False)
            self.camera_disconnect_btn.setEnabled(True)
        else:
            self.add_status_message("카메라 연결에 실패했습니다.")
            
    def disconnect_camera(self):
        """카메라 연결 해제"""
        self.camera_module.disconnect()
        self.add_status_message("카메라 연결이 해제되었습니다.")
        self.camera_connect_btn.setEnabled(True)
        self.camera_disconnect_btn.setEnabled(False)
        
    def calibrate_camera(self):
        """카메라 보정"""
        self.add_status_message("카메라 보정을 시작합니다...")
        # 카메라 보정 로직 구현
        
    def update_filter_angle(self, angle):
        """편광필터 각도 업데이트"""
        self.filter_angle_label.setText(f"각도: {angle}°")
        
    def toggle_filter(self, enabled):
        """편광필터 토글"""
        status = "활성화" if enabled else "비활성화"
        self.add_status_message(f"편광필터가 {status}되었습니다.")
        
    def detect_panel(self):
        """패널 감지"""
        if not self.camera_module.is_connected():
            self.add_status_message("카메라가 연결되지 않았습니다.")
            return
            
        self.add_status_message("패널 감지를 시작합니다...")
        
        frame = self.camera_module.get_frame()
        if frame is not None:
            print(f"프레임 크기: {frame.shape}")
            self.detected_panel = self.edge_detection.detect_display(frame)
            if self.detected_panel is not None:
                x, y, w, h = self.detected_panel
                self.add_status_message(f"패널이 감지되었습니다. 위치: ({x}, {y}), 크기: {w}x{h}")
                print(f"감지된 패널: {self.detected_panel}")
            else:
                self.add_status_message("패널 감지에 실패했습니다.")
        else:
            self.add_status_message("카메라에서 프레임을 가져올 수 없습니다.")
                
    def start_inspection(self):
        """검사 시작"""
        if self.detected_panel is None:
            self.add_status_message("먼저 패널을 감지해주세요.")
            return
            
        self.is_inspecting = True
        self.add_status_message("검사가 시작되었습니다.")
        
    def stop_inspection(self):
        """검사 중지"""
        self.is_inspecting = False
        self.add_status_message("검사가 중지되었습니다.")
        
    def save_results(self):
        """결과 저장"""
        if not self.inspection_results:
            self.add_status_message("저장할 결과가 없습니다.")
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # JSON 파일로 저장
            json_filename = f"inspection_results_{timestamp}.json"
            json_saved = self.inspection_controller.save_inspection_result(
                self.inspection_results, json_filename
            )
            
            # 텍스트 보고서 생성
            report_filename = f"inspection_report_{timestamp}.txt"
            report_content = self.generate_inspection_report()
            
            # 텍스트 파일 저장
            import os
            results_dir = "inspection_results"
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
                
            report_path = os.path.join(results_dir, report_filename)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            if json_saved:
                self.add_status_message(f"결과가 {json_filename}과 {report_filename}에 저장되었습니다.")
            else:
                self.add_status_message(f"텍스트 보고서가 {report_filename}에 저장되었습니다.")
                
        except Exception as e:
            self.add_status_message(f"결과 저장 오류: {e}")
            
    def generate_inspection_report(self):
        """검사 보고서 생성"""
        if not self.inspection_results:
            return "검사 결과가 없습니다."
            
        quality_grade = self.inspection_results.get('quality_grade', {})
        scratches = self.inspection_results.get('scratches', [])
        pixel_defects = self.inspection_results.get('pixel_defects', {})
        
        report = f"""
=== 디스플레이 품질 검사 보고서 ===

검사 일시: {self.inspection_results.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}
디스플레이 영역: {self.detected_panel if self.detected_panel else 'N/A'}

=== 품질 등급 ===
등급: {quality_grade.get('grade', 'N/A')}급
점수: {quality_grade.get('score', 0):.1f}점

=== 결함 통계 ===
데드픽셀: {quality_grade.get('dead_pixels', 0)}개
핫픽셀: {quality_grade.get('hot_pixels', 0)}개
스티킹픽셀: {quality_grade.get('stuck_pixels', 0)}개
총 결함: {quality_grade.get('total_defects', 0)}개
결함 밀도: {quality_grade.get('defect_density', 0):.6f}

=== 스크래치 검사 ===
검출된 스크래치: {len(scratches)}개
"""
        
        # 스크래치 상세 정보
        if scratches:
            report += "\n스크래치 상세:\n"
            for i, scratch in enumerate(scratches, 1):
                report += f"  {i}. 길이: {scratch.get('length', 0):.1f}px, "
                report += f"폭: {scratch.get('width', 0):.1f}px, "
                report += f"심각도: {scratch.get('severity', 'N/A')}\n"
        else:
            report += "스크래치 없음\n"
            
        # 픽셀 결함 상세 정보
        if pixel_defects:
            report += "\n=== 픽셀 결함 상세 ===\n"
            
            for defect_type, defects in pixel_defects.items():
                if defects:
                    report += f"\n{defect_type}:\n"
                    for i, defect in enumerate(defects, 1):
                        report += f"  {i}. 위치: {defect.get('position', 'N/A')}, "
                        report += f"심각도: {defect.get('severity', 'N/A')}\n"
                        
        return report
            
    def apply_aspect_ratio(self):
        """비율 적용"""
        ratio = self.ratio_combo.currentText()
        if ratio == "16:9":
            self.height_spin.setValue(int(self.width_spin.value() * 9 / 16))
        elif ratio == "4:3":
            self.height_spin.setValue(int(self.width_spin.value() * 3 / 4))
        elif ratio == "21:9":
            self.height_spin.setValue(int(self.width_spin.value() * 9 / 21))
        elif ratio == "1:1":
            self.height_spin.setValue(self.width_spin.value())
            
        self.generate_test_pattern()
        
    def generate_test_pattern(self):
        """테스트 패턴 생성"""
        width = self.width_spin.value()
        height = self.height_spin.value()
        pattern = self.pattern_generator.generate_pattern(width, height)
        
        # 패턴을 QLabel에 표시
        if pattern is not None:
            h, w, ch = pattern.shape
            bytes_per_line = ch * w
            qt_image = QImage(pattern.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.pattern_display.setPixmap(pixmap.scaled(300, 200, Qt.KeepAspectRatio))
            
    def update_camera_view(self):
        """카메라 뷰 업데이트"""
        if not self.camera_module.is_connected():
            return
            
        frame = self.camera_module.get_frame()
        if frame is not None:
            # 검사 중이면 검사 로직 실행
            if self.is_inspecting and self.detected_panel is not None:
                frame = self.run_inspection(frame)
                
            # 엣지 디텍션 결과 표시
            if self.detected_panel is not None:
                frame = self.edge_detection.draw_detection_result(frame, self.detected_panel)
                
            # 프레임을 QLabel에 표시
            self.display_frame(frame, self.camera_view)
            self.display_frame(frame, self.inspection_camera_view)
            
    def run_inspection(self, frame):
        """검사 실행"""
        if self.detected_panel is None:
            return frame
            
        try:
            # 스크래치 검사
            scratches = self.scratch_detection.detect_scratches(frame, self.detected_panel)
            
            # 픽셀 결함 검사
            pixel_defects = self.pixel_defect_detection.detect_defects(frame, self.detected_panel)
            
            # 품질 등급 계산
            display_area = self.detected_panel[2] * self.detected_panel[3]
            quality_grade = self.pixel_defect_detection.calculate_quality_grade(pixel_defects, display_area)
            
            # 검사 결과 저장
            self.inspection_results = {
                'scratches': scratches,
                'pixel_defects': pixel_defects,
                'quality_grade': quality_grade,
                'timestamp': datetime.now()
            }
            
            # 실시간 결과 업데이트
            self.update_inspection_display()
            
            # 검사 제어기에 결과 전달
            self.inspection_controller.update_inspection_results(
                scratches, pixel_defects, quality_grade
            )
            
        except Exception as e:
            print(f"검사 실행 오류: {e}")
        
        return frame
        
    def display_frame(self, frame, label):
        """프레임을 QLabel에 표시"""
        if frame is not None:
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            
            # RGB 형식으로 표시 (OpenCV BGR → RGB 변환됨)
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
    def update_inspection_display(self):
        """실시간 검사 결과 표시 업데이트"""
        if not self.inspection_results:
            return
            
        try:
            # 품질 등급 정보
            quality_grade = self.inspection_results.get('quality_grade', {})
            grade = quality_grade.get('grade', 'N/A')
            score = quality_grade.get('score', 0)
            
            # 결함 통계
            dead_pixels = quality_grade.get('dead_pixels', 0)
            hot_pixels = quality_grade.get('hot_pixels', 0)
            stuck_pixels = quality_grade.get('stuck_pixels', 0)
            total_defects = quality_grade.get('total_defects', 0)
            
            # 스크래치 정보
            scratches = self.inspection_results.get('scratches', [])
            scratch_count = len(scratches)
            
            # 결과 텍스트 업데이트
            result_text = f"""
=== 실시간 검사 결과 ===

품질 등급: {grade}급 ({score:.1f}점)

픽셀 결함:
- 데드픽셀: {dead_pixels}개
- 핫픽셀: {hot_pixels}개  
- 스티킹픽셀: {stuck_pixels}개
- 총 결함: {total_defects}개

스크래치: {scratch_count}개

마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}
"""
            
            # 검사 제어 탭의 결과 표시 업데이트
            if hasattr(self, 'results_display'):
                self.results_display.setPlainText(result_text)
                
            # 상태 메시지 업데이트
            status_msg = f"검사 중 - 등급: {grade}급, 결함: {total_defects}개, 스크래치: {scratch_count}개"
            self.add_status_message(status_msg)
            
        except Exception as e:
            print(f"검사 결과 표시 업데이트 오류: {e}")
            
    def add_status_message(self, message):
        """상태 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")


def main():
    app = QApplication(sys.argv)
    window = DisplayInspectionApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
