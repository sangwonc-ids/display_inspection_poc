#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
디스플레이 화면 스크래치 확인 및 RGB 픽셀 검사 시스템
Display Screen Scratch Detection and RGB Pixel Analysis System
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

class DisplayInspector:
    """디스플레이 검사 시스템 메인 클래스"""
    
    def __init__(self):
        self.camera = None
        self.current_image = None
        self.reference_image = None
        self.scratch_results = []
        self.rgb_results = {}
        self.preview_running = False
        self.preview_thread = None
        self.zoom_factor = 1.0
        self.focus_position = 0
        self.realtime_inspection = False
        self.inspection_thread = None
        self.display_area = None
        self.setup_ui()
        
    def setup_ui(self):
        """사용자 인터페이스 설정"""
        self.root = tk.Tk()
        self.root.title("디스플레이 검사 시스템")
        self.root.geometry("1200x800")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 미리보기 창 (오른쪽)
        preview_frame = ttk.LabelFrame(main_frame, text="카메라 미리보기")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 미리보기 라벨
        self.preview_label = ttk.Label(preview_frame, text="카메라를 연결하고 미리보기를 시작하세요", 
                                      font=("Arial", 12))
        self.preview_label.pack(expand=True)
        
        # 제어 패널 - 여러 행으로 분할
        control_frame = ttk.LabelFrame(main_frame, text="제어 패널")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 첫 번째 행: 카메라 연결
        camera_row = ttk.Frame(control_frame)
        camera_row.pack(fill=tk.X, pady=5)
        
        # 두 번째 행: 미리보기 및 카메라 제어
        preview_row = ttk.Frame(control_frame)
        preview_row.pack(fill=tk.X, pady=5)
        
        # 세 번째 행: 테스트 및 검사
        test_row = ttk.Frame(control_frame)
        test_row.pack(fill=tk.X, pady=5)
        
        # 첫 번째 행: 카메라 연결
        ttk.Label(camera_row, text="카메라:").pack(side=tk.LEFT, padx=5)
        self.camera_var = tk.StringVar(value="자동 선택")
        self.camera_combo = ttk.Combobox(camera_row, textvariable=self.camera_var, 
                                       state="readonly", width=15)
        self.camera_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(camera_row, text="카메라 연결", 
                  command=self.connect_camera).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(camera_row, text="목록 새로고침", 
                  command=self.refresh_camera_list).pack(side=tk.LEFT, padx=5)
        
        # 두 번째 행: 미리보기 및 카메라 제어
        ttk.Label(preview_row, text="미리보기:").pack(side=tk.LEFT, padx=5)
        ttk.Button(preview_row, text="시작", 
                  command=self.start_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(preview_row, text="중지", 
                  command=self.stop_preview).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(preview_row, text="카메라:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(preview_row, text="자동초점", 
                  command=self.auto_focus).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(preview_row, text="줌:").pack(side=tk.LEFT, padx=(10, 5))
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.zoom_scale = ttk.Scale(preview_row, from_=0.5, to=3.0, 
                                   variable=self.zoom_var, orient=tk.HORIZONTAL,
                                   command=self.on_zoom_change, length=80)
        self.zoom_scale.pack(side=tk.LEFT, padx=5)
        
        self.zoom_label = ttk.Label(preview_row, text="1.0x")
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        # 세 번째 행: 테스트 및 검사
        ttk.Label(test_row, text="이미지:").pack(side=tk.LEFT, padx=5)
        ttk.Button(test_row, text="캡처", 
                  command=self.capture_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_row, text="파일 로드", 
                  command=self.load_from_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(test_row, text="테스트:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(test_row, text="패턴 생성", 
                  command=self.create_test_pattern).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_row, text="실시간 검사", 
                  command=self.start_realtime_inspection).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_row, text="검사 중지", 
                  command=self.stop_realtime_inspection).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(test_row, text="검사:").pack(side=tk.LEFT, padx=(20, 5))
        self.inspection_mode = tk.StringVar(value="전체 검사")
        mode_combo = ttk.Combobox(test_row, textvariable=self.inspection_mode,
                                 values=["전체 검사", "스크래치 검사", "불량화소 검사", "색상 균일성 검사"],
                                 state="readonly", width=12)
        mode_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(test_row, text="검사 실행", 
                  command=self.run_inspection).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_row, text="결과 저장", 
                  command=self.save_results).pack(side=tk.LEFT, padx=5)
        
        # 이미지 표시 영역
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # 원본 이미지
        self.original_label = ttk.Label(image_frame, text="원본 이미지")
        self.original_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 분석 결과 이미지
        self.result_label = ttk.Label(image_frame, text="분석 결과")
        self.result_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 결과 텍스트 영역
        result_frame = ttk.LabelFrame(main_frame, text="검사 결과")
        result_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.result_text = tk.Text(result_frame, height=8)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 초기 카메라 목록 로드
        self.refresh_camera_list()
    
    def refresh_camera_list(self):
        """사용 가능한 카메라 목록 새로고침"""
        camera_list = ["자동 선택"]
        usb_cameras = []
        builtin_cameras = []
        
        for i in range(10):  # 0-9번 카메라 확인
            test_camera = cv2.VideoCapture(i)
            if test_camera.isOpened():
                ret, frame = test_camera.read()
                if ret and frame is not None:
                    # 카메라 정보 수집
                    width = int(test_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(test_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(test_camera.get(cv2.CAP_PROP_FPS))
                    
                    # 카메라 타입 추정 (해상도와 FPS 기반)
                    if width >= 1920 and height >= 1080:
                        camera_type = "USB 카메라"
                        camera_info = f"카메라 {i} - {camera_type} ({width}x{height} @ {fps}fps)"
                        usb_cameras.append(camera_info)
                    else:
                        camera_type = "내장 카메라"
                        camera_info = f"카메라 {i} - {camera_type} ({width}x{height} @ {fps}fps)"
                        builtin_cameras.append(camera_info)
                test_camera.release()
            else:
                test_camera.release()
        
        # USB 카메라를 먼저, 내장 카메라를 나중에 표시
        camera_list.extend(usb_cameras)
        camera_list.extend(builtin_cameras)
        
        self.camera_combo['values'] = camera_list
        self.log_result(f"사용 가능한 카메라: {len(usb_cameras)}개 USB, {len(builtin_cameras)}개 내장")
        
        # USB 카메라가 있으면 자동으로 첫 번째 USB 카메라 선택
        if usb_cameras:
            self.camera_var.set(usb_cameras[0])
            self.log_result("USB 카메라가 자동으로 선택되었습니다.")
        
    def connect_camera(self):
        """카메라 연결"""
        try:
            selected_camera = self.camera_var.get()
            self.camera = None
            camera_index = 0
            
            if selected_camera == "자동 선택":
                # 자동 선택: USB 카메라 우선, 그 다음 내장 카메라
                usb_found = False
                
                # 먼저 USB 카메라 찾기 (고해상도)
                for i in range(10):
                    test_camera = cv2.VideoCapture(i)
                    if test_camera.isOpened():
                        ret, frame = test_camera.read()
                        if ret and frame is not None:
                            width = int(test_camera.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(test_camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            if width >= 1920 and height >= 1080:  # USB 카메라로 추정
                                self.camera = test_camera
                                camera_index = i
                                self.log_result(f"자동 선택: USB 카메라 {i}번 연결 ({width}x{height})")
                                usb_found = True
                                break
                        test_camera.release()
                    else:
                        test_camera.release()
                
                # USB 카메라가 없으면 내장 카메라 사용
                if not usb_found:
                    for i in range(10):
                        test_camera = cv2.VideoCapture(i)
                        if test_camera.isOpened():
                            ret, frame = test_camera.read()
                            if ret and frame is not None:
                                self.camera = test_camera
                                camera_index = i
                                self.log_result(f"자동 선택: 내장 카메라 {i}번 연결")
                                break
                            else:
                                test_camera.release()
                        else:
                            test_camera.release()
            else:
                # 특정 카메라 선택
                # "카메라 0 (1920x1080 @ 30fps)" 형식에서 숫자 추출
                try:
                    camera_index = int(selected_camera.split()[1])
                    self.camera = cv2.VideoCapture(camera_index)
                    if self.camera.isOpened():
                        ret, frame = self.camera.read()
                        if ret and frame is not None:
                            self.log_result(f"선택된 카메라 {camera_index}번 연결 성공")
                        else:
                            self.camera.release()
                            self.camera = None
                            self.log_result(f"카메라 {camera_index}번 연결 실패 (프레임 읽기 불가)")
                    else:
                        self.camera = None
                        self.log_result(f"카메라 {camera_index}번 연결 실패")
                except (ValueError, IndexError):
                    self.log_result("잘못된 카메라 선택")
                    return
            
            if self.camera is not None and self.camera.isOpened():
                # 안전한 해상도로 설정
                try:
                    self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                    self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                    self.camera.set(cv2.CAP_PROP_FPS, 30)
                except:
                    # 기본 해상도 사용
                    pass
                
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
                    # 프레임 크기 조정 (미리보기용)
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
            self.preview_label.image = photo  # 참조 유지
    
    def auto_focus(self):
        """자동초점 기능"""
        if self.camera is None or not self.camera.isOpened():
            messagebox.showerror("오류", "먼저 카메라를 연결해주세요.")
            return
        
        try:
            # OpenCV의 자동초점 기능 사용
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.camera.set(cv2.CAP_PROP_FOCUS, -1)  # 자동초점 활성화
            
            # 초점 조정을 위한 여러 프레임 캡처
            for i in range(10):
                ret, frame = self.camera.read()
                if ret:
                    time.sleep(0.1)
            
            self.log_result("자동초점 완료")
            
        except Exception as e:
            self.log_result(f"자동초점 실패: {str(e)}")
    
    def on_zoom_change(self, value):
        """줌 변경 처리"""
        self.zoom_factor = float(value)
        self.zoom_label.configure(text=f"{self.zoom_factor:.1f}x")
        self.log_result(f"줌 레벨: {self.zoom_factor:.1f}x")
    
    def run_inspection(self):
        """검사 실행"""
        if self.current_image is None:
            messagebox.showerror("오류", "먼저 이미지를 캡처하거나 로드해주세요.")
            return
        
        mode = self.inspection_mode.get()
        self.log_result(f"{mode} 시작...")
        
        try:
            if mode == "전체 검사":
                self.run_full_inspection()
            elif mode == "스크래치 검사":
                self.run_scratch_inspection()
            elif mode == "불량화소 검사":
                self.run_pixel_inspection()
            elif mode == "색상 균일성 검사":
                self.run_color_inspection()
            
            self.log_result(f"{mode} 완료")
            
        except Exception as e:
            self.log_result(f"검사 실패: {str(e)}")
    
    def run_full_inspection(self):
        """전체 검사 실행"""
        from advanced_analysis import AdvancedDisplayAnalyzer
        
        analyzer = AdvancedDisplayAnalyzer()
        report = analyzer.create_analysis_report(self.current_image)
        
        # 결과 표시
        self.log_result(f"=== 전체 검사 결과 ===")
        self.log_result(f"품질 점수: {report['overall_quality_score']:.1f}/100")
        self.log_result(f"데드 픽셀: {report['dead_pixels']['count']}개")
        self.log_result(f"핫 픽셀: {report['bright_spots']['count']}개")
        self.log_result(f"무라 결함: {report['mura_defects']['count']}개")
        self.log_result(f"색상 균일성: {report['color_uniformity']['uniformity_score']:.2f}")
        
        # 결과 시각화
        analyzer.visualize_results(self.current_image, report, "inspection_result.png")
        self.log_result("결과 이미지 저장: inspection_result.png")
    
    def run_scratch_inspection(self):
        """스크래치 검사 실행"""
        from advanced_analysis import AdvancedDisplayAnalyzer
        
        analyzer = AdvancedDisplayAnalyzer()
        scratches = analyzer.detect_scratches(self.current_image)
        
        self.log_result(f"=== 스크래치 검사 결과 ===")
        self.log_result(f"감지된 스크래치: {scratches['count']}개")
        
        for i, scratch in enumerate(scratches['scratches']):
            self.log_result(f"스크래치 {i+1}: 길이 {scratch['length']:.1f}px, 각도 {scratch['angle']:.1f}°")
    
    def run_pixel_inspection(self):
        """불량화소 검사 실행"""
        from advanced_analysis import AdvancedDisplayAnalyzer
        
        analyzer = AdvancedDisplayAnalyzer()
        
        # 데드 픽셀 검사
        dead_pixels = analyzer.detect_dead_pixels(self.current_image)
        self.log_result(f"=== 불량화소 검사 결과 ===")
        self.log_result(f"데드 픽셀: {dead_pixels['count']}개")
        
        # 핫 픽셀 검사
        bright_spots = analyzer.detect_bright_spots(self.current_image)
        self.log_result(f"핫 픽셀: {bright_spots['count']}개")
        
        # 무라 결함 검사
        mura_defects = analyzer.detect_mura_defects(self.current_image)
        self.log_result(f"무라 결함: {mura_defects['count']}개")
    
    def run_color_inspection(self):
        """색상 균일성 검사 실행"""
        from advanced_analysis import AdvancedDisplayAnalyzer
        
        analyzer = AdvancedDisplayAnalyzer()
        color_uniformity = analyzer.analyze_color_uniformity(self.current_image)
        
        self.log_result(f"=== 색상 균일성 검사 결과 ===")
        self.log_result(f"균일성 점수: {color_uniformity['uniformity_score']:.2f}")
        self.log_result(f"R 채널 편차: {color_uniformity['r_std']:.2f}")
        self.log_result(f"G 채널 편차: {color_uniformity['g_std']:.2f}")
        self.log_result(f"B 채널 편차: {color_uniformity['b_std']:.2f}")
    
    def save_results(self):
        """검사 결과 저장"""
        if not hasattr(self, 'current_image') or self.current_image is None:
            messagebox.showerror("오류", "저장할 검사 결과가 없습니다.")
            return
        
        try:
            # 결과 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inspection_result_{timestamp}.json"
            
            # 검사 결과 수집
            from advanced_analysis import AdvancedDisplayAnalyzer
            analyzer = AdvancedDisplayAnalyzer()
            report = analyzer.create_analysis_report(self.current_image)
            
            # JSON 파일로 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            self.log_result(f"검사 결과 저장: {filename}")
            
        except Exception as e:
            self.log_result(f"결과 저장 실패: {str(e)}")
    
    def create_test_pattern(self):
        """테스트 패턴 생성"""
        try:
            # 테스트 패턴 설정 다이얼로그
            pattern_window = tk.Toplevel(self.root)
            pattern_window.title("테스트 패턴 설정")
            pattern_window.geometry("400x300")
            pattern_window.transient(self.root)
            pattern_window.grab_set()
            
            # 패턴 설정
            ttk.Label(pattern_window, text="패턴 크기 (픽셀):").pack(pady=5)
            size_frame = ttk.Frame(pattern_window)
            size_frame.pack(pady=5)
            
            ttk.Label(size_frame, text="너비:").pack(side=tk.LEFT, padx=5)
            width_var = tk.StringVar(value="1920")
            ttk.Entry(size_frame, textvariable=width_var, width=10).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(size_frame, text="높이:").pack(side=tk.LEFT, padx=5)
            height_var = tk.StringVar(value="1080")
            ttk.Entry(size_frame, textvariable=height_var, width=10).pack(side=tk.LEFT, padx=5)
            
            # 색상 선택
            ttk.Label(pattern_window, text="배경 색상:").pack(pady=5)
            color_var = tk.StringVar(value="R")
            color_frame = ttk.Frame(pattern_window)
            color_frame.pack(pady=5)
            
            ttk.Radiobutton(color_frame, text="빨간색 (R)", variable=color_var, value="R").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(color_frame, text="녹색 (G)", variable=color_var, value="G").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(color_frame, text="파란색 (B)", variable=color_var, value="B").pack(side=tk.LEFT, padx=5)
            ttk.Radiobutton(color_frame, text="흰색 (W)", variable=color_var, value="W").pack(side=tk.LEFT, padx=5)
            
            # 불량 시뮬레이션 옵션
            ttk.Label(pattern_window, text="불량 시뮬레이션:").pack(pady=5)
            defect_frame = ttk.Frame(pattern_window)
            defect_frame.pack(pady=5)
            
            dead_pixel_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(defect_frame, text="데드 픽셀", variable=dead_pixel_var).pack(side=tk.LEFT, padx=5)
            
            hot_pixel_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(defect_frame, text="핫 픽셀", variable=hot_pixel_var).pack(side=tk.LEFT, padx=5)
            
            scratch_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(defect_frame, text="스크래치", variable=scratch_var).pack(side=tk.LEFT, padx=5)
            
            # 생성 버튼
            def generate_pattern():
                try:
                    width = int(width_var.get())
                    height = int(height_var.get())
                    color = color_var.get()
                    
                    # 테스트 패턴 생성
                    pattern = self.generate_test_pattern(width, height, color, 
                                                       dead_pixel_var.get(), 
                                                       hot_pixel_var.get(), 
                                                       scratch_var.get())
                    
                    # 패턴을 현재 이미지로 설정
                    self.current_image = pattern
                    
                    # 패턴 저장
                    cv2.imwrite("test_pattern.png", pattern)
                    
                    self.log_result(f"테스트 패턴 생성 완료: {width}x{height}, 색상: {color}")
                    self.log_result("패턴 저장: test_pattern.png")
                    
                    pattern_window.destroy()
                    
                except Exception as e:
                    messagebox.showerror("오류", f"패턴 생성 실패: {str(e)}")
            
            ttk.Button(pattern_window, text="패턴 생성", command=generate_pattern).pack(pady=10)
            
        except Exception as e:
            self.log_result(f"테스트 패턴 생성 실패: {str(e)}")
    
    def generate_test_pattern(self, width, height, color, dead_pixels=True, hot_pixels=True, scratches=True):
        """테스트 패턴 생성"""
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
        
        # 데드 픽셀 시뮬레이션 (검은 점)
        if dead_pixels:
            for i in range(10):
                x = np.random.randint(50, width-50)
                y = np.random.randint(50, height-50)
                cv2.circle(pattern, (x, y), 2, (0, 0, 0), -1)
        
        # 핫 픽셀 시뮬레이션 (밝은 점)
        if hot_pixels:
            for i in range(5):
                x = np.random.randint(50, width-50)
                y = np.random.randint(50, height-50)
                cv2.circle(pattern, (x, y), 3, (255, 255, 255), -1)
        
        # 스크래치 시뮬레이션 (검은 선)
        if scratches:
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
                defect_color = (0, 0, 200)  # 어두운 빨간색
            elif color == "G":
                defect_color = (0, 200, 0)  # 어두운 녹색
            elif color == "B":
                defect_color = (200, 0, 0)  # 어두운 파란색
            else:
                defect_color = (200, 200, 200)  # 어두운 흰색
            
            cv2.rectangle(pattern, (x, y), (x+100, y+100), defect_color, -1)
        
        return pattern
    
    def detect_display_area(self):
        """디스플레이 영역 감지"""
        if self.current_image is None:
            messagebox.showerror("오류", "먼저 이미지를 캡처하거나 로드해주세요.")
            return
        
        try:
            # Edge detection으로 디스플레이 영역 감지
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            
            # Gaussian blur로 노이즈 제거
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Canny edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # 윤곽선 찾기
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 가장 큰 윤곽선 찾기 (디스플레이 영역으로 추정)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                
                # 윤곽선을 사각형으로 근사
                epsilon = 0.02 * cv2.arcLength(largest_contour, True)
                approx = cv2.approxPolyDP(largest_contour, epsilon, True)
                
                if len(approx) >= 4:
                    # 바운딩 박스 계산
                    x, y, w, h = cv2.boundingRect(approx)
                    
                    # 디스플레이 영역 표시
                    result_image = self.current_image.copy()
                    cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.putText(result_image, "Display Area", (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # 결과 저장
                    cv2.imwrite("display_detection.png", result_image)
                    
                    self.log_result(f"디스플레이 영역 감지 완료: ({x}, {y}, {w}, {h})")
                    self.log_result("감지 결과 저장: display_detection.png")
                    
                    # 감지된 영역을 현재 이미지로 설정
                    self.current_image = result_image
                    
                else:
                    self.log_result("디스플레이 영역을 감지할 수 없습니다.")
            else:
                self.log_result("윤곽선을 찾을 수 없습니다.")
                
        except Exception as e:
            self.log_result(f"디스플레이 감지 실패: {str(e)}")
    
    def start_realtime_inspection(self):
        """실시간 검사 시작"""
        if self.camera is None or not self.camera.isOpened():
            messagebox.showerror("오류", "먼저 카메라를 연결해주세요.")
            return
        
        if self.realtime_inspection:
            self.log_result("실시간 검사가 이미 실행 중입니다.")
            return
        
        self.realtime_inspection = True
        self.inspection_thread = threading.Thread(target=self.realtime_inspection_loop, daemon=True)
        self.inspection_thread.start()
        self.log_result("실시간 검사 시작됨")
    
    def stop_realtime_inspection(self):
        """실시간 검사 중지"""
        self.realtime_inspection = False
        if self.inspection_thread:
            self.inspection_thread.join(timeout=1)
        self.log_result("실시간 검사 중지됨")
    
    def realtime_inspection_loop(self):
        """실시간 검사 루프"""
        frame_count = 0
        
        while self.realtime_inspection and self.camera is not None:
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    frame_count += 1
                    
                    # 5프레임마다 검사 실행 (성능 최적화)
                    if frame_count % 5 == 0:
                        # 디스플레이 영역 자동 감지
                        display_roi = self.auto_detect_display_area(frame)
                        
                        if display_roi is not None:
                            # 감지된 영역에서 검사 실행
                            x, y, w, h = display_roi
                            roi_image = frame[y:y+h, x:x+w]
                            
                            # 검사 실행
                            results = self.quick_inspection(roi_image)
                            
                            # 결과를 원본 프레임에 표시
                            self.draw_inspection_results(frame, display_roi, results)
                            
                            # 미리보기 업데이트
                            self.update_realtime_preview(frame)
                            
                            # 결과 로그
                            if results:
                                self.log_result(f"검사 결과 - 스크래치: {results.get('scratches', 0)}개, "
                                              f"불량화소: {results.get('defects', 0)}개")
                    
                    time.sleep(0.1)  # 10 FPS
                    
            except Exception as e:
                self.log_result(f"실시간 검사 오류: {str(e)}")
                break
        
        self.realtime_inspection = False
    
    def auto_detect_display_area(self, frame):
        """디스플레이 영역 자동 감지"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 가장 큰 윤곽선 찾기
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                # 최소 면적 필터링 (너무 작은 영역 제외)
                if area > 10000:  # 최소 100x100 픽셀
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    return (x, y, w, h)
            
            return None
            
        except Exception as e:
            self.log_result(f"디스플레이 감지 오류: {str(e)}")
            return None
    
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
            cv2.putText(frame, "Display Area", (x, y-10), 
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
    
    def update_realtime_preview(self, frame):
        """실시간 미리보기 업데이트"""
        try:
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
            
        except Exception as e:
            self.log_result(f"미리보기 업데이트 오류: {str(e)}")
    
    def capture_image(self):
        """이미지 캡처"""
        if self.camera is None or not self.camera.isOpened():
            messagebox.showerror("오류", "먼저 카메라를 연결해주세요.")
            return
        
        try:
            ret, frame = self.camera.read()
            if ret:
                self.current_image = frame.copy()
                self.display_image(self.current_image, self.original_label)
                self.log_result("이미지가 성공적으로 캡처되었습니다.")
            else:
                messagebox.showerror("오류", "이미지 캡처에 실패했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"이미지 캡처 중 오류 발생: {str(e)}")
    
    def load_from_file(self):
        """파일에서 이미지 로드"""
        file_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[("이미지 파일", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        
        if file_path:
            try:
                self.current_image = cv2.imread(file_path)
                if self.current_image is not None:
                    self.display_image(self.current_image, self.original_label)
                    self.log_result(f"파일에서 이미지를 로드했습니다: {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("오류", "이미지 파일을 읽을 수 없습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"파일 로드 중 오류 발생: {str(e)}")
    
    def display_image(self, image, label_widget):
        """이미지를 UI에 표시"""
        if image is None:
            return
        
        # 이미지 크기 조정
        height, width = image.shape[:2]
        max_width, max_height = 400, 300
        
        if width > max_width or height > max_height:
            scale = min(max_width/width, max_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # BGR을 RGB로 변환
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # PIL 이미지로 변환
        pil_image = Image.fromarray(image_rgb)
        photo = ImageTk.PhotoImage(pil_image)
        
        # 라벨에 이미지 설정
        label_widget.configure(image=photo)
        label_widget.image = photo  # 참조 유지
    
    def detect_scratches(self):
        """스크래치 감지"""
        if self.current_image is None:
            messagebox.showerror("오류", "먼저 이미지를 로드하거나 캡처해주세요.")
            return
        
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
            
            # 가우시안 블러 적용
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 엣지 감지 (Canny)
            edges = cv2.Canny(blurred, 50, 150)
            
            # 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # 스크래치 후보 찾기 (긴 선형 구조)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, 
                                   minLineLength=50, maxLineGap=10)
            
            result_image = self.current_image.copy()
            scratch_count = 0
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    # 선의 길이 계산
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    if length > 30:  # 최소 길이 임계값
                        cv2.line(result_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        scratch_count += 1
            
            # 결과 표시
            self.display_image(result_image, self.result_label)
            
            # 결과 로그
            self.log_result(f"스크래치 검사 완료: {scratch_count}개의 스크래치가 감지되었습니다.")
            
            # 스크래치 결과 저장
            self.scratch_results = {
                'count': scratch_count,
                'timestamp': datetime.now().isoformat(),
                'image_shape': self.current_image.shape
            }
            
        except Exception as e:
            messagebox.showerror("오류", f"스크래치 감지 중 오류 발생: {str(e)}")
    
    def analyze_rgb(self):
        """RGB 픽셀 분석"""
        if self.current_image is None:
            messagebox.showerror("오류", "먼저 이미지를 로드하거나 캡처해주세요.")
            return
        
        try:
            # RGB 채널 분리
            b, g, r = cv2.split(self.current_image)
            
            # 각 채널의 통계 계산
            rgb_stats = {}
            for channel, name in [(r, 'Red'), (g, 'Green'), (b, 'Blue')]:
                rgb_stats[name] = {
                    'mean': float(np.mean(channel)),
                    'std': float(np.std(channel)),
                    'min': int(np.min(channel)),
                    'max': int(np.max(channel)),
                    'median': int(np.median(channel))
                }
            
            # 픽셀 분포 분석
            total_pixels = self.current_image.shape[0] * self.current_image.shape[1]
            
            # 색상 균일성 분석
            color_variance = np.var(self.current_image.reshape(-1, 3), axis=0)
            
            # 결과 이미지 생성 (RGB 채널 시각화)
            result_image = np.zeros_like(self.current_image)
            result_image[:, :, 0] = b  # Blue
            result_image[:, :, 1] = g  # Green  
            result_image[:, :, 2] = r  # Red
            
            # 결과 표시
            self.display_image(result_image, self.result_label)
            
            # 결과 로그
            self.log_result("RGB 분석 완료:")
            for channel, stats in rgb_stats.items():
                self.log_result(f"  {channel} 채널:")
                self.log_result(f"    평균: {stats['mean']:.2f}")
                self.log_result(f"    표준편차: {stats['std']:.2f}")
                self.log_result(f"    범위: {stats['min']} - {stats['max']}")
            
            self.log_result(f"색상 분산: R={color_variance[2]:.2f}, G={color_variance[1]:.2f}, B={color_variance[0]:.2f}")
            
            # RGB 결과 저장
            self.rgb_results = {
                'statistics': rgb_stats,
                'color_variance': color_variance.tolist(),
                'total_pixels': total_pixels,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            messagebox.showerror("오류", f"RGB 분석 중 오류 발생: {str(e)}")
    
    def save_results(self):
        """결과 저장"""
        if not self.scratch_results and not self.rgb_results:
            messagebox.showwarning("경고", "저장할 결과가 없습니다.")
            return
        
        try:
            # 결과 데이터 구성
            results = {
                'timestamp': datetime.now().isoformat(),
                'scratch_analysis': self.scratch_results,
                'rgb_analysis': self.rgb_results
            }
            
            # 파일 저장
            file_path = filedialog.asksaveasfilename(
                title="결과 저장",
                defaultextension=".json",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                self.log_result(f"결과가 저장되었습니다: {file_path}")
                
                # 이미지도 저장
                if self.current_image is not None:
                    image_path = file_path.replace('.json', '_image.jpg')
                    cv2.imwrite(image_path, self.current_image)
                    self.log_result(f"이미지가 저장되었습니다: {image_path}")
                
        except Exception as e:
            messagebox.showerror("오류", f"결과 저장 중 오류 발생: {str(e)}")
    
    def log_result(self, message):
        """결과 로그 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.result_text.insert(tk.END, log_message)
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        """애플리케이션 실행"""
        try:
            self.root.mainloop()
        finally:
            # 앱 종료 시 정리
            self.stop_preview()
            if self.camera is not None:
                self.camera.release()

def main():
    """메인 함수"""
    app = DisplayInspector()
    app.run()

if __name__ == "__main__":
    main()
