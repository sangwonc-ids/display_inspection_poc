#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 패턴 생성 및 카메라 검사 시스템
Test Pattern Generator and Camera Inspection System
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import json
import os
import math

class TestPatternInspector:
    """테스트 패턴 생성 및 검사 시스템"""
    
    def __init__(self):
        self.camera = None
        self.camera_running = False
        self.current_frame = None
        self.test_pattern = None
        self.panel_rectangle = None
        self.inspection_running = False
        self.inspection_results = {}
        self.polarizer_angle = 0  # 편광필터 각도 (0-180도)
        
        # 테스트 패턴 설정
        self.pattern_width = 1920
        self.pattern_height = 1080
        self.pattern_dpi = 96  # 기본 DPI
        self.current_color = "white"
        
        # 반사 제거 설정
        self.reflection_removal_enabled = True
        self.brightness_level = 1.0
        
        # 스크래치 검사 설정
        self.scratch_detection_active = False
        self.lighting_angle = 0  # 조명 각도 (0-90도)
        self.lighting_intensity = 100  # 조명 강도 (0-255)
        
        self.setup_ui()
        
    def setup_ui(self):
        """사용자 인터페이스 설정"""
        self.root = tk.Tk()
        self.root.title("테스트 패턴 생성 및 검사 시스템")
        self.root.geometry("1800x1000")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단 제어 패널 - 탭 형태로 변경
        control_notebook = ttk.Notebook(main_frame)
        control_notebook.pack(fill=tk.X, pady=(0, 10))
        
        # 카메라 제어 탭
        camera_tab = ttk.Frame(control_notebook)
        control_notebook.add(camera_tab, text="카메라")
        
        camera_frame = ttk.Frame(camera_tab)
        camera_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(camera_frame, text="카메라 시작", 
                  command=self.start_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(camera_frame, text="카메라 중지", 
                  command=self.stop_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(camera_frame, text="초점 조정", 
                  command=self.adjust_focus).pack(side=tk.LEFT, padx=5)
        ttk.Button(camera_frame, text="설정 초기화", 
                  command=self.reset_camera_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(camera_frame, text="자동초점", 
                  command=self.auto_focus).pack(side=tk.LEFT, padx=5)
        ttk.Button(camera_frame, text="연속자동초점", 
                  command=self.start_continuous_auto_focus).pack(side=tk.LEFT, padx=5)
        
        # 비네팅 보정 체크박스
        self.vignetting_correction = tk.BooleanVar(value=False)
        ttk.Checkbutton(camera_frame, text="비네팅 보정", 
                       variable=self.vignetting_correction).pack(side=tk.LEFT, padx=5)
        
        # 편광필터 탭
        polarizer_tab = ttk.Frame(control_notebook)
        control_notebook.add(polarizer_tab, text="편광필터")
        
        polarizer_frame = ttk.Frame(polarizer_tab)
        polarizer_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.polarizer_enabled = tk.BooleanVar()
        ttk.Checkbutton(polarizer_frame, text="편광필터 시뮬레이션", 
                       variable=self.polarizer_enabled).pack(side=tk.LEFT, padx=5)
        ttk.Button(polarizer_frame, text="편광 각도 조정", 
                  command=self.adjust_polarizer).pack(side=tk.LEFT, padx=5)
        ttk.Button(polarizer_frame, text="스크래치 검사", 
                  command=self.start_scratch_inspection).pack(side=tk.LEFT, padx=5)
        ttk.Button(polarizer_frame, text="딥러닝 탐지", 
                  command=self.start_deep_learning_detection).pack(side=tk.LEFT, padx=5)
        
        # 테스트 패턴 탭
        pattern_tab = ttk.Frame(control_notebook)
        control_notebook.add(pattern_tab, text="테스트 패턴")
        
        pattern_frame = ttk.Frame(pattern_tab)
        pattern_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(pattern_frame, text="Red 테스트", 
                  command=self.generate_red_test).pack(side=tk.LEFT, padx=2)
        ttk.Button(pattern_frame, text="Green 테스트", 
                  command=self.generate_green_test).pack(side=tk.LEFT, padx=2)
        ttk.Button(pattern_frame, text="Blue 테스트", 
                  command=self.generate_blue_test).pack(side=tk.LEFT, padx=2)
        ttk.Button(pattern_frame, text="데드픽셀 테스트", 
                  command=self.generate_dead_pixel_test).pack(side=tk.LEFT, padx=2)
        ttk.Button(pattern_frame, text="색상 균일성", 
                  command=self.generate_uniformity_test).pack(side=tk.LEFT, padx=2)
        ttk.Button(pattern_frame, text="불량픽셀 시뮬레이션", 
                  command=self.generate_defect_simulation).pack(side=tk.LEFT, padx=2)
        
        # 검사 제어 탭
        inspect_tab = ttk.Frame(control_notebook)
        control_notebook.add(inspect_tab, text="검사 제어")
        
        inspect_frame = ttk.Frame(inspect_tab)
        inspect_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(inspect_frame, text="패널 감지", 
                  command=self.detect_panel).pack(side=tk.LEFT, padx=5)
        ttk.Button(inspect_frame, text="검사 시작", 
                  command=self.start_inspection).pack(side=tk.LEFT, padx=5)
        ttk.Button(inspect_frame, text="검사 중지", 
                  command=self.stop_inspection).pack(side=tk.LEFT, padx=5)
        ttk.Button(inspect_frame, text="결과 저장", 
                  command=self.save_results).pack(side=tk.LEFT, padx=5)
        
        # 메인 콘텐츠 영역
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 테스트 패턴 생성
        left_frame = ttk.LabelFrame(content_frame, text="테스트 패턴 생성")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 패턴 설정
        settings_frame = ttk.Frame(left_frame)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 크기 설정
        size_frame = ttk.Frame(settings_frame)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="크기 설정:").pack(side=tk.LEFT)
        ttk.Label(size_frame, text="가로:").pack(side=tk.LEFT, padx=(10, 0))
        self.width_var = tk.StringVar(value="1920")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=8)
        width_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(size_frame, text="세로:").pack(side=tk.LEFT, padx=(10, 0))
        self.height_var = tk.StringVar(value="1080")
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=8)
        height_entry.pack(side=tk.LEFT, padx=2)
        
        # 인치 설정
        inch_frame = ttk.Frame(settings_frame)
        inch_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(inch_frame, text="인치 설정:").pack(side=tk.LEFT)
        ttk.Label(inch_frame, text="가로:").pack(side=tk.LEFT, padx=(10, 0))
        self.width_inch_var = tk.StringVar(value="20.0")
        width_inch_entry = ttk.Entry(inch_frame, textvariable=self.width_inch_var, width=8)
        width_inch_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(inch_frame, text="세로:").pack(side=tk.LEFT, padx=(10, 0))
        self.height_inch_var = tk.StringVar(value="11.25")
        height_inch_entry = ttk.Entry(inch_frame, textvariable=self.height_inch_var, width=8)
        height_inch_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(inch_frame, text="DPI:").pack(side=tk.LEFT, padx=(10, 0))
        self.dpi_var = tk.StringVar(value="96")
        dpi_entry = ttk.Entry(inch_frame, textvariable=self.dpi_var, width=6)
        dpi_entry.pack(side=tk.LEFT, padx=2)
        
        # 비율 설정
        ratio_frame = ttk.Frame(settings_frame)
        ratio_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ratio_frame, text="비율 설정:").pack(side=tk.LEFT)
        self.ratio_var = tk.StringVar(value="16:9")
        ratio_combo = ttk.Combobox(ratio_frame, textvariable=self.ratio_var, 
                                 values=["16:9", "16:10", "4:3", "21:9", "1:1", "사용자 정의"], width=10)
        ratio_combo.pack(side=tk.LEFT, padx=5)
        ratio_combo.bind('<<ComboboxSelected>>', self.on_ratio_changed)
        
        ttk.Button(ratio_frame, text="비율 적용", 
                  command=self.apply_ratio).pack(side=tk.LEFT, padx=5)
        
        # 패턴 표시
        self.pattern_label = ttk.Label(left_frame, text="테스트 패턴을 생성하세요")
        self.pattern_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 오른쪽: 카메라 뷰 및 검사 결과
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 카메라 뷰
        camera_view_frame = ttk.LabelFrame(right_frame, text="카메라 뷰 (검사 대상)")
        camera_view_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 10))
        
        self.camera_label = ttk.Label(camera_view_frame, text="카메라를 시작하세요")
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 검사 결과
        result_frame = ttk.LabelFrame(right_frame, text="검사 결과")
        result_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD)
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, 
                                       command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 품질 점수
        quality_frame = ttk.LabelFrame(right_frame, text="품질 점수")
        quality_frame.pack(fill=tk.X)
        
        self.quality_label = ttk.Label(quality_frame, text="품질 점수: --/100", 
                                     font=('Arial', 14, 'bold'))
        self.quality_label.pack(padx=10, pady=10)
        
        # 초기 로그
        self.log_result("테스트 패턴 생성 및 검사 시스템이 시작되었습니다.")
        self.log_result("1. 테스트 패턴을 생성하세요")
        self.log_result("2. 카메라를 시작하고 패널을 감지하세요")
        self.log_result("3. 검사를 시작하여 데드픽셀과 색상 균일성을 확인하세요")
        
    def on_ratio_changed(self, event=None):
        """비율 변경 처리"""
        ratio = self.ratio_var.get()
        if ratio != "사용자 정의":
            self.apply_ratio()
    
    def apply_ratio(self):
        """비율 적용"""
        try:
            ratio = self.ratio_var.get()
            if ratio == "사용자 정의":
                return
            
            # 비율 파싱
            w_ratio, h_ratio = map(int, ratio.split(':'))
            
            # 현재 가로 크기 기준으로 세로 계산
            current_width = int(self.width_var.get())
            new_height = int(current_width * h_ratio / w_ratio)
            
            self.height_var.set(str(new_height))
            
            # 인치도 업데이트
            dpi = int(self.dpi_var.get())
            width_inch = current_width / dpi
            height_inch = new_height / dpi
            
            self.width_inch_var.set(f"{width_inch:.2f}")
            self.height_inch_var.set(f"{height_inch:.2f}")
            
            self.log_result(f"비율 {ratio} 적용: {current_width}x{new_height}")
            
        except Exception as e:
            self.log_result(f"비율 적용 오류: {str(e)}")
    
    def generate_red_test(self):
        """Red 테스트 패턴 생성 (순수한 빨간색)"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # Red 테스트 패턴 생성 - 전체 화면을 순수한 Red로 채움
            pattern = np.zeros((height, width, 3), dtype=np.uint8)
            pattern[:, :, 2] = 255  # Red 채널만 활성화 (BGR 형식: 0,0,255)
            
            self.test_pattern = pattern
            self.display_pattern(pattern)
            self.log_result("Red 테스트 패턴이 생성되었습니다 (순수한 빨간색).")
            
        except Exception as e:
            self.log_result(f"Red 테스트 패턴 생성 오류: {str(e)}")
    
    def generate_green_test(self):
        """Green 테스트 패턴 생성 (순수한 초록색)"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # Green 테스트 패턴 생성 - 전체 화면을 순수한 Green으로 채움
            pattern = np.zeros((height, width, 3), dtype=np.uint8)
            pattern[:, :, 1] = 255  # Green 채널만 활성화 (BGR 형식: 0,255,0)
            
            self.test_pattern = pattern
            self.display_pattern(pattern)
            self.log_result("Green 테스트 패턴이 생성되었습니다 (순수한 초록색).")
            
        except Exception as e:
            self.log_result(f"Green 테스트 패턴 생성 오류: {str(e)}")
    
    def generate_blue_test(self):
        """Blue 테스트 패턴 생성 (순수한 파란색)"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # Blue 테스트 패턴 생성 - 전체 화면을 순수한 Blue로 채움
            pattern = np.zeros((height, width, 3), dtype=np.uint8)
            pattern[:, :, 0] = 255  # Blue 채널만 활성화 (BGR 형식: 255,0,0)
            
            self.test_pattern = pattern
            self.display_pattern(pattern)
            self.log_result("Blue 테스트 패턴이 생성되었습니다 (순수한 파란색).")
            
        except Exception as e:
            self.log_result(f"Blue 테스트 패턴 생성 오류: {str(e)}")
    
    def add_red_defect_pixels(self, pattern, width, height):
        """Red 영역에 데드픽셀 시뮬레이션 추가"""
        try:
            # 데드픽셀 추가 (검은 점들)
            for _ in range(12):
                x = np.random.randint(50, width-50)
                y = np.random.randint(50, height-50)
                size = np.random.randint(1, 4)
                cv2.circle(pattern, (x, y), size, (0, 0, 0), -1)  # 검은 점 (데드픽셀)
            
            # 일부 영역에 색상 불균일성 추가
            for _ in range(5):
                x = np.random.randint(100, width-100)
                y = np.random.randint(100, height-100)
                size = np.random.randint(15, 30)
                # 어두운 Red 영역
                cv2.rectangle(pattern, (x, y), (x+size, y+size), (0, 0, 180), -1)
                    
        except Exception as e:
            self.log_result(f"Red 불량픽셀 추가 오류: {str(e)}")
    
    def add_green_defect_pixels(self, pattern, width, height):
        """Green 영역에 핫픽셀 시뮬레이션 추가"""
        try:
            # 핫픽셀 추가 (밝은 점들)
            for _ in range(8):
                x = np.random.randint(50, width-50)
                y = np.random.randint(50, height-50)
                size = np.random.randint(1, 3)
                cv2.circle(pattern, (x, y), size, (255, 255, 255), -1)  # 흰 점 (핫픽셀)
            
            # 일부 영역에 색상 불균일성 추가
            for _ in range(4):
                x = np.random.randint(100, width-100)
                y = np.random.randint(100, height-100)
                size = np.random.randint(20, 35)
                # 밝은 Green 영역
                cv2.rectangle(pattern, (x, y), (x+size, y+size), (0, 255, 255), -1)
                    
        except Exception as e:
            self.log_result(f"Green 불량픽셀 추가 오류: {str(e)}")
    
    def add_blue_defect_pixels(self, pattern, width, height):
        """Blue 영역에 색상 불균일성 시뮬레이션 추가"""
        try:
            # 색상 불균일성 추가 (다양한 Blue 톤)
            for _ in range(6):
                x = np.random.randint(100, width-100)
                y = np.random.randint(100, height-100)
                size = np.random.randint(25, 40)
                # 다양한 Blue 톤
                blue_intensity = np.random.randint(150, 255)
                cv2.rectangle(pattern, (x, y), (x+size, y+size), (blue_intensity, 0, 0), -1)
            
            # 일부 데드픽셀도 추가
            for _ in range(6):
                x = np.random.randint(50, width-50)
                y = np.random.randint(50, height-50)
                size = np.random.randint(1, 3)
                cv2.circle(pattern, (x, y), size, (0, 0, 0), -1)  # 검은 점
                    
        except Exception as e:
            self.log_result(f"Blue 불량픽셀 추가 오류: {str(e)}")
    
    def adjust_focus(self):
        """웹캠 초점 조정"""
        if not self.camera_running:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        try:
            # 초점 조정 창 생성
            focus_window = tk.Toplevel(self.root)
            focus_window.title("웹캠 초점 조정")
            focus_window.geometry("400x300")
            
            # 초점 조정 슬라이더
            ttk.Label(focus_window, text="초점 조정 (0=무한대, 255=가까운 거리):").pack(pady=10)
            
            focus_var = tk.IntVar(value=0)
            focus_scale = ttk.Scale(focus_window, from_=0, to=255, 
                                  variable=focus_var, orient=tk.HORIZONTAL, length=300)
            focus_scale.pack(pady=10)
            
            # 실시간 초점 조정
            def update_focus(value):
                try:
                    self.camera.set(cv2.CAP_PROP_FOCUS, int(value))
                    self.log_result(f"초점 조정: {int(value)}")
                except:
                    pass
            
            focus_scale.configure(command=update_focus)
            
            # 다른 설정들
            ttk.Label(focus_window, text="노출 조정:").pack(pady=(20, 5))
            exposure_var = tk.IntVar(value=-6)
            exposure_scale = ttk.Scale(focus_window, from_=-13, to=0, 
                                     variable=exposure_var, orient=tk.HORIZONTAL, length=300)
            exposure_scale.pack(pady=5)
            
            def update_exposure(value):
                try:
                    self.camera.set(cv2.CAP_PROP_EXPOSURE, int(value))
                    self.log_result(f"노출 조정: {int(value)}")
                except:
                    pass
            
            exposure_scale.configure(command=update_exposure)
            
            # 밝기 조정
            ttk.Label(focus_window, text="밝기 조정:").pack(pady=(20, 5))
            brightness_var = tk.IntVar(value=128)
            brightness_scale = ttk.Scale(focus_window, from_=0, to=255, 
                                       variable=brightness_var, orient=tk.HORIZONTAL, length=300)
            brightness_scale.pack(pady=5)
            
            def update_brightness(value):
                try:
                    self.camera.set(cv2.CAP_PROP_BRIGHTNESS, int(value))
                    self.log_result(f"밝기 조정: {int(value)}")
                except:
                    pass
            
            brightness_scale.configure(command=update_brightness)
            
            # 닫기 버튼
            ttk.Button(focus_window, text="닫기", 
                      command=focus_window.destroy).pack(pady=20)
            
        except Exception as e:
            self.log_result(f"초점 조정 오류: {str(e)}")
    
    def reset_camera_settings(self):
        """웹캠 설정 초기화"""
        if not self.camera_running:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        try:
            # 기본 설정으로 초기화
            self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            self.camera.set(cv2.CAP_PROP_EXPOSURE, -6)
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            self.camera.set(cv2.CAP_PROP_FOCUS, 0)
            self.camera.set(cv2.CAP_PROP_GAIN, 0)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, 128)
            self.camera.set(cv2.CAP_PROP_CONTRAST, 128)
            self.camera.set(cv2.CAP_PROP_SATURATION, 128)
            
            self.log_result("웹캠 설정이 초기화되었습니다.")
            
        except Exception as e:
            self.log_result(f"웹캠 설정 초기화 오류: {str(e)}")
    
    def adjust_polarizer(self):
        """편광필터 각도 조정"""
        try:
            # 편광필터 조정 창 생성
            polarizer_window = tk.Toplevel(self.root)
            polarizer_window.title("편광필터 각도 조정")
            polarizer_window.geometry("400x200")
            
            # 편광 각도 조정
            ttk.Label(polarizer_window, text="편광필터 각도 (0°=수직, 90°=수평):").pack(pady=10)
            
            angle_var = tk.IntVar(value=self.polarizer_angle)
            angle_scale = ttk.Scale(polarizer_window, from_=0, to=180, 
                                  variable=angle_var, orient=tk.HORIZONTAL, length=300)
            angle_scale.pack(pady=10)
            
            # 실시간 각도 조정
            def update_angle(value):
                self.polarizer_angle = int(value)
                self.log_result(f"편광필터 각도: {int(value)}°")
            
            angle_scale.configure(command=update_angle)
            
            # 설명 텍스트
            info_text = """
