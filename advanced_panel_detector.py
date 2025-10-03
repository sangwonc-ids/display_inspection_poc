#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 패널 감지 및 캘리브레이션 시스템
Advanced Panel Detection and Calibration System
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import json
import os

class AdvancedPanelDetector:
    """고급 패널 감지 시스템"""
    
    def __init__(self):
        self.camera = None
        self.camera_running = False
        self.current_frame = None
        self.panel_contour = None
        self.calibration_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """사용자 인터페이스 설정"""
        self.root = tk.Tk()
        self.root.title("고급 패널 검사 시스템")
        self.root.geometry("1600x1000")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제어 패널
        control_frame = ttk.LabelFrame(main_frame, text="제어 패널")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 카메라 제어
        camera_frame = ttk.Frame(control_frame)
        camera_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(camera_frame, text="카메라 시작", 
                  command=self.start_camera).pack(side=tk.LEFT, padx=2)
        ttk.Button(camera_frame, text="카메라 중지", 
                  command=self.stop_camera).pack(side=tk.LEFT, padx=2)
        
        # 캘리브레이션
        calib_frame = ttk.Frame(control_frame)
        calib_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(calib_frame, text="캘리브레이션", 
                  command=self.start_calibration).pack(side=tk.LEFT, padx=2)
        ttk.Button(calib_frame, text="캘리브레이션 저장", 
                  command=self.save_calibration).pack(side=tk.LEFT, padx=2)
        ttk.Button(calib_frame, text="캘리브레이션 로드", 
                  command=self.load_calibration).pack(side=tk.LEFT, padx=2)
        
        # 검사 제어
        inspect_frame = ttk.Frame(control_frame)
        inspect_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(inspect_frame, text="자동 패널 감지", 
                  command=self.auto_detect_panel).pack(side=tk.LEFT, padx=2)
        ttk.Button(inspect_frame, text="검사 시작", 
                  command=self.start_inspection).pack(side=tk.LEFT, padx=2)
        ttk.Button(inspect_frame, text="결과 저장", 
                  command=self.save_results).pack(side=tk.LEFT, padx=2)
        
        # 메인 콘텐츠 영역
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 카메라 뷰
        left_frame = ttk.LabelFrame(content_frame, text="실시간 카메라 뷰")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.camera_label = ttk.Label(left_frame, text="카메라를 시작하세요")
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 오른쪽: 검사 결과
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 패널 정보
        panel_frame = ttk.LabelFrame(right_frame, text="패널 정보")
        panel_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.panel_info_text = tk.Text(panel_frame, height=6, wrap=tk.WORD)
        panel_scrollbar = ttk.Scrollbar(panel_frame, orient=tk.VERTICAL, 
                                      command=self.panel_info_text.yview)
        self.panel_info_text.configure(yscrollcommand=panel_scrollbar.set)
        
        self.panel_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        panel_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 검사 결과
        result_frame = ttk.LabelFrame(right_frame, text="검사 결과")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(result_frame, height=12, wrap=tk.WORD)
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, 
                                       command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 품질 점수
        quality_frame = ttk.LabelFrame(right_frame, text="품질 점수")
        quality_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.quality_label = ttk.Label(quality_frame, text="품질 점수: --/100", 
                                     font=('Arial', 14, 'bold'))
        self.quality_label.pack(padx=10, pady=10)
        
        # 검사 상태 변수
        self.inspection_running = False
        self.calibration_running = False
        
    def start_camera(self):
        """카메라 시작"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("오류", "카메라를 열 수 없습니다.")
                return
            
            # 카메라 설정
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.camera_running = True
            self.log_result("카메라가 시작되었습니다.")
            
            # 카메라 스레드 시작
            self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.camera_thread.start()
            
        except Exception as e:
            messagebox.showerror("오류", f"카메라 시작 중 오류: {str(e)}")
    
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
            # 패널 감지 및 표시
            display_frame = self.draw_panel_detection(frame)
            
            # 이미지 크기 조정
            height, width = display_frame.shape[:2]
            max_width, max_height = 700, 500
            
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
    
    def draw_panel_detection(self, frame):
        """패널 감지 결과 그리기"""
        display_frame = frame.copy()
        
        if self.panel_contour is not None:
            # 감지된 패널 표시
            cv2.drawContours(display_frame, [self.panel_contour], -1, (0, 255, 0), 3)
            
            # 패널 정보 표시
            if len(self.panel_contour) >= 4:
                # 패널 중심점
                M = cv2.moments(self.panel_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(display_frame, (cx, cy), 5, (0, 0, 255), -1)
                    
                    # 패널 크기 정보
                    x, y, w, h = cv2.boundingRect(self.panel_contour)
                    cv2.putText(display_frame, f"Size: {w}x{h}", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return display_frame
    
    def start_calibration(self):
        """캘리브레이션 시작"""
        if not self.camera_running:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        self.calibration_running = True
        self.log_result("캘리브레이션을 시작합니다. 패널을 카메라 앞에 놓고 '자동 패널 감지'를 클릭하세요.")
    
    def auto_detect_panel(self):
        """자동 패널 감지"""
        if self.current_frame is None:
            messagebox.showwarning("경고", "카메라에서 이미지를 가져올 수 없습니다.")
            return
        
        try:
            # 패널 감지 알고리즘
            panel_contour = self.detect_panel_contour(self.current_frame)
            
            if panel_contour is not None:
                self.panel_contour = panel_contour
                self.update_panel_info()
                self.log_result("패널이 성공적으로 감지되었습니다.")
            else:
                self.log_result("패널을 감지할 수 없습니다. 패널 위치를 조정하고 다시 시도하세요.")
                
        except Exception as e:
            self.log_result(f"패널 감지 오류: {str(e)}")
    
    def detect_panel_contour(self, frame):
        """패널 윤곽선 감지"""
        try:
            # 그레이스케일 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 가우시안 블러
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 적응적 임계값
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # 모폴로지 연산
            kernel = np.ones((3, 3), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # 윤곽선 찾기
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # 가장 큰 윤곽선 선택
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 윤곽선 근사화
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            # 사각형인지 확인 (4개 꼭짓점)
            if len(approx) >= 4:
                # 면적이 충분한지 확인
                area = cv2.contourArea(approx)
                if area > 10000:  # 최소 면적
                    return approx
            
            return None
            
        except Exception as e:
            self.log_result(f"패널 윤곽선 감지 오류: {str(e)}")
            return None
    
    def update_panel_info(self):
        """패널 정보 업데이트"""
        if self.panel_contour is None:
            return
        
        try:
            # 패널 크기 계산
            x, y, w, h = cv2.boundingRect(self.panel_contour)
            area = cv2.contourArea(self.panel_contour)
            
            # 종횡비 계산
            aspect_ratio = w / h if h > 0 else 0
            
            # 패널 중심점
            M = cv2.moments(self.panel_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = x + w//2, y + h//2
            
            # 패널 정보 텍스트
            info_text = f"패널 정보:\n"
            info_text += f"위치: ({x}, {y})\n"
            info_text += f"크기: {w} x {h} 픽셀\n"
            info_text += f"면적: {area:.0f} 픽셀²\n"
            info_text += f"종횡비: {aspect_ratio:.2f}\n"
            info_text += f"중심점: ({cx}, {cy})\n"
            
            # 디스플레이 타입 추정
            if 1.7 <= aspect_ratio <= 1.8:
                info_text += f"추정 타입: 16:9 디스플레이\n"
            elif 1.5 <= aspect_ratio <= 1.6:
                info_text += f"추정 타입: 16:10 디스플레이\n"
            elif 1.3 <= aspect_ratio <= 1.4:
                info_text += f"추정 타입: 4:3 디스플레이\n"
            elif 2.3 <= aspect_ratio <= 2.4:
                info_text += f"추정 타입: 21:9 디스플레이\n"
            else:
                info_text += f"추정 타입: 사용자 정의\n"
            
            self.panel_info_text.delete(1.0, tk.END)
            self.panel_info_text.insert(1.0, info_text)
            
        except Exception as e:
            self.log_result(f"패널 정보 업데이트 오류: {str(e)}")
    
    def start_inspection(self):
        """검사 시작"""
        if self.panel_contour is None:
            messagebox.showwarning("경고", "먼저 패널을 감지하세요.")
            return
        
        if not self.camera_running:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        self.inspection_running = True
        self.log_result("검사가 시작되었습니다.")
        
        # 검사 스레드 시작
        self.inspection_thread = threading.Thread(target=self.inspection_loop, daemon=True)
        self.inspection_thread.start()
    
    def inspection_loop(self):
        """검사 루프"""
        while self.inspection_running and self.camera_running:
            try:
                if self.current_frame is not None and self.panel_contour is not None:
                    # 패널 영역 추출
                    panel_region = self.extract_panel_region(self.current_frame, self.panel_contour)
                    
                    if panel_region is not None:
                        # 검사 실행
                        results = self.perform_advanced_inspection(panel_region)
                        self.update_inspection_results(results)
                
                time.sleep(2)  # 2초마다 검사
                
            except Exception as e:
                self.log_result(f"검사 루프 오류: {str(e)}")
                break
    
    def extract_panel_region(self, frame, contour):
        """패널 영역 추출"""
        try:
            # 마스크 생성
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(mask, [contour], 255)
            
            # 패널 영역 추출
            panel_region = cv2.bitwise_and(frame, frame, mask=mask)
            
            # 경계 상자로 자르기
            x, y, w, h = cv2.boundingRect(contour)
            panel_region = panel_region[y:y+h, x:x+w]
            
            return panel_region
            
        except Exception as e:
            self.log_result(f"패널 영역 추출 오류: {str(e)}")
            return None
    
    def perform_advanced_inspection(self, panel_region):
        """고급 검사 수행"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'defects': [],
            'quality_score': 0
        }
        
        try:
            # 1. 스크래치 감지
            scratches = self.detect_advanced_scratches(panel_region)
            results['defects'].extend(scratches)
            
            # 2. 데드 픽셀 감지
            dead_pixels = self.detect_advanced_dead_pixels(panel_region)
            results['defects'].extend(dead_pixels)
            
            # 3. 색상 균일성 검사
            color_issues = self.check_advanced_color_uniformity(panel_region)
            results['defects'].extend(color_issues)
            
            # 4. 밝기 균일성 검사
            brightness_issues = self.check_brightness_uniformity(panel_region)
            results['defects'].extend(brightness_issues)
            
            # 5. 품질 점수 계산
            results['quality_score'] = self.calculate_advanced_quality_score(results)
            
        except Exception as e:
            results['defects'].append(f"검사 중 오류: {str(e)}")
        
        return results
    
    def detect_advanced_scratches(self, region):
        """고급 스크래치 감지"""
        scratches = []
        
        try:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # 가우시안 블러
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Canny 엣지 감지
            edges = cv2.Canny(blurred, 50, 150)
            
            # 모폴로지 연산
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Hough 선 변환
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=30, 
                                   minLineLength=20, maxLineGap=5)
            
            if lines is not None:
                scratch_count = 0
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    if length > 15:
                        scratch_count += 1
                
                if scratch_count > 0:
                    scratches.append(f"스크래치 {scratch_count}개 감지")
            
        except Exception as e:
            scratches.append(f"스크래치 감지 오류: {str(e)}")
        
        return scratches
    
    def detect_advanced_dead_pixels(self, region):
        """고급 데드 픽셀 감지"""
        dead_pixels = []
        
        try:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # 로컬 평균 계산
            kernel = np.ones((5, 5), np.float32) / 25
            local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
            
            # 데드 픽셀 후보 찾기
            diff = np.abs(gray.astype(np.float32) - local_mean)
            dead_pixel_mask = diff > (0.1 * 255)
            
            dead_pixel_count = np.sum(dead_pixel_mask)
            if dead_pixel_count > 5:
                dead_pixels.append(f"데드 픽셀 {dead_pixel_count}개 감지")
            
        except Exception as e:
            dead_pixels.append(f"데드 픽셀 감지 오류: {str(e)}")
        
        return dead_pixels
    
    def check_advanced_color_uniformity(self, region):
        """고급 색상 균일성 검사"""
        color_issues = []
        
        try:
            # 각 채널 분석
            b, g, r = cv2.split(region)
            
            # 표준편차 계산
            std_b = np.std(b)
            std_g = np.std(g)
            std_r = np.std(r)
            
            # 색상 불균일성 임계값
            threshold = 40
            
            if std_b > threshold or std_g > threshold or std_r > threshold:
                color_issues.append(f"색상 불균일성 감지 (B:{std_b:.1f}, G:{std_g:.1f}, R:{std_r:.1f})")
            
            # 색상 편차 계산
            mean_b, mean_g, mean_r = np.mean(b), np.mean(g), np.mean(r)
            color_variance = np.var([mean_b, mean_g, mean_r])
            
            if color_variance > 1000:
                color_issues.append(f"색상 편차 과다: {color_variance:.1f}")
            
        except Exception as e:
            color_issues.append(f"색상 균일성 검사 오류: {str(e)}")
        
        return color_issues
    
    def check_brightness_uniformity(self, region):
        """밝기 균일성 검사"""
        brightness_issues = []
        
        try:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # 그리드 기반 밝기 분석
            h, w = gray.shape
            grid_size = 10
            
            brightness_values = []
            for i in range(0, h, h//grid_size):
                for j in range(0, w, w//grid_size):
                    grid_region = gray[i:i+h//grid_size, j:j+w//grid_size]
                    if grid_region.size > 0:
                        brightness_values.append(np.mean(grid_region))
            
            if brightness_values:
                brightness_std = np.std(brightness_values)
                if brightness_std > 30:
                    brightness_issues.append(f"밝기 불균일성 감지 (표준편차: {brightness_std:.1f})")
            
        except Exception as e:
            brightness_issues.append(f"밝기 균일성 검사 오류: {str(e)}")
        
        return brightness_issues
    
    def calculate_advanced_quality_score(self, results):
        """고급 품질 점수 계산"""
        score = 100
        
        # 결함별 감점
        for defect in results['defects']:
            if "스크래치" in defect:
                score -= 8
            elif "데드 픽셀" in defect:
                score -= 12
            elif "색상 불균일성" in defect:
                score -= 15
            elif "밝기 불균일성" in defect:
                score -= 10
            elif "색상 편차" in defect:
                score -= 20
            elif "오류" in defect:
                score -= 25
        
        return max(0, score)
    
    def update_inspection_results(self, results):
        """검사 결과 업데이트"""
        # 품질 점수 업데이트
        quality_score = results['quality_score']
        self.quality_label.configure(text=f"품질 점수: {quality_score}/100")
        
        # 결과 텍스트 업데이트
        self.result_text.delete(1.0, tk.END)
        
        result_text = f"검사 시간: {results['timestamp']}\n"
        result_text += f"품질 점수: {quality_score}/100\n\n"
        
        if results['defects']:
            result_text += "발견된 결함:\n"
            for i, defect in enumerate(results['defects'], 1):
                result_text += f"{i}. {defect}\n"
        else:
            result_text += "결함이 발견되지 않았습니다.\n"
        
        self.result_text.insert(1.0, result_text)
    
    def log_result(self, message):
        """결과 로그"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.result_text.insert(tk.END, log_message)
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def save_calibration(self):
        """캘리브레이션 저장"""
        if self.panel_contour is None:
            messagebox.showwarning("경고", "저장할 캘리브레이션 데이터가 없습니다.")
            return
        
        try:
            calibration_data = {
                'panel_contour': self.panel_contour.tolist(),
                'timestamp': datetime.now().isoformat()
            }
            
            file_path = filedialog.asksaveasfilename(
                title="캘리브레이션 저장",
                defaultextension=".json",
                filetypes=[("JSON 파일", "*.json")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(calibration_data, f, ensure_ascii=False, indent=2)
                
                self.log_result(f"캘리브레이션이 저장되었습니다: {file_path}")
                
        except Exception as e:
            messagebox.showerror("오류", f"캘리브레이션 저장 중 오류: {str(e)}")
    
    def load_calibration(self):
        """캘리브레이션 로드"""
        try:
            file_path = filedialog.askopenfilename(
                title="캘리브레이션 로드",
                filetypes=[("JSON 파일", "*.json")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    calibration_data = json.load(f)
                
                self.panel_contour = np.array(calibration_data['panel_contour'], dtype=np.int32)
                self.update_panel_info()
                self.log_result(f"캘리브레이션이 로드되었습니다: {file_path}")
                
        except Exception as e:
            messagebox.showerror("오류", f"캘리브레이션 로드 중 오류: {str(e)}")
    
    def save_results(self):
        """결과 저장"""
        # 구현 생략 - 기본 패널 검사 시스템과 동일
        pass
    
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

def main():
    """메인 함수"""
    app = AdvancedPanelDetector()
    app.run()

if __name__ == "__main__":
    main()
