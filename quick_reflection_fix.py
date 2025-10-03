#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
빠른 반사 제거 도구
Quick Reflection Removal Tool
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time

class QuickReflectionFix:
    """빠른 반사 제거 도구"""
    
    def __init__(self):
        self.camera = None
        self.camera_running = False
        self.current_frame = None
        self.setup_ui()
        
    def setup_ui(self):
        """사용자 인터페이스 설정"""
        self.root = tk.Tk()
        self.root.title("빠른 반사 제거 도구")
        self.root.geometry("1200x800")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 제어 패널
        control_frame = ttk.LabelFrame(main_frame, text="빠른 반사 제거")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 카메라 제어
        ttk.Button(control_frame, text="카메라 시작", 
                  command=self.start_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="카메라 중지", 
                  command=self.stop_camera).pack(side=tk.LEFT, padx=5)
        
        # 반사 제거 옵션
        ttk.Label(control_frame, text="반사 제거:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.auto_fix = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="자동 반사 제거", 
                       variable=self.auto_fix).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(control_frame, text="수동 반사 제거", 
                  command=self.manual_reflection_removal).pack(side=tk.LEFT, padx=5)
        
        # 밝기 조정
        ttk.Label(control_frame, text="밝기:").pack(side=tk.LEFT, padx=(20, 5))
        self.brightness_var = tk.DoubleVar(value=1.0)
        brightness_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, 
                                   variable=self.brightness_var, orient=tk.HORIZONTAL, length=100)
        brightness_scale.pack(side=tk.LEFT, padx=5)
        
        # 메인 콘텐츠 영역
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 원본
        left_frame = ttk.LabelFrame(content_frame, text="원본 (반사 있음)")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.original_label = ttk.Label(left_frame, text="카메라를 시작하세요")
        self.original_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 오른쪽: 처리됨
        right_frame = ttk.LabelFrame(content_frame, text="처리됨 (반사 제거)")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.processed_label = ttk.Label(right_frame, text="반사 제거 결과")
        self.processed_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 하단: 가이드
        guide_frame = ttk.LabelFrame(main_frame, text="반사 제거 가이드")
        guide_frame.pack(fill=tk.X, pady=(10, 0))
        
        guide_text = """💡 반사 제거 팁:
1. 카메라를 15-30도 각도로 기울이세요
2. 측면 조명을 사용하세요 (정면 조명 피하기)
3. 디스플레이와 카메라 사이 거리를 30-50cm로 조정하세요
4. 어두운 배경에서 검사하세요
5. 편광 필터 사용을 고려하세요 (가장 효과적)"""
        
        ttk.Label(guide_frame, text=guide_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
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
                break
    
    def update_displays(self, frame):
        """디스플레이 업데이트"""
        try:
            # 원본 이미지 표시
            self.display_image(frame, self.original_label)
            
            # 반사 제거 처리
            if self.auto_fix.get():
                processed_frame = self.quick_reflection_removal(frame)
            else:
                processed_frame = frame
            
            # 처리된 이미지 표시
            self.display_image(processed_frame, self.processed_label)
            
        except Exception as e:
            pass
    
    def display_image(self, image, label_widget):
        """이미지를 UI에 표시"""
        if image is None:
            return
        
        # 이미지 크기 조정
        height, width = image.shape[:2]
        max_width, max_height = 500, 350
        
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
    
    def quick_reflection_removal(self, frame):
        """빠른 반사 제거"""
        try:
            # 1. 밝기 조정
            brightness = self.brightness_var.get()
            result = cv2.convertScaleAbs(frame, alpha=brightness, beta=0)
            
            # 2. 반사 영역 감지 및 제거
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            
            # 밝은 영역 (반사 영역) 감지
            bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]
            
            # 모폴로지 연산으로 노이즈 제거
            kernel = np.ones((5, 5), np.uint8)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_CLOSE, kernel)
            bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
            
            # 3. 반사 영역에 블러 적용
            blurred = cv2.GaussianBlur(result, (15, 15), 0)
            
            # 반사 영역만 블러 처리
            result[bright_mask > 0] = blurred[bright_mask > 0]
            
            # 4. 대비 개선
            lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # CLAHE 적용
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # LAB 채널 합치기
            lab = cv2.merge([l, a, b])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            return result
            
        except Exception as e:
            return frame
    
    def manual_reflection_removal(self):
        """수동 반사 제거"""
        if self.current_frame is None:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        try:
            # 현재 프레임에 반사 제거 적용
            processed_frame = self.quick_reflection_removal(self.current_frame)
            
            # 결과 표시
            self.display_image(processed_frame, self.processed_label)
            
            messagebox.showinfo("완료", "수동 반사 제거가 완료되었습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"반사 제거 중 오류: {str(e)}")
    
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
    app = QuickReflectionFix()
    app.run()

if __name__ == "__main__":
    main()