편광필터 효과:
• 0°-30°: 반사 최대 감소 (수직 편광)
• 60°-90°: 글로우 효과 감소
• 120°-150°: 색상 대비 향상
• 150°-180°: 디테일 선명도 향상
            """
            ttk.Label(polarizer_window, text=info_text, justify=tk.LEFT).pack(pady=10)
            
            # 닫기 버튼
            ttk.Button(polarizer_window, text="닫기", 
                      command=polarizer_window.destroy).pack(pady=10)
            
        except Exception as e:
            self.log_result(f"편광필터 조정 오류: {str(e)}")
    
    def apply_vignetting_correction(self, frame):
        """비네팅 보정 적용"""
        if not self.vignetting_correction.get():
            return frame
        
        try:
            height, width = frame.shape[:2]
            
            # 중심점 계산
            center_x, center_y = width // 2, height // 2
            
            # 최대 반지름 (이미지 대각선의 절반)
            max_radius = np.sqrt(center_x**2 + center_y**2)
            
            # 비네팅 보정 마스크 생성
            y, x = np.ogrid[:height, :width]
            
            # 각 픽셀의 중심으로부터의 거리 계산
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            
            # 비네팅 보정 계수 (거리가 멀수록 더 밝게)
            vignette_factor = 1.0 + (distance / max_radius) * 0.3  # 30% 보정
            
            # 보정 적용
            result = frame.copy().astype(np.float32)
            result = result * vignette_factor[..., np.newaxis]
            
            # 값 범위 제한
            result = np.clip(result, 0, 255).astype(np.uint8)
            
            return result
            
        except Exception as e:
            self.log_result(f"비네팅 보정 오류: {str(e)}")
            return frame
    
    def apply_polarizer_effect(self, frame):
        """편광필터 효과 적용"""
        if not self.polarizer_enabled.get():
            return frame
        
        try:
            # 편광필터 시뮬레이션
            # 각도에 따른 효과 계산
            angle_rad = np.radians(self.polarizer_angle)
            
            # 반사 감소 효과 (0-30도에서 최대)
            reflection_reduction = np.cos(angle_rad) if self.polarizer_angle <= 30 else 0.5
            
            # 글로우 감소 효과 (60-90도에서 최대)
            glow_reduction = np.sin(angle_rad) if 60 <= self.polarizer_angle <= 90 else 0.3
            
            # 색상 대비 향상 (120-150도에서 최대)
            contrast_enhancement = np.sin(angle_rad) if 120 <= self.polarizer_angle <= 150 else 0.2
            
            # 디테일 선명도 향상 (150-180도에서 최대)
            sharpness_enhancement = np.cos(angle_rad) if 150 <= self.polarizer_angle <= 180 else 0.1
            
            # 효과 적용
            result = frame.copy().astype(np.float32)
            
            # 반사 감소 (밝은 영역 감소)
            if reflection_reduction > 0:
                bright_mask = result > 200
                result[bright_mask] = result[bright_mask] * (1 - reflection_reduction * 0.3)
            
            # 글로우 감소 (부드러운 그라데이션 감소)
            if glow_reduction > 0:
                kernel = np.ones((3, 3), np.float32) / 9
                blurred = cv2.filter2D(result, -1, kernel)
                result = result * (1 - glow_reduction * 0.2) + blurred * (glow_reduction * 0.2)
            
            # 색상 대비 향상
            if contrast_enhancement > 0:
                result = result * (1 + contrast_enhancement * 0.1)
            
            # 디테일 선명도 향상
            if sharpness_enhancement > 0:
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                sharpened = cv2.filter2D(result, -1, kernel)
                result = result * (1 - sharpness_enhancement * 0.1) + sharpened * (sharpness_enhancement * 0.1)
            
            # 값 범위 제한
            result = np.clip(result, 0, 255).astype(np.uint8)
            
            return result
            
        except Exception as e:
            self.log_result(f"편광필터 효과 적용 오류: {str(e)}")
            return frame
    
    def generate_defect_simulation(self):
        """불량픽셀 시뮬레이션 패턴 생성"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # 흰색 배경에 불량픽셀 시뮬레이션 추가
            pattern = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            # 데드픽셀 (검은 점들)
            for _ in range(20):
                x = np.random.randint(50, width-50)
                y = np.random.randint(50, height-50)
                size = np.random.randint(1, 4)
                cv2.circle(pattern, (x, y), size, (0, 0, 0), -1)
            
            # 핫픽셀 (흰 점들)
            for _ in range(15):
                x = np.random.randint(50, width-50)
                y = np.random.randint(50, height-50)
                size = np.random.randint(1, 3)
                cv2.circle(pattern, (x, y), size, (255, 255, 255), -1)
            
            # 색상 불균일성 (다양한 색상의 사각형들)
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
            for _ in range(10):
                x = np.random.randint(100, width-100)
                y = np.random.randint(100, height-100)
                size = np.random.randint(20, 50)
                color = colors[np.random.randint(0, len(colors))]
                cv2.rectangle(pattern, (x, y), (x+size, y+size), color, -1)
            
            self.test_pattern = pattern
            self.display_pattern(pattern)
            self.log_result("불량픽셀 시뮬레이션 패턴이 생성되었습니다.")
            
        except Exception as e:
            self.log_result(f"불량픽셀 시뮬레이션 생성 오류: {str(e)}")
    
    def generate_dead_pixel_test(self):
        """데드픽셀 테스트 패턴 생성"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # 데드픽셀 테스트 패턴 생성
            pattern = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 전체를 흰색으로 채우기
            pattern.fill(255)
            
            # 데드픽셀 시뮬레이션 (검은 점들)
            num_dead_pixels = 50
            for _ in range(num_dead_pixels):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(1, 4)
                cv2.circle(pattern, (x, y), size, (0, 0, 0), -1)
            
            # 핫픽셀 시뮬레이션 (밝은 점들)
            num_hot_pixels = 20
            for _ in range(num_hot_pixels):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                size = np.random.randint(1, 3)
                cv2.circle(pattern, (x, y), size, (255, 255, 255), -1)
            
            # 그리드 추가 (데드픽셀 위치 확인용)
            grid_size = 100
            for i in range(0, width, grid_size):
                cv2.line(pattern, (i, 0), (i, height), (200, 200, 200), 1)
            for i in range(0, height, grid_size):
                cv2.line(pattern, (0, i), (width, i), (200, 200, 200), 1)
            
            # 제목 제거 (깔끔한 패턴)
            
            self.test_pattern = pattern
            self.display_pattern(pattern)
            self.log_result("데드픽셀 테스트 패턴이 생성되었습니다.")
            
        except Exception as e:
            self.log_result(f"데드픽셀 테스트 패턴 생성 오류: {str(e)}")
    
    def generate_uniformity_test(self):
        """색상 균일성 테스트 패턴 생성"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            # 색상 균일성 테스트 패턴 생성
            pattern = np.zeros((height, width, 3), dtype=np.uint8)
            
            # 그라데이션 패턴 생성
            for y in range(height):
                for x in range(width):
                    # Red 그라데이션
                    r = int(255 * x / width)
                    # Green 그라데이션
                    g = int(255 * y / height)
                    # Blue 그라데이션
                    b = int(255 * (x + y) / (width + height))
                    
                    pattern[y, x] = [b, g, r]  # BGR 형식
            
            # 그리드 추가
            grid_size = 50
            for i in range(0, width, grid_size):
                cv2.line(pattern, (i, 0), (i, height), (255, 255, 255), 1)
            for i in range(0, height, grid_size):
                cv2.line(pattern, (0, i), (width, i), (255, 255, 255), 1)
            
            # 제목 제거 (깔끔한 패턴)
            
            self.test_pattern = pattern
            self.display_pattern(pattern)
            self.log_result("색상 균일성 테스트 패턴이 생성되었습니다.")
            
        except Exception as e:
            self.log_result(f"색상 균일성 테스트 패턴 생성 오류: {str(e)}")
    
    def display_pattern(self, pattern):
        """패턴을 UI에 표시"""
        try:
            # 이미지 크기 조정
            height, width = pattern.shape[:2]
            max_width, max_height = 600, 400
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                display_pattern = cv2.resize(pattern, (new_width, new_height))
            else:
                display_pattern = pattern
            
            # BGR을 RGB로 변환
            display_pattern = cv2.cvtColor(display_pattern, cv2.COLOR_BGR2RGB)
            
            # PIL 이미지로 변환
            pil_image = Image.fromarray(display_pattern)
            photo = ImageTk.PhotoImage(pil_image)
            
            # 라벨에 이미지 설정
            self.pattern_label.configure(image=photo, text="")
            self.pattern_label.image = photo  # 참조 유지
            
        except Exception as e:
            self.log_result(f"패턴 표시 오류: {str(e)}")
    
    def start_camera(self):
        """웹캠 시작"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("오류", "웹캠을 열 수 없습니다.")
                return
            
            # 웹캠 설정 (최대 해상도 사용)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            # 수동 설정으로 초점 및 노출 최적화
            self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 수동 노출
            self.camera.set(cv2.CAP_PROP_EXPOSURE, -6)  # 노출 조정
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # 자동 초점 비활성화
            self.camera.set(cv2.CAP_PROP_FOCUS, 0)  # 초점을 무한대로 설정
            self.camera.set(cv2.CAP_PROP_GAIN, 0)  # 게인 최소화
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, 128)  # 밝기 중간값
            self.camera.set(cv2.CAP_PROP_CONTRAST, 128)  # 대비 중간값
            self.camera.set(cv2.CAP_PROP_SATURATION, 128)  # 채도 중간값
            
            # 실제 설정된 해상도 확인
            actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(self.camera.get(cv2.CAP_PROP_FPS))
            
            self.camera_running = True
            self.log_result(f"웹캠이 시작되었습니다.")
            self.log_result(f"해상도: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # 카메라 스레드 시작
            self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.camera_thread.start()
            
        except Exception as e:
            messagebox.showerror("오류", f"웹캠 시작 중 오류: {str(e)}")
    
    def stop_camera(self):
        """카메라 중지"""
        self.camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.log_result("카메라가 중지되었습니다.")
        self.camera_label.configure(image='', text="카메라가 중지되었습니다")
    
    def camera_loop(self):
        """카메라 루프"""
        while self.camera_running and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    self.current_frame = frame.copy()
                    self.update_camera_display(frame)
                time.sleep(0.03)  # 30 FPS
            except Exception as e:
                self.log_result(f"카메라 루프 오류: {str(e)}")
                break
    
    def update_camera_display(self, frame):
        """카메라 디스플레이 업데이트"""
        try:
            # 비네팅 보정 적용
            frame = self.apply_vignetting_correction(frame)
            
            # 편광필터 효과 적용
            frame = self.apply_polarizer_effect(frame)
            
            # 반사 제거 적용
            if self.reflection_removal_enabled:
                frame = self.apply_reflection_removal(frame)
            
            # 스크래치 검사 적용
            if self.scratch_detection_active:
                # 조명 시뮬레이션 적용
                frame = self.apply_lighting_simulation(frame, self.lighting_angle, self.lighting_intensity)
                
                # 스크래치 감지
                scratches = self.detect_scratches(frame)
                frame = self.draw_scratch_analysis(frame, scratches)
            
            # 패널 감지 결과 표시
            display_frame = self.draw_panel_detection(frame)
            
            # 이미지 크기 조정
            height, width = display_frame.shape[:2]
            max_width, max_height = 600, 400
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                display_frame = cv2.resize(display_frame, (new_width, new_height))
            
            # BGR을 RGB로 변환
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            
            # PIL 이미지로 변환
            pil_image = Image.fromarray(display_frame)
            photo = ImageTk.PhotoImage(pil_image)
            
            # 라벨에 이미지 설정
            self.camera_label.configure(image=photo, text="")
            self.camera_label.image = photo  # 참조 유지
            
        except Exception as e:
            self.log_result(f"디스플레이 업데이트 오류: {str(e)}")
    
    def apply_reflection_removal(self, frame):
        """반사 제거 적용"""
        try:
            # 밝기 조정
            result = cv2.convertScaleAbs(frame, alpha=self.brightness_level, beta=0)
            
            # 반사 영역 감지
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
            
            # 모폴로지 연산
            kernel = np.ones((5, 5), np.uint8)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
            
            # 반사 영역에 블러 적용
            blurred = cv2.GaussianBlur(result, (15, 15), 0)
            result[bright_mask > 0] = blurred[bright_mask > 0]
            
            return result
            
        except Exception as e:
            return frame
    
    def draw_panel_detection(self, frame):
        """패널 감지 결과 그리기"""
        display_frame = frame.copy()
        
        # 정확한 사각형 표시
        if self.panel_rectangle is not None:
            x, y, w, h = self.panel_rectangle
            
            # 패널 완전성에 따른 색상 결정
            if self.panel_detected:
                color = (0, 255, 0)  # 녹색 - 완전함
                status_text = "Panel OK"
            else:
                color = (0, 0, 255)  # 빨간색 - 불완전함
                status_text = "Panel Incomplete"
            
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 3)
            
            # 모서리 마커
            corner_size = 15
            cv2.line(display_frame, (x, y), (x + corner_size, y), color, 5)
            cv2.line(display_frame, (x, y), (x, y + corner_size), color, 5)
            cv2.line(display_frame, (x+w, y), (x+w - corner_size, y), color, 5)
            cv2.line(display_frame, (x+w, y), (x+w, y + corner_size), color, 5)
            cv2.line(display_frame, (x, y+h), (x + corner_size, y+h), color, 5)
            cv2.line(display_frame, (x, y+h), (x, y+h - corner_size), color, 5)
            cv2.line(display_frame, (x+w, y+h), (x+w - corner_size, y+h), color, 5)
            cv2.line(display_frame, (x+w, y+h), (x+w, y+h - corner_size), color, 5)
            
            # 패널 엣지 강조 (윤곽선이 있는 경우)
            if hasattr(self, 'panel_edges') and self.panel_edges is not None:
                for i in range(len(self.panel_edges)):
                    pt1 = tuple(self.panel_edges[i])
                    pt2 = tuple(self.panel_edges[(i + 1) % len(self.panel_edges)])
                    cv2.line(display_frame, pt1, pt2, color, 2)
                
                # 엣지 포인트 표시
                for point in self.panel_edges:
                    cv2.circle(display_frame, tuple(point), 5, color, -1)
            
            # 패널 정보 표시
            cv2.putText(display_frame, f"{status_text}: {w}x{h}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # 패널 완전성 상태 표시
            if self.panel_detected:
                cv2.putText(display_frame, "READY FOR INSPECTION", (x, y+h+25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "ADJUST CAMERA POSITION", (x, y+h+25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return display_frame
    
    def detect_panel(self):
        """패널 감지 및 완전성 검사"""
        if self.current_frame is None:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        try:
            # 패널 감지 알고리즘
            panel_contour = self.detect_panel_contour(self.current_frame)
            
            if panel_contour is not None:
                # 정확한 사각형 추출
                rectangle = self.extract_rectangle_from_contour(panel_contour)
                
                if rectangle is not None:
                    # 패널 완전성 검사
                    if self.check_panel_completeness(rectangle):
                        self.panel_rectangle = rectangle
                        self.panel_detected = True
                        
                        # 패널 엣지 정보 저장
                        self.panel_edges = panel_contour.reshape(-1, 2)
                        
                        self.log_result("패널이 성공적으로 감지되었습니다.")
                        self.log_result(f"패널 크기: {rectangle[2]}x{rectangle[3]}")
                        self.log_result("패널이 완전히 보입니다. 검사 가능합니다.")
                    else:
                        self.log_result("패널이 화면에서 잘렸습니다.")
                        self.log_result("카메라 위치를 조정하여 패널 전체가 보이도록 하세요.")
                        self.panel_detected = False
                else:
                    self.log_result("패널을 감지했지만 사각형 추출에 실패했습니다.")
            else:
                self.log_result("패널을 감지할 수 없습니다. 패널 위치를 조정하고 다시 시도하세요.")
                
        except Exception as e:
            self.log_result(f"패널 감지 오류: {str(e)}")
    
    def check_panel_completeness(self, rectangle):
        """패널이 화면에 완전히 보이는지 확인 - 완화된 조건"""
        try:
            x, y, w, h = rectangle
            frame_height, frame_width = self.current_frame.shape[:2]
            
            # 패널이 화면 경계에서 충분한 여백을 가지는지 확인 (여백 완화)
            margin = 10  # 픽셀 여백 (20에서 10으로 완화)
            
            # 패널이 화면 경계에 너무 가까운지 확인
            if (x < margin or y < margin or 
                x + w > frame_width - margin or 
                y + h > frame_height - margin):
                self.log_result(f"패널이 화면 경계에 너무 가까움: x={x}, y={y}, w={w}, h={h}")
                return False
            
            # 패널 크기가 화면의 최소 비율을 만족하는지 확인 (비율 완화)
            panel_area = w * h
            frame_area = frame_width * frame_height
            min_coverage = 0.15  # 최소 15% 커버리지 (30%에서 15%로 완화)
            
            if panel_area < frame_area * min_coverage:
                self.log_result(f"패널이 너무 작음: {panel_area}/{frame_area} ({panel_area/frame_area*100:.1f}%)")
                return False
            
            # 패널 비율이 합리적인지 확인 (비율 범위 완화)
            aspect_ratio = w / h
            if aspect_ratio < 0.3 or aspect_ratio > 5.0:  # 0.5-3.0에서 0.3-5.0으로 완화
                self.log_result(f"패널 비율이 부적절함: {aspect_ratio:.2f}")
                return False
            
            self.log_result(f"패널 완전성 검사 통과: {w}x{h}, 비율={aspect_ratio:.2f}, 커버리지={panel_area/frame_area*100:.1f}%")
            return True
            
        except Exception as e:
            self.log_result(f"패널 완전성 검사 오류: {str(e)}")
            return False
    
    def detect_panel_contour(self, frame):
        """RGB 색상 영역을 직접 감지하여 패널 찾기"""
        try:
            # BGR 채널 분리
            b, g, r = cv2.split(frame)
            
            # 각 채널별로 강한 색상 영역 찾기
            # 빨간색 영역 (Red 테스트)
            red_strong = cv2.threshold(r, 150, 255, cv2.THRESH_BINARY)[1]
            red_weak = cv2.threshold(g, 100, 255, cv2.THRESH_BINARY_INV)[1]
            red_weak2 = cv2.threshold(b, 100, 255, cv2.THRESH_BINARY_INV)[1]
            red_mask = cv2.bitwise_and(red_strong, red_weak)
            red_mask = cv2.bitwise_and(red_mask, red_weak2)
            
            # 초록색 영역 (Green 테스트)
            green_strong = cv2.threshold(g, 150, 255, cv2.THRESH_BINARY)[1]
            green_weak = cv2.threshold(r, 100, 255, cv2.THRESH_BINARY_INV)[1]
            green_weak2 = cv2.threshold(b, 100, 255, cv2.THRESH_BINARY_INV)[1]
            green_mask = cv2.bitwise_and(green_strong, green_weak)
            green_mask = cv2.bitwise_and(green_mask, green_weak2)
            
            # 파란색 영역 (Blue 테스트)
            blue_strong = cv2.threshold(b, 150, 255, cv2.THRESH_BINARY)[1]
            blue_weak = cv2.threshold(r, 100, 255, cv2.THRESH_BINARY_INV)[1]
            blue_weak2 = cv2.threshold(g, 100, 255, cv2.THRESH_BINARY_INV)[1]
            blue_mask = cv2.bitwise_and(blue_strong, blue_weak)
            blue_mask = cv2.bitwise_and(blue_mask, blue_weak2)
            
            # 모든 색상 마스크 결합
            color_mask = red_mask + green_mask + blue_mask
            
            # 마스크 정리 (노이즈 제거)
            kernel = np.ones((3, 3), np.uint8)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
            
            # 컨투어 찾기
            contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 면적별로 정렬
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                for contour in contours[:5]:  # 상위 5개 검사
                    area = cv2.contourArea(contour)
                    if area > 2000:  # 최소 면적 (더 낮게 설정)
                        # 사각형으로 근사 (매우 유연하게)
                        epsilon = 0.1 * cv2.arcLength(contour, True)  # 매우 큰 epsilon
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) >= 4:  # 4개 이상의 꼭짓점
                            self.log_result(f"RGB 색상 기반 패널 감지 성공: 면적 {area}")
                            return contour
            
            # RGB 색상 감지가 실패하면 밝기 기반으로 시도
            self.log_result("RGB 색상 감지 실패, 밝기 기반으로 시도")
            return self.detect_by_brightness(frame)
            
        except Exception as e:
            self.log_result(f"패널 윤곽선 감지 오류: {str(e)}")
            return None
    
    def detect_by_brightness(self, frame):
        """밝기 기반으로 패널 감지 - 개선된 방법"""
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 적응적 임계값으로 밝은 영역 찾기
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((3, 3), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # 컨투어 찾기
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 면적별로 정렬
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                for contour in contours[:5]:  # 상위 5개 검사
                    area = cv2.contourArea(contour)
                    if area > 2000:  # 최소 면적 (더 낮게 설정)
                        # 사각형으로 근사 (매우 유연하게)
                        epsilon = 0.1 * cv2.arcLength(contour, True)  # 매우 큰 epsilon
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) >= 4:  # 4개 이상의 꼭짓점
                            self.log_result(f"밝기 기반 패널 감지 성공: 면적 {area}")
                            return contour
            
            # 밝기 기반도 실패하면 간단한 임계값으로 시도
            self.log_result("적응적 임계값 실패, 단순 임계값으로 시도")
            return self.detect_by_simple_threshold(frame)
            
        except Exception as e:
            self.log_result(f"밝기 기반 감지 오류: {str(e)}")
            return None
    
    def detect_by_simple_threshold(self, frame):
        """단순 임계값으로 패널 감지"""
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 여러 임계값으로 시도
            thresholds = [80, 100, 120, 150]
            
            for thresh_val in thresholds:
                _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
                
                # 모폴로지 연산
                kernel = np.ones((5, 5), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                
                # 컨투어 찾기
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # 면적별로 정렬
                    contours = sorted(contours, key=cv2.contourArea, reverse=True)
                    
                    for contour in contours[:3]:
                        area = cv2.contourArea(contour)
                        if area > 1500:  # 매우 낮은 임계값
                            # 사각형으로 근사 (매우 유연하게)
                            epsilon = 0.15 * cv2.arcLength(contour, True)  # 매우 큰 epsilon
                            approx = cv2.approxPolyDP(contour, epsilon, True)
                            
                            if len(approx) >= 4:  # 4개 이상의 꼭짓점
                                self.log_result(f"단순 임계값({thresh_val}) 패널 감지 성공: 면적 {area}")
                                return contour
            
            self.log_result("모든 감지 방법 실패")
            return None
            
        except Exception as e:
            self.log_result(f"단순 임계값 감지 오류: {str(e)}")
            return None
    
    def detect_by_canny(self, blurred, frame):
        """Canny 엣지 감지로 패널 찾기"""
        try:
            # Canny 엣지 감지
            edges = cv2.Canny(blurred, 50, 150)
            
            # 모폴로지 연산으로 엣지 강화
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # 컨투어 찾기
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 면적별로 정렬
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                for contour in contours[:3]:  # 상위 3개만 검사
                    area = cv2.contourArea(contour)
                    if area > 5000:  # 최소 면적
                        # 사각형으로 근사
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) >= 4:  # 4개 이상의 꼭짓점
                            return contour
            
            return None
            
        except Exception as e:
            return None
    
    def detect_by_threshold(self, blurred, frame):
        """임계값 기반으로 패널 찾기"""
        try:
            # 적응적 임계값
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # 모폴로지 연산
            kernel = np.ones((5, 5), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # 컨투어 찾기
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 면적별로 정렬
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                for contour in contours[:3]:
                    area = cv2.contourArea(contour)
                    if area > 5000:
                        # 사각형으로 근사
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) >= 4:
                            return contour
            
            return None
            
        except Exception as e:
            return None
    
    def detect_by_color_variance(self, blurred, frame):
        """색상 분산으로 패널 영역 찾기"""
        try:
            # 색상 분산 계산 (RGB 영상이 있는 영역)
            b, g, r = cv2.split(frame)
            
            # 각 채널의 분산 계산
            b_var = cv2.Laplacian(b, cv2.CV_64F).var()
            g_var = cv2.Laplacian(g, cv2.CV_64F).var()
            r_var = cv2.Laplacian(r, cv2.CV_64F).var()
            
            # 색상 변화가 큰 영역 찾기
            color_variance = cv2.Laplacian(blurred, cv2.CV_64F)
            color_variance = np.uint8(np.absolute(color_variance))
            
            # 임계값 적용
            _, thresh = cv2.threshold(color_variance, 30, 255, cv2.THRESH_BINARY)
            
            # 모폴로지 연산
            kernel = np.ones((5, 5), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # 컨투어 찾기
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 면적별로 정렬
                contours = sorted(contours, key=cv2.contourArea, reverse=True)
                
                for contour in contours[:3]:
                    area = cv2.contourArea(contour)
                    if area > 5000:
                        # 사각형으로 근사
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        if len(approx) >= 4:
                            return contour
            
            return None
            
        except Exception as e:
            return None
    
    def evaluate_contour_quality(self, contour, frame):
        """컨투어 품질 평가"""
        try:
            # 면적 점수
            area = cv2.contourArea(contour)
            area_score = min(area / 10000, 1.0)  # 10000 이상이면 1점
            
            # 사각형 근사 점수
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            rect_score = 1.0 if len(approx) == 4 else 0.5
            
            # 종횡비 점수
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if 0.5 <= aspect_ratio <= 2.0:  # 합리적인 비율
                ratio_score = 1.0
            else:
                ratio_score = 0.3
            
            # 전체 점수 계산
            total_score = (area_score * 0.4 + rect_score * 0.4 + ratio_score * 0.2)
            
            return total_score
            
        except Exception as e:
            return 0.0
    
    def extract_rectangle_from_contour(self, contour):
        """윤곽선에서 정확한 사각형 추출"""
        try:
            # 경계 상자 계산
            x, y, w, h = cv2.boundingRect(contour)
            
            # 윤곽선 근사화
            epsilon = 0.005 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # 사각형인지 확인
            if len(approx) >= 4:
                # 꼭짓점들을 정렬
                approx = approx.reshape(-1, 2)
                
                # 사각형의 경계 계산
                x_min = int(np.min(approx[:, 0]))
                y_min = int(np.min(approx[:, 1]))
                x_max = int(np.max(approx[:, 0]))
                y_max = int(np.max(approx[:, 1]))
                
                return (x_min, y_min, x_max - x_min, y_max - y_min)
            
            # 사각형이 아닌 경우 경계 상자 사용
            return (x, y, w, h)
            
        except Exception as e:
            return None
    
    def start_inspection(self):
        """검사 시작"""
        if self.panel_rectangle is None:
            messagebox.showwarning("경고", "먼저 패널을 감지하세요.")
            return
        
        if not self.camera_running:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        # 패널 완전성 재확인
        if not self.panel_detected:
            messagebox.showwarning("경고", "패널이 완전히 보이지 않습니다. 카메라 위치를 조정하세요.")
            return
        
        # 패널 완전성 실시간 검사
        if not self.check_panel_completeness(self.panel_rectangle):
            messagebox.showwarning("경고", "패널이 화면에서 잘렸습니다. 카메라 위치를 조정하세요.")
            return
        
        self.inspection_running = True
        self.log_result("검사가 시작되었습니다.")
        self.log_result("패널 완전성 확인 완료 - 검사 진행 가능")
        
        # 검사 스레드 시작
        self.inspection_thread = threading.Thread(target=self.inspection_loop, daemon=True)
        self.inspection_thread.start()
    
    def stop_inspection(self):
        """검사 중지"""
        self.inspection_running = False
        self.log_result("검사가 중지되었습니다.")
    
    def inspection_loop(self):
        """검사 루프"""
        while self.inspection_running and self.camera_running:
            try:
                if self.current_frame is not None and self.panel_rectangle is not None:
                    # 정확한 사각형 영역 추출
                    panel_region = self.extract_rectangle_region(self.current_frame, self.panel_rectangle)
                    
                    if panel_region is not None:
                        # 검사 실행
                        results = self.perform_inspection(panel_region)
                        self.update_inspection_results(results)
                
                time.sleep(2)  # 2초마다 검사
                
            except Exception as e:
                self.log_result(f"검사 루프 오류: {str(e)}")
                break
    
    def extract_rectangle_region(self, frame, rectangle):
        """정확한 사각형 영역 추출"""
        try:
            x, y, w, h = rectangle
            
            # 경계 확인
            if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
                return None
            
            # 사각형 영역 추출
            panel_region = frame[y:y+h, x:x+w]
            
            return panel_region
            
        except Exception as e:
            return None
    
    def perform_inspection(self, panel_region):
        """검사 수행"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'defects': [],
            'quality_score': 0
        }
        
        try:
            # 1. 데드픽셀 감지
            dead_pixels = self.detect_dead_pixels(panel_region)
            results['defects'].extend(dead_pixels)
            
            # 2. 핫픽셀 감지
            hot_pixels = self.detect_hot_pixels(panel_region)
            results['defects'].extend(hot_pixels)
            
            # 3. 색상 균일성 검사
            color_issues = self.check_color_uniformity(panel_region)
            results['defects'].extend(color_issues)
            
            # 4. RGB 채널 분석
            rgb_analysis = self.analyze_rgb_channels(panel_region)
            results['defects'].extend(rgb_analysis)
            
            # 5. 품질 점수 계산
            results['quality_score'] = self.calculate_quality_score(results)
            
        except Exception as e:
            results['defects'].append(f"검사 중 오류: {str(e)}")
        
        return results
    
    def detect_dead_pixels(self, region):
        """데드픽셀 감지 (개선된 알고리즘)"""
        dead_pixels = []
        
        try:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # 1. 적응적 임계값으로 어두운 영역 감지
            dark_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                 cv2.THRESH_BINARY_INV, 11, 2)
            
            # 2. 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((3, 3), np.uint8)
            dark_threshold = cv2.morphologyEx(dark_threshold, cv2.MORPH_OPEN, kernel)
            dark_threshold = cv2.morphologyEx(dark_threshold, cv2.MORPH_CLOSE, kernel)
            
            # 3. 연결된 구성 요소 분석
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(dark_threshold, connectivity=8)
            
            dead_pixel_count = 0
            for i in range(1, num_labels):  # 0은 배경
                area = stats[i, cv2.CC_STAT_AREA]
                if 1 <= area <= 10:  # 작은 영역만 데드픽셀로 간주
                    dead_pixel_count += 1
            
            # 4. 추가 검증: 로컬 평균과의 차이
            kernel = np.ones((5, 5), np.float32) / 25
            local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            diff = np.abs(gray.astype(np.float32) - local_mean)
            additional_dead = np.sum(diff > (0.3 * 255))
            
            total_dead_pixels = dead_pixel_count + (additional_dead // 10)  # 정규화
            
            if total_dead_pixels > 0:
                dead_pixels.append(f"데드픽셀 {total_dead_pixels}개 감지")
                dead_pixels.append(f"  - 연결된 구성요소: {dead_pixel_count}개")
                dead_pixels.append(f"  - 로컬 평균 차이: {additional_dead}개")
            
        except Exception as e:
            dead_pixels.append(f"데드픽셀 감지 오류: {str(e)}")
        
        return dead_pixels
    
    def detect_hot_pixels(self, region):
        """핫픽셀 감지 (개선된 알고리즘)"""
        hot_pixels = []
        
        try:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # 1. 적응적 임계값으로 밝은 영역 감지
            bright_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                                   cv2.THRESH_BINARY, 11, 2)
            
            # 2. 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((3, 3), np.uint8)
            bright_threshold = cv2.morphologyEx(bright_threshold, cv2.MORPH_OPEN, kernel)
            bright_threshold = cv2.morphologyEx(bright_threshold, cv2.MORPH_CLOSE, kernel)
            
            # 3. 연결된 구성 요소 분석
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bright_threshold, connectivity=8)
            
            hot_pixel_count = 0
            for i in range(1, num_labels):  # 0은 배경
                area = stats[i, cv2.CC_STAT_AREA]
                if 1 <= area <= 8:  # 작은 영역만 핫픽셀로 간주
                    hot_pixel_count += 1
            
            # 4. 추가 검증: 로컬 평균과의 차이
            kernel = np.ones((5, 5), np.float32) / 25
            local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            diff = np.abs(gray.astype(np.float32) - local_mean)
            additional_hot = np.sum(diff > (0.4 * 255))
            
            total_hot_pixels = hot_pixel_count + (additional_hot // 15)  # 정규화
            
            if total_hot_pixels > 0:
                hot_pixels.append(f"핫픽셀 {total_hot_pixels}개 감지")
                hot_pixels.append(f"  - 연결된 구성요소: {hot_pixel_count}개")
                hot_pixels.append(f"  - 로컬 평균 차이: {additional_hot}개")
            
        except Exception as e:
            hot_pixels.append(f"핫픽셀 감지 오류: {str(e)}")
        
        return hot_pixels
    
    def check_color_uniformity(self, region):
        """색상 균일성 검사"""
        color_issues = []
        
        try:
            b, g, r = cv2.split(region)
            std_b = np.std(b)
            std_g = np.std(g)
            std_r = np.std(r)
            
            threshold = 30  # 더 엄격한 임계값
            if std_b > threshold or std_g > threshold or std_r > threshold:
                color_issues.append(f"색상 불균일성 감지 (B:{std_b:.1f}, G:{std_g:.1f}, R:{std_r:.1f})")
            
        except Exception as e:
            color_issues.append(f"색상 균일성 검사 오류: {str(e)}")
        
        return color_issues
    
    def analyze_rgb_channels(self, region):
        """RGB 채널 분석"""
        rgb_issues = []
        
        try:
            b, g, r = cv2.split(region)
            
            # 각 채널의 평균값 계산
            mean_b = np.mean(b)
            mean_g = np.mean(g)
            mean_r = np.mean(r)
            
            # 채널 간 균형 확인
            total_mean = (mean_b + mean_g + mean_r) / 3
            b_ratio = mean_b / total_mean if total_mean > 0 else 0
            g_ratio = mean_g / total_mean if total_mean > 0 else 0
            r_ratio = mean_r / total_mean if total_mean > 0 else 0
            
            # 균형이 맞지 않는 경우
            if b_ratio < 0.8 or b_ratio > 1.2:
                rgb_issues.append(f"Blue 채널 불균형: {b_ratio:.2f}")
            if g_ratio < 0.8 or g_ratio > 1.2:
                rgb_issues.append(f"Green 채널 불균형: {g_ratio:.2f}")
            if r_ratio < 0.8 or r_ratio > 1.2:
                rgb_issues.append(f"Red 채널 불균형: {r_ratio:.2f}")
            
        except Exception as e:
            rgb_issues.append(f"RGB 채널 분석 오류: {str(e)}")
        
        return rgb_issues
    
    def calculate_quality_score(self, results):
        """품질 점수 계산 (업계 표준 기준)"""
        score = 100
        
        # 각 결함별 상세 분석
        dead_pixel_count = 0
        hot_pixel_count = 0
        color_uniformity_issues = 0
        rgb_imbalance_issues = 0
        
        for defect in results['defects']:
            if "데드픽셀" in defect and "감지" in defect:
                # 데드픽셀 개수 추출
                try:
                    count_str = defect.split("데드픽셀")[1].split("개")[0].strip()
                    dead_pixel_count = int(count_str)
                except:
                    dead_pixel_count = 1
            elif "핫픽셀" in defect and "감지" in defect:
                # 핫픽셀 개수 추출
                try:
                    count_str = defect.split("핫픽셀")[1].split("개")[0].strip()
                    hot_pixel_count = int(count_str)
                except:
                    hot_pixel_count = 1
            elif "색상 불균일성" in defect:
                color_uniformity_issues += 1
            elif "채널 불균형" in defect:
                rgb_imbalance_issues += 1
            elif "오류" in defect:
                score -= 25
        
        # 데드픽셀 감점 (업계 표준)
        if dead_pixel_count == 0:
            dead_penalty = 0
        elif dead_pixel_count <= 2:
            dead_penalty = dead_pixel_count * 2  # 1-2개: 2점씩
        elif dead_pixel_count <= 5:
            dead_penalty = 4 + (dead_pixel_count - 2) * 3  # 3-5개: 3점씩
        elif dead_pixel_count <= 10:
            dead_penalty = 13 + (dead_pixel_count - 5) * 4  # 6-10개: 4점씩
        else:
            dead_penalty = 33 + (dead_pixel_count - 10) * 5  # 11개 이상: 5점씩
        
        dead_penalty = min(dead_penalty, 50)  # 최대 50점 감점
        
        # 핫픽셀 감점
        if hot_pixel_count == 0:
            hot_penalty = 0
        elif hot_pixel_count <= 3:
            hot_penalty = hot_pixel_count * 1.5  # 1-3개: 1.5점씩
        elif hot_pixel_count <= 5:
            hot_penalty = 4.5 + (hot_pixel_count - 3) * 2  # 4-5개: 2점씩
        else:
            hot_penalty = 8.5 + (hot_pixel_count - 5) * 3  # 6개 이상: 3점씩
        
        hot_penalty = min(hot_penalty, 30)  # 최대 30점 감점
        
        # 색상 균일성 감점
        color_penalty = color_uniformity_issues * 15  # 15점씩
        color_penalty = min(color_penalty, 25)  # 최대 25점 감점
        
        # RGB 채널 불균형 감점
        rgb_penalty = rgb_imbalance_issues * 5  # 5점씩
        rgb_penalty = min(rgb_penalty, 15)  # 최대 15점 감점
        
        # 최종 점수 계산
        final_score = score - dead_penalty - hot_penalty - color_penalty - rgb_penalty
        final_score = max(0, final_score)  # 최소 0점
        
        # 품질 등급 결정
        if final_score >= 90:
            grade = "A급 (우수)"
        elif final_score >= 80:
            grade = "B급 (양호)"
        elif final_score >= 70:
            grade = "C급 (보통)"
        elif final_score >= 60:
            grade = "D급 (불량)"
        else:
            grade = "F급 (심각한 불량)"
        
        # 상세 점수 정보 추가
        results['quality_details'] = {
            'dead_pixel_penalty': dead_penalty,
            'hot_pixel_penalty': hot_penalty,
            'color_uniformity_penalty': color_penalty,
            'rgb_imbalance_penalty': rgb_penalty,
            'grade': grade,
            'dead_pixel_count': dead_pixel_count,
            'hot_pixel_count': hot_pixel_count
        }
        
        return int(final_score)
    
    def update_inspection_results(self, results):
        """검사 결과 업데이트"""
        self.inspection_results = results
        
        # 품질 점수 및 등급 업데이트
        quality_score = results['quality_score']
        if 'quality_details' in results:
            grade = results['quality_details']['grade']
            self.quality_label.configure(text=f"품질 점수: {quality_score}/100 - {grade}")
        else:
            self.quality_label.configure(text=f"품질 점수: {quality_score}/100")
        
        # 결과 텍스트 업데이트
        self.result_text.delete(1.0, tk.END)
        
        result_text = f"검사 시간: {results['timestamp']}\n"
        result_text += f"품질 점수: {quality_score}/100\n"
        
        if 'quality_details' in results:
            details = results['quality_details']
            result_text += f"품질 등급: {details['grade']}\n"
            result_text += f"데드픽셀: {details['dead_pixel_count']}개 (감점: {details['dead_pixel_penalty']:.1f}점)\n"
            result_text += f"핫픽셀: {details['hot_pixel_count']}개 (감점: {details['hot_pixel_penalty']:.1f}점)\n"
            result_text += f"색상 균일성 감점: {details['color_uniformity_penalty']:.1f}점\n"
            result_text += f"RGB 균형 감점: {details['rgb_imbalance_penalty']:.1f}점\n\n"
        
        if results['defects']:
            result_text += "발견된 결함:\n"
            for i, defect in enumerate(results['defects'], 1):
                result_text += f"{i}. {defect}\n"
        else:
            result_text += "결함이 발견되지 않았습니다.\n"
        
        # 품질 기준 안내
        result_text += "\n" + "="*50 + "\n"
        result_text += "품질 기준 안내:\n"
        result_text += "A급 (90-100점): 데드픽셀 0-1개, 핫픽셀 0-1개\n"
        result_text += "B급 (80-89점): 데드픽셀 2-3개, 핫픽셀 2-3개\n"
        result_text += "C급 (70-79점): 데드픽셀 4-5개, 핫픽셀 4-5개\n"
        result_text += "D급 (60-69점): 데드픽셀 6-10개, 핫픽셀 6-10개\n"
        result_text += "F급 (60점 미만): 데드픽셀 11개 이상, 핫픽셀 11개 이상\n"
        
        self.result_text.insert(1.0, result_text)
    
    def save_results(self):
        """결과 저장"""
        if not self.inspection_results:
            messagebox.showwarning("경고", "저장할 결과가 없습니다.")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                title="결과 저장",
                defaultextension=".json",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.inspection_results, f, ensure_ascii=False, indent=2)
                
                self.log_result(f"결과가 저장되었습니다: {file_path}")
                
        except Exception as e:
            messagebox.showerror("오류", f"결과 저장 중 오류: {str(e)}")
    
    def log_result(self, message):
        """결과 로그"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.result_text.insert(tk.END, log_message)
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        """애플리케이션 실행"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """애플리케이션 종료 처리"""
        self.camera_running = False
        self.inspection_running = False
        
        if self.camera:
            self.camera.release()
        
        self.root.destroy()
    
    def apply_lighting_simulation(self, frame, angle, intensity):
        """조명 시뮬레이션 적용 (스크래치 검사용)"""
        if angle == 0:  # 정면 조명
            return frame
        
        h, w = frame.shape[:2]
        
        if angle == 45:  # 45도 측면 조명
            # 좌측에서 오는 조명
            x = np.linspace(0, 1, w)
            y = np.linspace(0, 1, h)
            X, Y = np.meshgrid(x, y)
            lighting = (X * 0.7 + 0.3) * intensity / 255.0
            lighting = np.stack([lighting] * 3, axis=2)
        elif angle == 90:  # 90도 측면 조명
            # 강한 측면 조명
            x = np.linspace(0, 1, w)
            lighting = (x * 0.5 + 0.5) * intensity / 255.0
            lighting = np.stack([lighting] * 3, axis=2)
        else:  # 기타 각도
            # 복합 조명
            x = np.linspace(0, 1, w)
            y = np.linspace(0, 1, h)
            X, Y = np.meshgrid(x, y)
            lighting = (X * 0.6 + Y * 0.4) * intensity / 255.0
            lighting = np.stack([lighting] * 3, axis=2)
        
        # 조명 적용
        enhanced_frame = frame.astype(np.float32) * lighting
        enhanced_frame = np.clip(enhanced_frame, 0, 255).astype(np.uint8)
        
        return enhanced_frame
    
    def detect_scratches(self, frame):
        """스크래치 감지"""
        # 그레이스케일 변환
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 가우시안 블러로 노이즈 제거
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny 엣지 검출
        edges = cv2.Canny(blurred, 50, 150)
        
        # 모폴로지 연산으로 스크래치 강화
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 스크래치 후보 찾기
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        scratches = []
        for contour in contours:
            # 면적과 길이 비율 확인
            area = cv2.contourArea(contour)
            if area < 50:  # 너무 작은 것 제외
                continue
            
            # 길이와 너비 비율 확인 (스크래치는 길쭉함)
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = max(w, h) / min(w, h)
            
            if aspect_ratio > 3:  # 길쭉한 형태
                scratches.append({
                    'contour': contour,
                    'area': area,
                    'bbox': (x, y, w, h),
                    'aspect_ratio': aspect_ratio
                })
        
        return scratches
    
    def analyze_scratch_severity(self, scratches):
        """스크래치 심각도 분석"""
        if not scratches:
            return "스크래치 없음", 100
        
        total_area = sum(scratch['area'] for scratch in scratches)
        max_area = max(scratch['area'] for scratch in scratches)
        count = len(scratches)
        
        # 심각도 판정
        if count == 0:
            severity = "스크래치 없음"
            score = 100
        elif count <= 2 and max_area < 200:
            severity = "경미한 스크래치"
            score = 80
        elif count <= 5 and max_area < 500:
            severity = "보통 스크래치"
            score = 60
        elif count <= 10 and max_area < 1000:
            severity = "심각한 스크래치"
            score = 40
        else:
            severity = "매우 심각한 스크래치"
            score = 20
        
        return severity, score
    
    def draw_scratch_analysis(self, frame, scratches):
        """스크래치 분석 결과 그리기"""
        result_frame = frame.copy()
        
        # 스크래치 그리기
        for i, scratch in enumerate(scratches):
            x, y, w, h = scratch['bbox']
            
            # 스크래치 경계 그리기
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # 스크래치 번호 표시
            cv2.putText(result_frame, f"S{i+1}", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 분석 결과 텍스트
        severity, score = self.analyze_scratch_severity(scratches)
        cv2.putText(result_frame, f"스크래치: {severity}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(result_frame, f"점수: {score}/100", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return result_frame
    
    def start_scratch_inspection(self):
        """스크래치 검사 시작"""
        if not self.camera_running:
            messagebox.showerror("오류", "먼저 카메라를 시작하세요")
            return
        
        # 조명 각도 설정 다이얼로그
        dialog = tk.Toplevel(self.root)
        dialog.title("스크래치 검사 설정")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 조명 각도 설정
        ttk.Label(dialog, text="조명 각도 (0-90도):").pack(pady=10)
        angle_var = tk.IntVar(value=45)
        angle_scale = ttk.Scale(dialog, from_=0, to=90, variable=angle_var, orient=tk.HORIZONTAL)
        angle_scale.pack(fill=tk.X, padx=20, pady=5)
        
        # 조명 강도 설정
        ttk.Label(dialog, text="조명 강도 (0-255):").pack(pady=10)
        intensity_var = tk.IntVar(value=150)
        intensity_scale = ttk.Scale(dialog, from_=0, to=255, variable=intensity_var, orient=tk.HORIZONTAL)
        intensity_scale.pack(fill=tk.X, padx=20, pady=5)
        
        # 확인 버튼
        def start_inspection():
            self.lighting_angle = angle_var.get()
            self.lighting_intensity = intensity_var.get()
            self.scratch_detection_active = True
            dialog.destroy()
            messagebox.showinfo("정보", f"스크래치 검사가 시작되었습니다\n조명 각도: {self.lighting_angle}도\n조명 강도: {self.lighting_intensity}")
        
        ttk.Button(dialog, text="검사 시작", command=start_inspection).pack(pady=20)
        ttk.Button(dialog, text="취소", command=dialog.destroy).pack()
    
    def start_deep_learning_detection(self):
        """딥러닝 탐지 시작"""
        if not self.camera_running:
            messagebox.showerror("오류", "먼저 카메라를 시작하세요")
            return
        
        # 딥러닝 탐지 설정 다이얼로그
        dialog = tk.Toplevel(self.root)
        dialog.title("딥러닝 탐지 설정")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 모델 선택
        ttk.Label(dialog, text="탐지 모델 선택:").pack(pady=10)
        model_var = tk.StringVar(value="U-Net")
        model_combo = ttk.Combobox(dialog, textvariable=model_var, 
                                   values=["U-Net", "YOLO", "Faster R-CNN", "Mask R-CNN"])
        model_combo.pack(fill=tk.X, padx=20, pady=5)
        
        # 신뢰도 임계값
        ttk.Label(dialog, text="신뢰도 임계값 (0.0-1.0):").pack(pady=10)
        confidence_var = tk.DoubleVar(value=0.5)
        confidence_scale = ttk.Scale(dialog, from_=0.0, to=1.0, variable=confidence_var, orient=tk.HORIZONTAL)
        confidence_scale.pack(fill=tk.X, padx=20, pady=5)
        
        # 탐지 모드
        ttk.Label(dialog, text="탐지 모드:").pack(pady=10)
        mode_var = tk.StringVar(value="실시간")
        mode_combo = ttk.Combobox(dialog, textvariable=mode_var, 
                                 values=["실시간", "배치", "단일 이미지"])
        mode_combo.pack(fill=tk.X, padx=20, pady=5)
        
        # 고급 설정
        advanced_frame = ttk.LabelFrame(dialog, text="고급 설정")
        advanced_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # GPU 사용
        gpu_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(advanced_frame, text="GPU 가속 사용", variable=gpu_var).pack(anchor=tk.W, padx=5)
        
        # 모델 경로
        ttk.Label(advanced_frame, text="모델 경로:").pack(anchor=tk.W, padx=5)
        model_path_var = tk.StringVar()
        model_path_frame = ttk.Frame(advanced_frame)
        model_path_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Entry(model_path_frame, textvariable=model_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(model_path_frame, text="찾기", 
                  command=lambda: self.browse_model_path(model_path_var)).pack(side=tk.RIGHT, padx=5)
        
        # 확인 버튼
        def start_detection():
            self.deep_learning_model = model_var.get()
            self.confidence_threshold = confidence_var.get()
            self.detection_mode = mode_var.get()
            self.use_gpu = gpu_var.get()
            self.model_path = model_path_var.get()
            
            dialog.destroy()
            messagebox.showinfo("정보", f"딥러닝 탐지가 시작되었습니다\n모델: {self.deep_learning_model}\n신뢰도: {self.confidence_threshold}")
        
        ttk.Button(dialog, text="탐지 시작", command=start_detection).pack(pady=20)
        ttk.Button(dialog, text="취소", command=dialog.destroy).pack()
    
    def browse_model_path(self, path_var):
        """모델 경로 선택"""
        file_path = filedialog.askopenfilename(
            title="모델 파일 선택",
            filetypes=[("PyTorch files", "*.pth"), ("All files", "*.*")]
        )
        if file_path:
            path_var.set(file_path)
    
    def auto_focus(self):
        """자동초점 기능"""
        if not self.camera_running:
            messagebox.showerror("오류", "먼저 카메라를 시작하세요")
            return
        
        try:
            # 자동초점 설정
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # 자동초점 활성화
            self.camera.set(cv2.CAP_PROP_FOCUS, 0)     # 자동초점 모드
            
            # 초점 조정을 위한 여러 프레임 캡처
            for i in range(10):
                ret, frame = self.camera.read()
                if ret:
                    # 초점 품질 측정
                    focus_quality = self.measure_focus_quality(frame)
                    self.log_result(f"초점 품질: {focus_quality:.2f}")
                    time.sleep(0.1)
            
            # 최종 초점 설정
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # 자동초점 비활성화
            self.log_result("자동초점이 완료되었습니다")
            messagebox.showinfo("성공", "자동초점이 완료되었습니다")
            
        except Exception as e:
            self.log_result(f"자동초점 오류: {str(e)}")
            messagebox.showerror("오류", f"자동초점 실패: {str(e)}")
    
    def measure_focus_quality(self, frame):
        """초점 품질 측정 (Laplacian variance 사용)"""
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Laplacian 필터 적용
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            
            # 분산 계산 (높을수록 선명함)
            focus_quality = laplacian.var()
            
            return focus_quality
            
        except Exception as e:
            self.log_result(f"초점 품질 측정 오류: {str(e)}")
            return 0.0
    
    def continuous_auto_focus(self):
        """연속 자동초점 (백그라운드에서 실행)"""
        if not self.camera_running:
            return
        
        try:
            ret, frame = self.camera.read()
            if ret:
                # 초점 품질 측정
                focus_quality = self.measure_focus_quality(frame)
                
                # 초점 품질이 낮으면 자동 조정
                if focus_quality < 100:  # 임계값
                    self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                    time.sleep(0.1)
                    self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
                
                # 1초 후 다시 체크
                self.root.after(1000, self.continuous_auto_focus)
                
        except Exception as e:
            self.log_result(f"연속 자동초점 오류: {str(e)}")
    
    def start_continuous_auto_focus(self):
        """연속 자동초점 시작"""
        if not self.camera_running:
            messagebox.showerror("오류", "먼저 카메라를 시작하세요")
            return
        
        self.continuous_auto_focus()
        self.log_result("연속 자동초점이 시작되었습니다")
        messagebox.showinfo("정보", "연속 자동초점이 시작되었습니다")
    
    def stop_continuous_auto_focus(self):
        """연속 자동초점 중지"""
        try:
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            self.log_result("연속 자동초점이 중지되었습니다")
        except Exception as e:
            self.log_result(f"연속 자동초점 중지 오류: {str(e)}")

def main():
    """메인 함수"""
    app = TestPatternInspector()
    app.run()

if __name__ == "__main__":
    main()
