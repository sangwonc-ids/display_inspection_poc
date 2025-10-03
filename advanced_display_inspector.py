#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 디스플레이 검사 시스템
Advanced Display Inspection System with Professional UI
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from datetime import datetime
from typing import Tuple, List, Dict, Optional
import threading
import time

class AdvancedDisplayInspector:
    """고급 디스플레이 검사 시스템"""
    
    def __init__(self):
        self.camera = None
        self.current_image = None
        self.reference_image = None
        self.preview_running = False
        self.preview_thread = None
        self.inspection_running = False
        self.inspection_thread = None
        self.display_area = None
        self.test_pattern = None
        self.setup_ui()
        
    def setup_ui(self):
        """고급 UI 설정"""
        self.root = tk.Tk()
        self.root.title("테스트 패턴 생성 및 검사 시스템")
        self.root.geometry("1400x900")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 탭 컨트롤
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 카메라 탭
        self.setup_camera_tab()
        
        # 편광필터 탭
        self.setup_polarizer_tab()
        
        # 테스트 패턴 탭
        self.setup_test_pattern_tab()
        
        # 검사 제어 탭
        self.setup_inspection_tab()
        
    def setup_camera_tab(self):
        """카메라 탭 설정"""
        camera_frame = ttk.Frame(self.notebook)
        self.notebook.add(camera_frame, text="카메라")
        
        # 카메라 설정
        settings_frame = ttk.LabelFrame(camera_frame, text="카메라 설정")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 카메라 선택
        ttk.Label(settings_frame, text="카메라:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.camera_var = tk.StringVar(value="자동 선택")
        self.camera_combo = ttk.Combobox(settings_frame, textvariable=self.camera_var, 
                                       state="readonly", width=20)
        self.camera_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(settings_frame, text="카메라 연결", 
                  command=self.connect_camera).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(settings_frame, text="목록 새로고침", 
                  command=self.refresh_camera_list).grid(row=0, column=3, padx=5, pady=5)
        
        # 카메라 제어
        control_frame = ttk.LabelFrame(camera_frame, text="카메라 제어")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="미리보기 시작", 
                  command=self.start_preview).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(control_frame, text="미리보기 중지", 
                  command=self.stop_preview).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(control_frame, text="자동초점", 
                  command=self.auto_focus).grid(row=0, column=2, padx=5, pady=5)
        
        # 줌 컨트롤
        ttk.Label(control_frame, text="줌:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.zoom_scale = ttk.Scale(control_frame, from_=0.5, to=3.0, 
                                   variable=self.zoom_var, orient=tk.HORIZONTAL,
                                   command=self.on_zoom_change, length=200)
        self.zoom_scale.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        self.zoom_label = ttk.Label(control_frame, text="1.0x")
        self.zoom_label.grid(row=1, column=3, padx=5, pady=5)
        
        # 미리보기 영역
        preview_frame = ttk.LabelFrame(camera_frame, text="카메라 미리보기")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.preview_label = ttk.Label(preview_frame, text="카메라를 연결하고 미리보기를 시작하세요", 
                                      font=("Arial", 12))
        self.preview_label.pack(expand=True)
        
        # 초기 카메라 목록 로드는 UI 완성 후에 실행
        
    def setup_polarizer_tab(self):
        """편광필터 탭 설정"""
        polarizer_frame = ttk.Frame(self.notebook)
        self.notebook.add(polarizer_frame, text="편광필터")
        
        ttk.Label(polarizer_frame, text="편광필터 설정", font=("Arial", 16)).pack(pady=20)
        ttk.Label(polarizer_frame, text="편광필터 기능은 향후 구현 예정입니다.", 
                 font=("Arial", 12)).pack(pady=10)
        
    def setup_test_pattern_tab(self):
        """테스트 패턴 탭 설정"""
        pattern_frame = ttk.Frame(self.notebook)
        self.notebook.add(pattern_frame, text="테스트 패턴")
        
        # 좌우 분할
        left_frame = ttk.Frame(pattern_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        right_frame = ttk.Frame(pattern_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # 왼쪽: 테스트 패턴 생성
        pattern_settings = ttk.LabelFrame(left_frame, text="테스트 패턴 생성")
        pattern_settings.pack(fill=tk.X, pady=(0, 10))
        
        # 크기 설정
        size_frame = ttk.Frame(pattern_settings)
        size_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(size_frame, text="크기 설정:").pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="가로:").pack(side=tk.LEFT, padx=5)
        self.width_var = tk.StringVar(value="1920")
        ttk.Entry(size_frame, textvariable=self.width_var, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(size_frame, text="세로:").pack(side=tk.LEFT, padx=5)
        self.height_var = tk.StringVar(value="1080")
        ttk.Entry(size_frame, textvariable=self.height_var, width=8).pack(side=tk.LEFT, padx=5)
        
        # 인치 설정
        inch_frame = ttk.Frame(pattern_settings)
        inch_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(inch_frame, text="인치 설정:").pack(side=tk.LEFT, padx=5)
        ttk.Label(inch_frame, text="가로:").pack(side=tk.LEFT, padx=5)
        self.width_inch_var = tk.StringVar(value="20.0")
        ttk.Entry(inch_frame, textvariable=self.width_inch_var, width=8).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(inch_frame, text="세로:").pack(side=tk.LEFT, padx=5)
        self.height_inch_var = tk.StringVar(value="11.25")
        ttk.Entry(inch_frame, textvariable=self.height_inch_var, width=8).pack(side=tk.LEFT, padx=5)
        
        # DPI 표시
        dpi_frame = ttk.Frame(pattern_settings)
        dpi_frame.pack(fill=tk.X, pady=5)
        ttk.Label(dpi_frame, text="DPI: 96").pack(side=tk.LEFT, padx=5)
        
        # 비율 설정
        ratio_frame = ttk.Frame(pattern_settings)
        ratio_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(ratio_frame, text="비율 설정:").pack(side=tk.LEFT, padx=5)
        self.ratio_var = tk.StringVar(value="16:9")
        ratio_combo = ttk.Combobox(ratio_frame, textvariable=self.ratio_var,
                                 values=["16:9", "4:3", "21:9", "1:1"], width=8)
        ratio_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(ratio_frame, text="비율 적용", 
                  command=self.apply_ratio).pack(side=tk.LEFT, padx=5)
        
        # 색상 선택
        color_frame = ttk.Frame(pattern_settings)
        color_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(color_frame, text="색상:").pack(side=tk.LEFT, padx=5)
        self.color_var = tk.StringVar(value="R")
        ttk.Radiobutton(color_frame, text="R", variable=self.color_var, value="R").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="G", variable=self.color_var, value="G").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="B", variable=self.color_var, value="B").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(color_frame, text="W", variable=self.color_var, value="W").pack(side=tk.LEFT, padx=5)
        
        # 불량 시뮬레이션
        defect_frame = ttk.Frame(pattern_settings)
        defect_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(defect_frame, text="불량 시뮬레이션:").pack(side=tk.LEFT, padx=5)
        self.dead_pixel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(defect_frame, text="데드픽셀", variable=self.dead_pixel_var).pack(side=tk.LEFT, padx=5)
        
        self.hot_pixel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(defect_frame, text="핫픽셀", variable=self.hot_pixel_var).pack(side=tk.LEFT, padx=5)
        
        self.scratch_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(defect_frame, text="스크래치", variable=self.scratch_var).pack(side=tk.LEFT, padx=5)
        
        # 생성 버튼
        ttk.Button(pattern_settings, text="패턴 생성", 
                  command=self.generate_test_pattern).pack(pady=10)
        
        # 오른쪽: 패턴 미리보기
        preview_frame = ttk.LabelFrame(right_frame, text="패턴 미리보기")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pattern_label = ttk.Label(preview_frame, text="패턴을 생성하세요", 
                                      font=("Arial", 12))
        self.pattern_label.pack(expand=True)
        
    def setup_inspection_tab(self):
        """검사 제어 탭 설정"""
        inspection_frame = ttk.Frame(self.notebook)
        self.notebook.add(inspection_frame, text="검사 제어")
        
        # 좌우 분할
        left_frame = ttk.Frame(inspection_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        right_frame = ttk.Frame(inspection_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # 왼쪽: 검사 제어
        control_frame = ttk.LabelFrame(left_frame, text="검사 제어")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 검사 버튼들
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="패널 감지", 
                  command=self.detect_panel).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="검사 시작", 
                  command=self.start_inspection).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="검사 중지", 
                  command=self.stop_inspection).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="결과 저장", 
                  command=self.save_results).pack(side=tk.LEFT, padx=5)
        
        # 검사 모드 선택
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="검사 모드:").pack(side=tk.LEFT, padx=5)
        self.inspection_mode = tk.StringVar(value="전체 검사")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.inspection_mode,
                                 values=["전체 검사", "스크래치 검사", "불량화소 검사", "색상 균일성 검사"],
                                 state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT, padx=5)
        
        # 오른쪽: 카메라 뷰 및 결과
        camera_view_frame = ttk.LabelFrame(right_frame, text="카메라 뷰 (검사 대상)")
        camera_view_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.camera_view_label = ttk.Label(camera_view_frame, text="카메라를 연결하고 검사를 시작하세요", 
                                          font=("Arial", 12))
        self.camera_view_label.pack(expand=True)
        
        # 검사 결과
        result_frame = ttk.LabelFrame(right_frame, text="검사 결과")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 품질 기준 안내
        quality_frame = ttk.LabelFrame(result_frame, text="품질 기준 안내")
        quality_frame.pack(fill=tk.X, pady=5)
        
        quality_text = """A급 (90-100점): 데드픽셀 0-1개, 핫픽셀 0-1개
B급 (80-89점): 데드픽셀 2-3개, 핫픽셀 2-3개
C급 (70-79점): 데드픽셀 4-5개, 핫픽셀 4-5개
D급 (60-69점): 데드픽셀 6-10개, 핫픽셀 6-10개
F급 (60점 미만): 데드픽셀 11개 이상, 핫픽셀 11개 이상"""
        
        ttk.Label(quality_frame, text=quality_text, font=("Arial", 9)).pack(pady=5)
        
        # 결과 로그
        log_frame = ttk.LabelFrame(result_frame, text="검사 로그")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=8)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 초기 로그 메시지
        self.log_result("시스템이 준비되었습니다.")
        
        # 초기 카메라 목록 로드
        self.refresh_camera_list()
        
    def refresh_camera_list(self):
        """카메라 목록 새로고침"""
        camera_list = ["자동 선택"]
        
        for i in range(10):
            test_camera = cv2.VideoCapture(i)
            if test_camera.isOpened():
                ret, frame = test_camera.read()
                if ret and frame is not None:
                    width = int(test_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(test_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(test_camera.get(cv2.CAP_PROP_FPS))
                    
                    camera_info = f"카메라 {i} ({width}x{height} @ {fps}fps)"
                    camera_list.append(camera_info)
                test_camera.release()
            else:
                test_camera.release()
        
        self.camera_combo['values'] = camera_list
        self.log_result(f"사용 가능한 카메라: {len(camera_list)-1}개 발견")
        
    def connect_camera(self):
        """카메라 연결"""
        try:
            selected_camera = self.camera_var.get()
            self.camera = None
            camera_index = 0
            
            if selected_camera == "자동 선택":
                for i in range(10):
                    test_camera = cv2.VideoCapture(i)
                    if test_camera.isOpened():
                        ret, frame = test_camera.read()
                        if ret and frame is not None:
                            self.camera = test_camera
                            camera_index = i
                            break
                        else:
                            test_camera.release()
                    else:
                        test_camera.release()
            else:
                try:
                    camera_index = int(selected_camera.split()[1])
                    self.camera = cv2.VideoCapture(camera_index)
                    if self.camera.isOpened():
                        ret, frame = self.camera.read()
                        if not ret or frame is None:
                            self.camera.release()
                            self.camera = None
                except (ValueError, IndexError):
                    self.log_result("잘못된 카메라 선택")
                    return
            
            if self.camera is not None and self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                
                actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                actual_fps = int(self.camera.get(cv2.CAP_PROP_FPS))
                
                self.log_result("카메라가 성공적으로 연결되었습니다.")
                self.log_result(f"카메라 인덱스: {camera_index}")
                self.log_result(f"해상도: {actual_width}x{actual_height}")
                self.log_result(f"FPS: {actual_fps}")
            else:
                messagebox.showerror("오류", "카메라 연결에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"카메라 연결 중 오류 발생: {str(e)}")
    
    def start_preview(self):
        """미리보기 시작"""
        if self.camera is None or not self.camera.isOpened():
            messagebox.showerror("오류", "먼저 카메라를 연결해주세요.")
            return
        
        if self.preview_running:
            self.log_result("미리보기가 이미 실행 중입니다.")
            return
        
        self.preview_running = True
        self.preview_thread = threading.Thread(target=self.preview_loop, daemon=True)
        self.preview_thread.start()
        self.log_result("미리보기 시작됨")
    
    def stop_preview(self):
        """미리보기 중지"""
        self.preview_running = False
        if self.preview_thread:
            self.preview_thread.join(timeout=1)
        self.preview_label.configure(image="", text="미리보기가 중지되었습니다")
        self.log_result("미리보기 중지됨")
    
    def preview_loop(self):
        """미리보기 루프"""
        while self.preview_running and self.camera is not None:
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    # 프레임 크기 조정
                    height, width = frame.shape[:2]
                    max_width = 640
                    max_height = 480
                    
                    if width > max_width or height > max_height:
                        scale = min(max_width/width, max_height/height)
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                    
                    # BGR을 RGB로 변환
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # PIL 이미지로 변환
                    image = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(image)
                    
                    # UI 스레드에서 라벨 업데이트
                    self.root.after(0, self.update_preview, photo)
                    
                time.sleep(0.033)  # 약 30 FPS
            except Exception as e:
                self.log_result(f"미리보기 오류: {str(e)}")
                break
        
        self.preview_running = False
    
    def update_preview(self, photo):
        """미리보기 이미지 업데이트"""
        if self.preview_running:
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo
    
    def auto_focus(self):
        """자동초점"""
        if self.camera is None or not self.camera.isOpened():
            messagebox.showerror("오류", "먼저 카메라를 연결해주세요.")
            return
        
        try:
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.camera.set(cv2.CAP_PROP_FOCUS, -1)
            
            for i in range(10):
                ret, frame = self.camera.read()
                if ret:
                    time.sleep(0.1)
            
            self.log_result("자동초점 완료")
        except Exception as e:
            self.log_result(f"자동초점 실패: {str(e)}")
    
    def on_zoom_change(self, value):
        """줌 변경"""
        self.zoom_factor = float(value)
        self.zoom_label.configure(text=f"{self.zoom_factor:.1f}x")
        self.log_result(f"줌 레벨: {self.zoom_factor:.1f}x")
    
    def apply_ratio(self):
        """비율 적용"""
        try:
            ratio = self.ratio_var.get()
            if ratio == "16:9":
                self.height_var.set(str(int(int(self.width_var.get()) * 9 / 16)))
            elif ratio == "4:3":
                self.height_var.set(str(int(int(self.width_var.get()) * 3 / 4)))
            elif ratio == "21:9":
                self.height_var.set(str(int(int(self.width_var.get()) * 9 / 21)))
            elif ratio == "1:1":
                self.height_var.set(self.width_var.get())
            
            self.log_result(f"비율 {ratio} 적용됨")
        except Exception as e:
            self.log_result(f"비율 적용 실패: {str(e)}")
    
    def generate_test_pattern(self):
        """테스트 패턴 생성"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            color = self.color_var.get()
            
            # 기본 색상 설정
            if color == "R":
                base_color = (0, 0, 255)  # 빨간색 (BGR)
            elif color == "G":
                base_color = (0, 255, 0)  # 녹색
            elif color == "B":
                base_color = (255, 0, 0)  # 파란색
            else:  # W
                base_color = (255, 255, 255)  # 흰색
            
            # 기본 패턴 생성
            pattern = np.full((height, width, 3), base_color, dtype=np.uint8)
            
            # 데드 픽셀 시뮬레이션
            if self.dead_pixel_var.get():
                for i in range(10):
                    x = np.random.randint(50, width-50)
                    y = np.random.randint(50, height-50)
                    cv2.circle(pattern, (x, y), 2, (0, 0, 0), -1)
            
            # 핫 픽셀 시뮬레이션
            if self.hot_pixel_var.get():
                for i in range(5):
                    x = np.random.randint(50, width-50)
                    y = np.random.randint(50, height-50)
                    cv2.circle(pattern, (x, y), 3, (255, 255, 255), -1)
            
            # 스크래치 시뮬레이션
            if self.scratch_var.get():
                for i in range(3):
                    start_x = np.random.randint(0, width)
                    start_y = np.random.randint(0, height)
                    end_x = np.random.randint(0, width)
                    end_y = np.random.randint(0, height)
                    cv2.line(pattern, (start_x, start_y), (end_x, end_y), (0, 0, 0), 2)
            
            # 색상 불균일성 시뮬레이션
            for i in range(3):
                x = np.random.randint(0, width-200)
                y = np.random.randint(0, height-200)
                if color == "R":
                    defect_color = (0, 0, 200)
                elif color == "G":
                    defect_color = (0, 200, 0)
                elif color == "B":
                    defect_color = (200, 0, 0)
                else:
                    defect_color = (200, 200, 200)
                
                cv2.rectangle(pattern, (x, y), (x+100, y+100), defect_color, -1)
            
            # 패턴 저장
            self.test_pattern = pattern
            cv2.imwrite("test_pattern.png", pattern)
            
            # 미리보기 업데이트
            self.update_pattern_preview(pattern)
            
            self.log_result(f"테스트 패턴 생성 완료: {width}x{height}, 색상: {color}")
            self.log_result("패턴 저장: test_pattern.png")
            
        except Exception as e:
            self.log_result(f"패턴 생성 실패: {str(e)}")
    
    def update_pattern_preview(self, pattern):
        """패턴 미리보기 업데이트"""
        try:
            # 패턴 크기 조정
            height, width = pattern.shape[:2]
            max_width = 400
            max_height = 300
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                pattern = cv2.resize(pattern, (new_width, new_height))
            
            # BGR을 RGB로 변환
            pattern_rgb = cv2.cvtColor(pattern, cv2.COLOR_BGR2RGB)
            
            # PIL 이미지로 변환
            image = Image.fromarray(pattern_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # 패턴 라벨 업데이트
            self.pattern_label.configure(image=photo, text="")
            self.pattern_label.image = photo
            
        except Exception as e:
            self.log_result(f"패턴 미리보기 업데이트 오류: {str(e)}")
    
    def detect_panel(self):
        """패널 감지"""
        if self.camera is None or not self.camera.isOpened():
            messagebox.showerror("오류", "먼저 카메라를 연결해주세요.")
            return
        
        try:
            ret, frame = self.camera.read()
            if ret and frame is not None:
                # 디스플레이 영역 감지
                display_roi = self.auto_detect_display_area(frame)
                
                if display_roi is not None:
                    x, y, w, h = display_roi
                    
                    # 감지된 영역 표시
                    result_frame = frame.copy()
                    cv2.rectangle(result_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.putText(result_frame, "Panel 06, 1114215", (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # 카메라 뷰 업데이트
                    self.update_camera_view(result_frame)
                    
                    self.log_result(f"패널 감지 완료: ({x}, {y}, {w}, {h})")
                else:
                    self.log_result("패널을 감지할 수 없습니다.")
            else:
                self.log_result("카메라에서 프레임을 읽을 수 없습니다.")
                
        except Exception as e:
            self.log_result(f"패널 감지 실패: {str(e)}")
    
    def auto_detect_display_area(self, frame):
        """디스플레이 영역 자동 감지"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                if area > 10000:
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    return (x, y, w, h)
            
            return None
            
        except Exception as e:
            self.log_result(f"디스플레이 감지 오류: {str(e)}")
            return None
    
    def update_camera_view(self, frame):
        """카메라 뷰 업데이트"""
        try:
            # 프레임 크기 조정
            height, width = frame.shape[:2]
            max_width = 600
            max_height = 400
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # BGR을 RGB로 변환
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # PIL 이미지로 변환
            image = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image)
            
            # 카메라 뷰 라벨 업데이트
            self.camera_view_label.configure(image=photo, text="")
            self.camera_view_label.image = photo
            
        except Exception as e:
            self.log_result(f"카메라 뷰 업데이트 오류: {str(e)}")
    
    def start_inspection(self):
        """검사 시작"""
        if self.camera is None or not self.camera.isOpened():
            messagebox.showerror("오류", "먼저 카메라를 연결해주세요.")
            return
        
        if self.inspection_running:
            self.log_result("검사가 이미 실행 중입니다.")
            return
        
        self.inspection_running = True
        self.inspection_thread = threading.Thread(target=self.inspection_loop, daemon=True)
        self.inspection_thread.start()
        self.log_result("검사가 시작되었습니다.")
    
    def stop_inspection(self):
        """검사 중지"""
        self.inspection_running = False
        if self.inspection_thread:
            self.inspection_thread.join(timeout=1)
        self.log_result("검사가 중지되었습니다.")
    
    def inspection_loop(self):
        """검사 루프"""
        frame_count = 0
        last_log_time = 0
        
        while self.inspection_running and self.camera is not None:
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    frame_count += 1
                    
                    # 매 프레임마다 디스플레이 영역 감지 시도
                    display_roi = self.auto_detect_display_area(frame)
                    
                    if display_roi is not None:
                        x, y, w, h = display_roi
                        
                        # 디스플레이 영역 표시 (항상 표시)
                        result_frame = frame.copy()
                        cv2.rectangle(result_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                        cv2.putText(result_frame, "Panel 06, 1114215", (x, y-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # 5프레임마다 상세 검사 실행
                        if frame_count % 5 == 0:
                            roi_image = frame[y:y+h, x:x+w]
                            
                            # 검사 실행
                            results = self.quick_inspection(roi_image)
                            
                            # 검사 결과를 프레임에 표시
                            if results:
                                result_text = f"Scratches: {results.get('scratches', 0)} | "
                                result_text += f"Defects: {results.get('defects', 0)} | "
                                result_text += f"Uniformity: {results.get('uniformity', 0):.2f}"
                                
                                cv2.putText(result_frame, result_text, (x, y+h+25), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                                
                                # 배경 박스
                                text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                                cv2.rectangle(result_frame, (x, y+h+5), (x+text_size[0]+10, y+h+30), (0, 0, 0), -1)
                                cv2.putText(result_frame, result_text, (x+5, y+h+20), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                                
                                # 로그 출력 (3초마다)
                                current_time = time.time()
                                if current_time - last_log_time > 3:
                                    self.log_result(f"검사 결과 - 스크래치: {results.get('scratches', 0)}개, "
                                                  f"불량화소: {results.get('defects', 0)}개, "
                                                  f"균일성: {results.get('uniformity', 0):.2f}")
                                    last_log_time = current_time
                            
                            # 카메라 뷰 업데이트
                            self.update_camera_view(result_frame)
                        else:
                            # 검사 없이 디스플레이 영역만 표시
                            self.update_camera_view(result_frame)
                    else:
                        # 디스플레이 영역이 감지되지 않을 때 상태 표시
                        status_frame = frame.copy()
                        cv2.putText(status_frame, "Display Area Not Detected", (50, 50), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        cv2.putText(status_frame, "Please position camera to capture display", (50, 100), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                        self.update_camera_view(status_frame)
                        
                        # 5초마다 상태 로그
                        if frame_count % 50 == 0:
                            self.log_result("디스플레이 영역을 감지할 수 없습니다. 카메라 위치를 조정해주세요.")
                    
                    time.sleep(0.1)  # 10 FPS
                    
            except Exception as e:
                self.log_result(f"검사 오류: {str(e)}")
                break
        
        self.inspection_running = False
    
    def quick_inspection(self, roi_image):
        """빠른 검사 실행"""
        try:
            from advanced_analysis import AdvancedDisplayAnalyzer
            analyzer = AdvancedDisplayAnalyzer()
            
            results = {}
            
            # 스크래치 검사
            scratches = analyzer.detect_scratches(roi_image)
            results['scratches'] = scratches['count']
            
            # 불량화소 검사
            dead_pixels = analyzer.detect_dead_pixels(roi_image)
            bright_spots = analyzer.detect_bright_spots(roi_image)
            results['defects'] = dead_pixels['count'] + bright_spots['count']
            
            # 색상 균일성
            color_uniformity = analyzer.analyze_color_uniformity(roi_image)
            results['uniformity'] = color_uniformity['uniformity_score']
            
            return results
            
        except Exception as e:
            self.log_result(f"빠른 검사 오류: {str(e)}")
            return {}
    
    def draw_inspection_results(self, frame, display_roi, results):
        """검사 결과를 프레임에 그리기"""
        try:
            x, y, w, h = display_roi
            
            # 디스플레이 영역 표시
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Panel 06, 1114215", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 검사 결과 표시
            if results:
                result_text = f"Scratches: {results.get('scratches', 0)} | "
                result_text += f"Defects: {results.get('defects', 0)} | "
                result_text += f"Uniformity: {results.get('uniformity', 0):.2f}"
                
                cv2.putText(frame, result_text, (x, y+h+25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # 배경 박스
                text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(frame, (x, y+h+5), (x+text_size[0]+10, y+h+30), (0, 0, 0), -1)
                cv2.putText(frame, result_text, (x+5, y+h+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
        except Exception as e:
            self.log_result(f"결과 그리기 오류: {str(e)}")
    
    def save_results(self):
        """결과 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inspection_result_{timestamp}.json"
            
            # 검사 결과 수집
            from advanced_analysis import AdvancedDisplayAnalyzer
            analyzer = AdvancedDisplayAnalyzer()
            
            if self.current_image is not None:
                report = analyzer.create_analysis_report(self.current_image)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                
                self.log_result(f"검사 결과 저장: {filename}")
            else:
                self.log_result("저장할 검사 결과가 없습니다.")
            
        except Exception as e:
            self.log_result(f"결과 저장 실패: {str(e)}")
    
    def log_result(self, message):
        """결과 로그"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # log_text가 초기화되었는지 확인
        if hasattr(self, 'log_text') and self.log_text is not None:
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        else:
            # log_text가 없으면 콘솔에 출력
            print(log_message.strip())
    
    def run(self):
        """앱 실행"""
        try:
            self.root.mainloop()
        finally:
            # 앱 종료 시 정리
            self.stop_preview()
            self.stop_inspection()
            if self.camera is not None:
                self.camera.release()

def main():
    """메인 함수"""
    app = AdvancedDisplayInspector()
    app.run()

if __name__ == "__main__":
    main()
