#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
반사 제거 및 조명 제어 시스템
Reflection Removal and Lighting Control System
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime

class ReflectionHandler:
    """반사 제거 및 조명 제어 클래스"""
    
    def __init__(self):
        self.camera = None
        self.camera_running = False
        self.current_frame = None
        self.reflection_mask = None
        self.setup_ui()
        
    def setup_ui(self):
        """사용자 인터페이스 설정"""
        self.root = tk.Tk()
        self.root.title("반사 제거 시스템 - 디스플레이 검사")
        self.root.geometry("1600x1000")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제어 패널
        control_frame = ttk.LabelFrame(main_frame, text="반사 제거 제어")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 카메라 제어
        camera_frame = ttk.Frame(control_frame)
        camera_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(camera_frame, text="카메라 시작", 
                  command=self.start_camera).pack(side=tk.LEFT, padx=2)
        ttk.Button(camera_frame, text="카메라 중지", 
                  command=self.stop_camera).pack(side=tk.LEFT, padx=2)
        
        # 반사 제거 옵션
        reflection_frame = ttk.Frame(control_frame)
        reflection_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(reflection_frame, text="반사 제거 방법:").pack(side=tk.LEFT)
        
        self.reflection_method = tk.StringVar(value="polarization")
        ttk.Radiobutton(reflection_frame, text="편광 필터", variable=self.reflection_method, 
                       value="polarization").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(reflection_frame, text="각도 조정", variable=self.reflection_method, 
                       value="angle").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(reflection_frame, text="조명 제어", variable=self.reflection_method, 
                       value="lighting").pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(reflection_frame, text="AI 제거", variable=self.reflection_method, 
                       value="ai").pack(side=tk.LEFT, padx=2)
        
        # 조명 제어
        lighting_frame = ttk.Frame(control_frame)
        lighting_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(lighting_frame, text="조명 밝기:").pack(side=tk.LEFT)
        self.brightness_var = tk.DoubleVar(value=0.5)
        brightness_scale = ttk.Scale(lighting_frame, from_=0.0, to=1.0, 
                                   variable=self.brightness_var, orient=tk.HORIZONTAL, length=100)
        brightness_scale.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(lighting_frame, text="조명 최적화", 
                  command=self.optimize_lighting).pack(side=tk.LEFT, padx=2)
        
        # 메인 콘텐츠 영역
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 원본 카메라 뷰
        left_frame = ttk.LabelFrame(content_frame, text="원본 카메라 뷰")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.original_label = ttk.Label(left_frame, text="카메라를 시작하세요")
        self.original_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 오른쪽: 반사 제거된 뷰
        right_frame = ttk.LabelFrame(content_frame, text="반사 제거된 뷰")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.processed_label = ttk.Label(right_frame, text="반사 제거 결과")
        self.processed_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 하단: 가이드 및 결과
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 가이드 프레임
        guide_frame = ttk.LabelFrame(bottom_frame, text="반사 제거 가이드")
        guide_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.guide_text = tk.Text(guide_frame, height=8, wrap=tk.WORD)
        guide_scrollbar = ttk.Scrollbar(guide_frame, orient=tk.VERTICAL, 
                                      command=self.guide_text.yview)
        self.guide_text.configure(yscrollcommand=guide_scrollbar.set)
        
        self.guide_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        guide_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 결과 프레임
        result_frame = ttk.LabelFrame(bottom_frame, text="반사 제거 결과")
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.result_text = tk.Text(result_frame, height=8, wrap=tk.WORD)
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, 
                                       command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 초기 가이드 텍스트 설정
        self.update_guide_text()
        
    def update_guide_text(self):
        """가이드 텍스트 업데이트"""
        guide_text = """반사 제거 가이드:

1. 편광 필터 방법:
   - 편광 필터를 카메라 렌즈에 부착
   - 필터를 회전시켜 반사 최소화
   - 45도 각도에서 최적 효과

2. 각도 조정 방법:
   - 카메라를 15-30도 각도로 기울임
   - 디스플레이와 카메라 사이 거리 조정
   - 반사가 최소화되는 위치 찾기

3. 조명 제어 방법:
   - 측면 조명 사용 (정면 조명 피하기)
   - LED 스트립 조명 권장
   - 균일한 조명 분포 확보

4. AI 제거 방법:
   - 딥러닝 기반 반사 제거
   - 실시간 반사 영역 감지
   - 자동 보정 및 복원

현재 선택된 방법에 따라 가이드가 업데이트됩니다."""
        
        self.guide_text.delete(1.0, tk.END)
        self.guide_text.insert(1.0, guide_text)
    
    def start_camera(self):
        """카메라 시작"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                messagebox.showerror("오류", "카메라를 열 수 없습니다.")
                return
            
            # 카메라 설정
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
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
        self.original_label.configure(image='', text="카메라가 중지되었습니다")
        self.processed_label.configure(image='', text="반사 제거 결과")
    
    def camera_loop(self):
        """카메라 루프"""
        while self.camera_running and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    self.current_frame = frame.copy()
                    self.update_displays(frame)
                time.sleep(0.03)  # 30 FPS
            except Exception as e:
                self.log_result(f"카메라 루프 오류: {str(e)}")
                break
    
    def update_displays(self, frame):
        """디스플레이 업데이트"""
        try:
            # 원본 이미지 표시
            self.display_image(frame, self.original_label)
            
            # 반사 제거 처리
            processed_frame = self.remove_reflection(frame)
            
            # 처리된 이미지 표시
            self.display_image(processed_frame, self.processed_label)
            
        except Exception as e:
            self.log_result(f"디스플레이 업데이트 오류: {str(e)}")
    
    def display_image(self, image, label_widget):
        """이미지를 UI에 표시"""
        if image is None:
            return
        
        # 이미지 크기 조정
        height, width = image.shape[:2]
        max_width, max_height = 600, 400
        
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
        label_widget.configure(image=photo, text="")
        label_widget.image = photo  # 참조 유지
    
    def remove_reflection(self, frame):
        """반사 제거 처리"""
        method = self.reflection_method.get()
        
        if method == "polarization":
            return self.polarization_filter(frame)
        elif method == "angle":
            return self.angle_adjustment(frame)
        elif method == "lighting":
            return self.lighting_control(frame)
        elif method == "ai":
            return self.ai_reflection_removal(frame)
        else:
            return frame
    
    def polarization_filter(self, frame):
        """편광 필터 시뮬레이션"""
        try:
            # HSV 변환
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 밝은 영역 (반사 영역) 감지
            bright_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
            
            # 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((5, 5), np.uint8)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
            
            # 반사 영역에 가우시안 블러 적용
            blurred = cv2.GaussianBlur(frame, (15, 15), 0)
            
            # 반사 영역만 블러 처리
            result = frame.copy()
            result[bright_mask > 0] = blurred[bright_mask > 0]
            
            # 밝기 조정
            brightness = self.brightness_var.get()
            result = cv2.convertScaleAbs(result, alpha=brightness, beta=0)
            
            return result
            
        except Exception as e:
            self.log_result(f"편광 필터 처리 오류: {str(e)}")
            return frame
    
    def angle_adjustment(self, frame):
        """각도 조정 시뮬레이션"""
        try:
            # 이미지 크기
            height, width = frame.shape[:2]
            
            # 원근 변환을 통한 각도 조정 시뮬레이션
            # 카메라가 기울어진 효과
            pts1 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
            pts2 = np.float32([[0, 0], [width, 0], [50, height], [width-50, height]])
            
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            result = cv2.warpPerspective(frame, matrix, (width, height))
            
            # 밝기 조정
            brightness = self.brightness_var.get()
            result = cv2.convertScaleAbs(result, alpha=brightness, beta=0)
            
            return result
            
        except Exception as e:
            self.log_result(f"각도 조정 처리 오류: {str(e)}")
            return frame
    
    def lighting_control(self, frame):
        """조명 제어"""
        try:
            # 밝기 조정
            brightness = self.brightness_var.get()
            result = cv2.convertScaleAbs(frame, alpha=brightness, beta=0)
            
            # 대비 조정
            lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # LAB 채널 합치기
            lab = cv2.merge([l, a, b])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            return result
            
        except Exception as e:
            self.log_result(f"조명 제어 처리 오류: {str(e)}")
            return frame
    
    def ai_reflection_removal(self, frame):
        """AI 기반 반사 제거"""
        try:
            # 간단한 AI 시뮬레이션 (실제로는 더 복잡한 모델 사용)
            
            # 1. 반사 영역 감지
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 밝은 영역 감지
            bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
            
            # 모폴로지 연산
            kernel = np.ones((10, 10), np.uint8)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
            
            # 2. 반사 영역 복원
            result = frame.copy()
            
            # 반사 영역에 인페인팅 적용
            result = cv2.inpaint(result, bright_mask, 3, cv2.INPAINT_TELEA)
            
            # 3. 색상 보정
            result = cv2.bilateralFilter(result, 9, 75, 75)
            
            # 밝기 조정
            brightness = self.brightness_var.get()
            result = cv2.convertScaleAbs(result, alpha=brightness, beta=0)
            
            return result
            
        except Exception as e:
            self.log_result(f"AI 반사 제거 처리 오류: {str(e)}")
            return frame
    
    def optimize_lighting(self):
        """조명 최적화"""
        if self.current_frame is None:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        try:
            # 현재 프레임 분석
            gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
            
            # 평균 밝기 계산
            mean_brightness = np.mean(gray)
            
            # 최적 밝기 계산 (128 목표)
            optimal_alpha = 128.0 / mean_brightness if mean_brightness > 0 else 1.0
            
            # 밝기 조정
            self.brightness_var.set(min(1.0, max(0.1, optimal_alpha)))
            
            self.log_result(f"조명 최적화 완료: 평균 밝기 {mean_brightness:.1f} -> 목표 128")
            
        except Exception as e:
            self.log_result(f"조명 최적화 오류: {str(e)}")
    
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
        if self.camera:
            self.camera.release()
        self.root.destroy()

def main():
    """메인 함수"""
    app = ReflectionHandler()
    app.run()

if __name__ == "__main__":
    main()
