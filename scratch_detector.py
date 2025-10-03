#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스크래치 검사 모듈
업계 표준 스크래치 검사 방법을 소프트웨어로 구현
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class ScratchDetector:
    def __init__(self):
        self.camera = None
        self.camera_running = False
        self.scratch_detection_active = False
        self.angle = 0  # 검사 각도 (0-360도)
        self.lighting_intensity = 100  # 조명 강도 (0-255)
        self.polarizer_angle = 0  # 편광 필터 각도
        
    def start_camera(self):
        """카메라 시작"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                raise Exception("카메라를 열 수 없습니다")
            
            # 카메라 설정
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            self.camera_running = True
            return True
        except Exception as e:
            print(f"카메라 시작 오류: {e}")
            return False
    
    def stop_camera(self):
        """카메라 중지"""
        self.camera_running = False
        if self.camera:
            self.camera.release()
    
    def apply_lighting_simulation(self, frame, angle, intensity):
        """조명 시뮬레이션 적용"""
        # 각도에 따른 조명 효과
        if angle == 0:  # 정면 조명
            # 균등한 조명
            lighting = np.ones_like(frame, dtype=np.float32)
        elif angle == 45:  # 45도 측면 조명
            # 좌측에서 오는 조명
            h, w = frame.shape[:2]
            x = np.linspace(0, 1, w)
            y = np.linspace(0, 1, h)
            X, Y = np.meshgrid(x, y)
            lighting = (X * 0.7 + 0.3) * intensity / 255.0
            lighting = np.stack([lighting] * 3, axis=2)
        elif angle == 90:  # 90도 측면 조명
            # 강한 측면 조명
            h, w = frame.shape[:2]
            x = np.linspace(0, 1, w)
            lighting = (x * 0.5 + 0.5) * intensity / 255.0
            lighting = np.stack([lighting] * 3, axis=2)
        else:  # 기타 각도
            # 복합 조명
            h, w = frame.shape[:2]
            x = np.linspace(0, 1, w)
            y = np.linspace(0, 1, h)
            X, Y = np.meshgrid(x, y)
            lighting = (X * 0.6 + Y * 0.4) * intensity / 255.0
            lighting = np.stack([lighting] * 3, axis=2)
        
        # 조명 적용
        enhanced_frame = frame.astype(np.float32) * lighting
        enhanced_frame = np.clip(enhanced_frame, 0, 255).astype(np.uint8)
        
        return enhanced_frame
    
    def apply_polarizer_effect(self, frame, angle):
        """편광 필터 효과 적용"""
        # 편광 각도에 따른 반사광 제거
        if angle == 0:
            return frame
        
        # HSV 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 편광 효과 (반사광 제거)
        polarizer_strength = abs(np.sin(np.radians(angle * 2))) * 0.3
        hsv[:, :, 1] = hsv[:, :, 1] * (1 - polarizer_strength)  # 채도 감소
        hsv[:, :, 2] = hsv[:, :, 2] * (1 - polarizer_strength * 0.5)  # 명도 조정
        
        # BGR로 변환
        filtered_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        return filtered_frame
    
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
            return "스크래치 없음", 0
        
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

class ScratchInspectionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("스크래치 검사 시스템")
        self.root.geometry("1200x800")
        
        self.detector = ScratchDetector()
        self.setup_ui()
        
    def setup_ui(self):
        """UI 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 카메라 화면
        self.camera_frame = ttk.LabelFrame(main_frame, text="카메라 화면")
        self.camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # 제어 패널
        control_frame = ttk.LabelFrame(main_frame, text="검사 제어")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 카메라 제어
        camera_control = ttk.LabelFrame(control_frame, text="카메라 제어")
        camera_control.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(camera_control, text="카메라 시작", 
                  command=self.start_camera).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(camera_control, text="카메라 중지", 
                  command=self.stop_camera).pack(fill=tk.X, padx=5, pady=5)
        
        # 조명 제어
        lighting_control = ttk.LabelFrame(control_frame, text="조명 제어")
        lighting_control.pack(fill=tk.X, pady=(0, 10))
        
        # 조명 각도
        ttk.Label(lighting_control, text="조명 각도:").pack(anchor=tk.W, padx=5)
        self.angle_var = tk.IntVar(value=0)
        angle_scale = ttk.Scale(lighting_control, from_=0, to=90, 
                               variable=self.angle_var, orient=tk.HORIZONTAL)
        angle_scale.pack(fill=tk.X, padx=5, pady=5)
        
        # 조명 강도
        ttk.Label(lighting_control, text="조명 강도:").pack(anchor=tk.W, padx=5)
        self.intensity_var = tk.IntVar(value=100)
        intensity_scale = ttk.Scale(lighting_control, from_=0, to=255, 
                                   variable=self.intensity_var, orient=tk.HORIZONTAL)
        intensity_scale.pack(fill=tk.X, padx=5, pady=5)
        
        # 편광 필터
        polarizer_control = ttk.LabelFrame(control_frame, text="편광 필터")
        polarizer_control.pack(fill=tk.X, pady=(0, 10))
        
        self.polarizer_var = tk.BooleanVar()
        ttk.Checkbutton(polarizer_control, text="편광 필터 사용", 
                       variable=self.polarizer_var).pack(anchor=tk.W, padx=5)
        
        ttk.Label(polarizer_control, text="편광 각도:").pack(anchor=tk.W, padx=5)
        self.polarizer_angle_var = tk.IntVar(value=0)
        polarizer_scale = ttk.Scale(polarizer_control, from_=0, to=180, 
                                   variable=self.polarizer_angle_var, orient=tk.HORIZONTAL)
        polarizer_scale.pack(fill=tk.X, padx=5, pady=5)
        
        # 검사 제어
        inspection_control = ttk.LabelFrame(control_frame, text="검사 제어")
        inspection_control.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(inspection_control, text="스크래치 검사 시작", 
                  command=self.start_scratch_inspection).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(inspection_control, text="검사 중지", 
                  command=self.stop_scratch_inspection).pack(fill=tk.X, padx=5, pady=5)
        
        # 결과 표시
        result_frame = ttk.LabelFrame(control_frame, text="검사 결과")
        result_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.result_text = tk.Text(result_frame, height=8, width=30)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
    def start_camera(self):
        """카메라 시작"""
        if self.detector.start_camera():
            self.update_camera_display()
            messagebox.showinfo("성공", "카메라가 시작되었습니다")
        else:
            messagebox.showerror("오류", "카메라를 시작할 수 없습니다")
    
    def stop_camera(self):
        """카메라 중지"""
        self.detector.stop_camera()
        messagebox.showinfo("정보", "카메라가 중지되었습니다")
    
    def start_scratch_inspection(self):
        """스크래치 검사 시작"""
        if not self.detector.camera_running:
            messagebox.showerror("오류", "먼저 카메라를 시작하세요")
            return
        
        self.detector.scratch_detection_active = True
        messagebox.showinfo("정보", "스크래치 검사가 시작되었습니다")
    
    def stop_scratch_inspection(self):
        """스크래치 검사 중지"""
        self.detector.scratch_detection_active = False
        messagebox.showinfo("정보", "스크래치 검사가 중지되었습니다")
    
    def update_camera_display(self):
        """카메라 화면 업데이트"""
        if not self.detector.camera_running:
            return
        
        ret, frame = self.detector.camera.read()
        if not ret:
            return
        
        # 조명 시뮬레이션 적용
        angle = self.angle_var.get()
        intensity = self.intensity_var.get()
        frame = self.detector.apply_lighting_simulation(frame, angle, intensity)
        
        # 편광 필터 적용
        if self.polarizer_var.get():
            polarizer_angle = self.polarizer_angle_var.get()
            frame = self.detector.apply_polarizer_effect(frame, polarizer_angle)
        
        # 스크래치 검사
        if self.detector.scratch_detection_active:
            scratches = self.detector.detect_scratches(frame)
            frame = self.detector.draw_scratch_analysis(frame, scratches)
            
            # 결과 업데이트
            severity, score = self.detector.analyze_scratch_severity(scratches)
            self.update_results(severity, score, len(scratches))
        
        # 화면에 표시
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(frame_pil)
        
        self.camera_label.config(image=frame_tk)
        self.camera_label.image = frame_tk
        
        # 다음 프레임 업데이트
        self.root.after(33, self.update_camera_display)  # 30 FPS
    
    def update_results(self, severity, score, count):
        """검사 결과 업데이트"""
        result_text = f"스크래치 검사 결과:\n"
        result_text += f"심각도: {severity}\n"
        result_text += f"점수: {score}/100\n"
        result_text += f"스크래치 개수: {count}개\n"
        result_text += f"시간: {time.strftime('%H:%M:%S')}\n"
        result_text += "-" * 30 + "\n"
        
        self.result_text.insert(tk.END, result_text)
        self.result_text.see(tk.END)
    
    def run(self):
        """GUI 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    # 필요한 라이브러리 import
    try:
        from PIL import Image, ImageTk
        app = ScratchInspectionGUI()
        app.run()
    except ImportError:
        print("PIL 라이브러리가 필요합니다: pip install Pillow")
