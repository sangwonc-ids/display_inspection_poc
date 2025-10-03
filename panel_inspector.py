#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
패널 검사 시스템 - 노트북 카메라 기반
Panel Inspection System - Laptop Camera Based
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

class PanelInspector:
    """패널 검사 시스템 메인 클래스"""
    
    def __init__(self):
        self.camera = None
        self.camera_running = False
        self.current_frame = None
        self.display_guide = None
        self.inspection_results = {}
        self.display_types = {
            "16:9 (1920x1080)": (16, 9),
            "16:10 (1920x1200)": (16, 10),
            "4:3 (1024x768)": (4, 3),
            "21:9 (2560x1080)": (21, 9),
            "1:1 (1024x1024)": (1, 1),
            "사용자 정의": None
        }
        self.selected_display_type = "16:9 (1920x1080)"
        self.guide_alpha = 0.3
        self.setup_ui()
        
    def setup_ui(self):
        """사용자 인터페이스 설정"""
        self.root = tk.Tk()
        self.root.title("패널 검사 시스템 - 실시간 검사")
        self.root.geometry("1400x900")
        
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
        
        # 디스플레이 타입 선택
        display_frame = ttk.Frame(control_frame)
        display_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(display_frame, text="디스플레이 타입:").pack(side=tk.LEFT)
        self.display_var = tk.StringVar(value=self.selected_display_type)
        display_combo = ttk.Combobox(display_frame, textvariable=self.display_var, 
                                   values=list(self.display_types.keys()), width=20)
        display_combo.pack(side=tk.LEFT, padx=5)
        display_combo.bind('<<ComboboxSelected>>', self.on_display_type_changed)
        
        # 검사 제어
        inspect_frame = ttk.Frame(control_frame)
        inspect_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(inspect_frame, text="검사 시작", 
                  command=self.start_inspection).pack(side=tk.LEFT, padx=2)
        ttk.Button(inspect_frame, text="검사 중지", 
                  command=self.stop_inspection).pack(side=tk.LEFT, padx=2)
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
        
        # 검사 상태
        status_frame = ttk.LabelFrame(right_frame, text="검사 상태")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="대기 중...")
        self.status_label.pack(padx=10, pady=5)
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
        # 검사 결과
        result_frame = ttk.LabelFrame(right_frame, text="검사 결과")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 결과 텍스트
        self.result_text = tk.Text(result_frame, height=15, wrap=tk.WORD)
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
        self.inspection_thread = None
        
    def on_display_type_changed(self, event=None):
        """디스플레이 타입 변경 처리"""
        self.selected_display_type = self.display_var.get()
        self.log_result(f"디스플레이 타입 변경: {self.selected_display_type}")
        
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
            # 가이드 박스 그리기
            display_frame = self.draw_display_guide(frame)
            
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
    
    def draw_display_guide(self, frame):
        """디스플레이 가이드 박스 그리기"""
        if self.selected_display_type not in self.display_types:
            return frame
        
        height, width = frame.shape[:2]
        display_ratio = self.display_types[self.selected_display_type]
        
        if display_ratio is None:  # 사용자 정의
            return frame
        
        ratio_w, ratio_h = display_ratio
        
        # 화면 중앙에 가이드 박스 그리기
        center_x, center_y = width // 2, height // 2
        
        # 가이드 박스 크기 계산 (화면의 80% 사용)
        max_width = int(width * 0.8)
        max_height = int(height * 0.8)
        
        # 비율에 맞는 크기 계산
        if max_width / ratio_w < max_height / ratio_h:
            guide_width = max_width
            guide_height = int(max_width * ratio_h / ratio_w)
        else:
            guide_height = max_height
            guide_width = int(max_height * ratio_w / ratio_h)
        
        # 가이드 박스 좌표
        x1 = center_x - guide_width // 2
        y1 = center_y - guide_height // 2
        x2 = center_x + guide_width // 2
        y2 = center_y + guide_height // 2
        
        # 가이드 박스 그리기
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 3)
        
        # 모서리 마커
        corner_size = 20
        cv2.line(overlay, (x1, y1), (x1 + corner_size, y1), (0, 255, 0), 5)
        cv2.line(overlay, (x1, y1), (x1, y1 + corner_size), (0, 255, 0), 5)
        cv2.line(overlay, (x2, y1), (x2 - corner_size, y1), (0, 255, 0), 5)
        cv2.line(overlay, (x2, y1), (x2, y1 + corner_size), (0, 255, 0), 5)
        cv2.line(overlay, (x1, y2), (x1 + corner_size, y2), (0, 255, 0), 5)
        cv2.line(overlay, (x1, y2), (x1, y2 - corner_size), (0, 255, 0), 5)
        cv2.line(overlay, (x2, y2), (x2 - corner_size, y2), (0, 255, 0), 5)
        cv2.line(overlay, (x2, y2), (x2, y2 - corner_size), (0, 255, 0), 5)
        
        # 비율 텍스트
        cv2.putText(overlay, f"{ratio_w}:{ratio_h}", (x1, y1 - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 알파 블렌딩
        cv2.addWeighted(overlay, self.guide_alpha, frame, 1 - self.guide_alpha, 0, frame)
        
        return frame
    
    def start_inspection(self):
        """검사 시작"""
        if not self.camera_running:
            messagebox.showwarning("경고", "먼저 카메라를 시작하세요.")
            return
        
        if self.inspection_running:
            messagebox.showwarning("경고", "검사가 이미 실행 중입니다.")
            return
        
        self.inspection_running = True
        self.progress.start()
        self.status_label.configure(text="검사 중...")
        
        # 검사 스레드 시작
        self.inspection_thread = threading.Thread(target=self.inspection_loop, daemon=True)
        self.inspection_thread.start()
        
        self.log_result("검사가 시작되었습니다.")
    
    def stop_inspection(self):
        """검사 중지"""
        self.inspection_running = False
        self.progress.stop()
        self.status_label.configure(text="검사 중지됨")
        self.log_result("검사가 중지되었습니다.")
    
    def inspection_loop(self):
        """검사 루프"""
        while self.inspection_running and self.camera_running:
            try:
                if self.current_frame is not None:
                    # 검사 실행
                    results = self.perform_inspection(self.current_frame)
                    self.update_inspection_results(results)
                
                time.sleep(1)  # 1초마다 검사
                
            except Exception as e:
                self.log_result(f"검사 루프 오류: {str(e)}")
                break
    
    def perform_inspection(self, frame):
        """실제 검사 수행"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'display_type': self.selected_display_type,
            'defects': [],
            'quality_score': 0
        }
        
        try:
            # 1. 디스플레이 영역 감지
            display_region = self.detect_display_region(frame)
            if display_region is None:
                results['defects'].append("디스플레이 영역을 찾을 수 없습니다.")
                return results
            
            # 2. 스크래치 감지
            scratches = self.detect_scratches(display_region)
            results['defects'].extend(scratches)
            
            # 3. 데드 픽셀 감지
            dead_pixels = self.detect_dead_pixels(display_region)
            results['defects'].extend(dead_pixels)
            
            # 4. 색상 균일성 검사
            color_issues = self.check_color_uniformity(display_region)
            results['defects'].extend(color_issues)
            
            # 5. 품질 점수 계산
            results['quality_score'] = self.calculate_quality_score(results)
            
        except Exception as e:
            results['defects'].append(f"검사 중 오류: {str(e)}")
        
        return results
    
    def detect_display_region(self, frame):
        """디스플레이 영역 감지"""
        # 간단한 구현 - 실제로는 더 정교한 알고리즘 필요
        height, width = frame.shape[:2]
        
        # 가이드 박스 영역 반환
        center_x, center_y = width // 2, height // 2
        region_width = int(width * 0.6)
        region_height = int(height * 0.6)
        
        x1 = center_x - region_width // 2
        y1 = center_y - region_height // 2
        x2 = center_x + region_width // 2
        y2 = center_y + region_height // 2
        
        return frame[y1:y2, x1:x2]
    
    def detect_scratches(self, region):
        """스크래치 감지"""
        scratches = []
        
        try:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=30, maxLineGap=10)
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    if length > 20:
                        scratches.append(f"스크래치 감지: 길이 {length:.1f}px")
            
        except Exception as e:
            scratches.append(f"스크래치 감지 오류: {str(e)}")
        
        return scratches
    
    def detect_dead_pixels(self, region):
        """데드 픽셀 감지"""
        dead_pixels = []
        
        try:
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # 매우 어두운 픽셀 찾기
            dark_pixels = np.where(gray < 30)
            if len(dark_pixels[0]) > 10:
                dead_pixels.append(f"데드 픽셀 {len(dark_pixels[0])}개 감지")
            
        except Exception as e:
            dead_pixels.append(f"데드 픽셀 감지 오류: {str(e)}")
        
        return dead_pixels
    
    def check_color_uniformity(self, region):
        """색상 균일성 검사"""
        color_issues = []
        
        try:
            # 각 채널의 표준편차 계산
            b, g, r = cv2.split(region)
            std_b = np.std(b)
            std_g = np.std(g)
            std_r = np.std(r)
            
            if std_b > 50 or std_g > 50 or std_r > 50:
                color_issues.append(f"색상 불균일성 감지 (B:{std_b:.1f}, G:{std_g:.1f}, R:{std_r:.1f})")
            
        except Exception as e:
            color_issues.append(f"색상 균일성 검사 오류: {str(e)}")
        
        return color_issues
    
    def calculate_quality_score(self, results):
        """품질 점수 계산"""
        score = 100
        
        # 결함별 감점
        for defect in results['defects']:
            if "스크래치" in defect:
                score -= 10
            elif "데드 픽셀" in defect:
                score -= 15
            elif "색상 불균일성" in defect:
                score -= 20
            elif "오류" in defect:
                score -= 30
        
        return max(0, score)
    
    def update_inspection_results(self, results):
        """검사 결과 업데이트"""
        self.inspection_results = results
        
        # 품질 점수 업데이트
        quality_score = results['quality_score']
        self.quality_label.configure(text=f"품질 점수: {quality_score}/100")
        
        # 결과 텍스트 업데이트
        self.result_text.delete(1.0, tk.END)
        
        result_text = f"검사 시간: {results['timestamp']}\n"
        result_text += f"디스플레이 타입: {results['display_type']}\n"
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
    
    def save_results(self):
        """결과 저장"""
        if not self.inspection_results:
            messagebox.showwarning("경고", "저장할 결과가 없습니다.")
            return
        
        try:
            from tkinter import filedialog
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
    app = PanelInspector()
    app.run()

if __name__ == "__main__":
    main()
