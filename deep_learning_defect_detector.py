#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
딥러닝 기반 불량 픽셀 탐지 시스템
Deep Learning Based Defect Pixel Detection System
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from PIL import Image
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import json

class UNet(nn.Module):
    """U-Net 아키텍처 for 불량 픽셀 탐지"""
    
    def __init__(self, in_channels=3, out_channels=1):
        super(UNet, self).__init__()
        
        # Encoder (다운샘플링)
        self.enc1 = self.conv_block(in_channels, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)
        self.enc4 = self.conv_block(256, 512)
        
        # Bottleneck
        self.bottleneck = self.conv_block(512, 1024)
        
        # Decoder (업샘플링)
        self.upconv4 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.dec4 = self.conv_block(1024, 512)
        
        self.upconv3 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.dec3 = self.conv_block(512, 256)
        
        self.upconv2 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.dec2 = self.conv_block(256, 128)
        
        self.upconv1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.dec1 = self.conv_block(128, 64)
        
        # Final layer
        self.final = nn.Conv2d(64, out_channels, kernel_size=1)
        
    def conv_block(self, in_channels, out_channels):
        """Convolution block"""
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        enc2 = self.enc2(F.max_pool2d(enc1, 2))
        enc3 = self.enc3(F.max_pool2d(enc2, 2))
        enc4 = self.enc4(F.max_pool2d(enc3, 2))
        
        # Bottleneck
        bottleneck = self.bottleneck(F.max_pool2d(enc4, 2))
        
        # Decoder
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat((dec4, enc4), dim=1)
        dec4 = self.dec4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat((dec3, enc3), dim=1)
        dec3 = self.dec3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.dec2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.dec1(dec1)
        
        # Final layer
        output = self.final(dec1)
        return torch.sigmoid(output)

class DefectDataset(Dataset):
    """불량 픽셀 데이터셋"""
    
    def __init__(self, image_paths, mask_paths, transform=None):
        self.image_paths = image_paths
        self.mask_paths = mask_paths
        self.transform = transform
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        # 이미지 로드
        image = Image.open(self.image_paths[idx]).convert('RGB')
        mask = Image.open(self.mask_paths[idx]).convert('L')
        
        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)
        
        return image, mask

class DeepLearningDefectDetector:
    """딥러닝 기반 불량 픽셀 탐지 시스템"""
    
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.camera = None
        self.camera_running = False
        self.detection_active = False
        
        # 전처리 설정
        self.transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 설정"""
        self.root = tk.Tk()
        self.root.title("딥러닝 불량 픽셀 탐지 시스템")
        self.root.geometry("1400x900")
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 카메라 화면
        camera_frame = ttk.LabelFrame(main_frame, text="카메라 화면")
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # 제어 패널
        control_frame = ttk.LabelFrame(main_frame, text="딥러닝 제어")
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 모델 제어
        model_control = ttk.LabelFrame(control_frame, text="모델 제어")
        model_control.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(model_control, text="모델 로드", 
                  command=self.load_model).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(model_control, text="모델 훈련", 
                  command=self.train_model).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(model_control, text="모델 저장", 
                  command=self.save_model).pack(fill=tk.X, padx=5, pady=5)
        
        # 카메라 제어
        camera_control = ttk.LabelFrame(control_frame, text="카메라 제어")
        camera_control.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(camera_control, text="카메라 시작", 
                  command=self.start_camera).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(camera_control, text="카메라 중지", 
                  command=self.stop_camera).pack(fill=tk.X, padx=5, pady=5)
        
        # 탐지 제어
        detection_control = ttk.LabelFrame(control_frame, text="탐지 제어")
        detection_control.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(detection_control, text="불량 픽셀 탐지 시작", 
                  command=self.start_detection).pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(detection_control, text="탐지 중지", 
                  command=self.stop_detection).pack(fill=tk.X, padx=5, pady=5)
        
        # 결과 표시
        result_frame = ttk.LabelFrame(control_frame, text="탐지 결과")
        result_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.result_text = tk.Text(result_frame, height=10, width=30)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # 모델 상태
        status_frame = ttk.LabelFrame(control_frame, text="모델 상태")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="모델 미로드")
        self.status_label.pack(pady=5)
        
        # 종료 버튼
        ttk.Button(control_frame, text="종료", 
                  command=self.on_closing).pack(fill=tk.X, padx=5, pady=5)
    
    def load_model(self):
        """모델 로드"""
        try:
            # U-Net 모델 초기화
            self.model = UNet(in_channels=3, out_channels=1)
            self.model.to(self.device)
            self.model.eval()
            
            # 사전 훈련된 가중치 로드 (있는 경우)
            model_path = filedialog.askopenfilename(
                title="모델 파일 선택",
                filetypes=[("PyTorch files", "*.pth"), ("All files", "*.*")]
            )
            
            if model_path:
                checkpoint = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.log_result("모델이 성공적으로 로드되었습니다")
                self.status_label.config(text="모델 로드됨")
            else:
                self.log_result("새 모델이 초기화되었습니다")
                self.status_label.config(text="새 모델")
                
        except Exception as e:
            self.log_result(f"모델 로드 오류: {str(e)}")
            messagebox.showerror("오류", f"모델 로드 실패: {str(e)}")
    
    def train_model(self):
        """모델 훈련"""
        try:
            if not self.model:
                self.model = UNet(in_channels=3, out_channels=1)
                self.model.to(self.device)
            
            # 훈련 데이터 경로 선택
            data_path = filedialog.askdirectory(title="훈련 데이터 폴더 선택")
            if not data_path:
                return
            
            # 데이터셋 생성
            image_paths, mask_paths = self.prepare_dataset(data_path)
            if not image_paths:
                messagebox.showerror("오류", "훈련 데이터를 찾을 수 없습니다")
                return
            
            # 데이터로더 생성
            dataset = DefectDataset(image_paths, mask_paths, self.transform)
            dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
            
            # 손실 함수 및 옵티마이저
            criterion = nn.BCELoss()
            optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
            
            # 훈련 시작
            self.log_result("모델 훈련을 시작합니다...")
            self.status_label.config(text="훈련 중...")
            
            # 훈련 루프 (간단한 예시)
            for epoch in range(10):  # 10 에포크
                self.model.train()
                total_loss = 0
                
                for batch_idx, (images, masks) in enumerate(dataloader):
                    images, masks = images.to(self.device), masks.to(self.device)
                    
                    optimizer.zero_grad()
                    outputs = self.model(images)
                    loss = criterion(outputs, masks)
                    loss.backward()
                    optimizer.step()
                    
                    total_loss += loss.item()
                
                self.log_result(f"Epoch {epoch+1}/10, Loss: {total_loss/len(dataloader):.4f}")
            
            self.log_result("모델 훈련이 완료되었습니다")
            self.status_label.config(text="훈련 완료")
            
        except Exception as e:
            self.log_result(f"훈련 오류: {str(e)}")
            messagebox.showerror("오류", f"모델 훈련 실패: {str(e)}")
    
    def save_model(self):
        """모델 저장"""
        if not self.model:
            messagebox.showerror("오류", "저장할 모델이 없습니다")
            return
        
        try:
            save_path = filedialog.asksaveasfilename(
                title="모델 저장",
                defaultextension=".pth",
                filetypes=[("PyTorch files", "*.pth"), ("All files", "*.*")]
            )
            
            if save_path:
                torch.save({
                    'model_state_dict': self.model.state_dict(),
                    'model_architecture': 'UNet'
                }, save_path)
                self.log_result(f"모델이 저장되었습니다: {save_path}")
                
        except Exception as e:
            self.log_result(f"모델 저장 오류: {str(e)}")
            messagebox.showerror("오류", f"모델 저장 실패: {str(e)}")
    
    def prepare_dataset(self, data_path):
        """데이터셋 준비"""
        image_paths = []
        mask_paths = []
        
        # 이미지 파일 찾기
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(root, file)
                    mask_path = image_path.replace('images', 'masks').replace('.jpg', '_mask.png')
                    
                    if os.path.exists(mask_path):
                        image_paths.append(image_path)
                        mask_paths.append(mask_path)
        
        return image_paths, mask_paths
    
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
            self.update_camera_display()
            self.log_result("카메라가 시작되었습니다")
            
        except Exception as e:
            self.log_result(f"카메라 시작 오류: {str(e)}")
            messagebox.showerror("오류", f"카메라 시작 실패: {str(e)}")
    
    def stop_camera(self):
        """카메라 중지"""
        self.camera_running = False
        if self.camera:
            self.camera.release()
        self.log_result("카메라가 중지되었습니다")
    
    def start_detection(self):
        """불량 픽셀 탐지 시작"""
        if not self.camera_running:
            messagebox.showerror("오류", "먼저 카메라를 시작하세요")
            return
        
        if not self.model:
            messagebox.showerror("오류", "먼저 모델을 로드하세요")
            return
        
        self.detection_active = True
        self.log_result("불량 픽셀 탐지가 시작되었습니다")
    
    def stop_detection(self):
        """불량 픽셀 탐지 중지"""
        self.detection_active = False
        self.log_result("불량 픽셀 탐지가 중지되었습니다")
    
    def detect_defects(self, frame):
        """불량 픽셀 탐지"""
        if not self.model:
            return frame
        
        try:
            # 이미지 전처리
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # 모델 추론
            with torch.no_grad():
                output = self.model(input_tensor)
                output = output.squeeze().cpu().numpy()
            
            # 결과 시각화
            result_frame = frame.copy()
            
            # 불량 픽셀 마스크 생성
            mask = (output > 0.5).astype(np.uint8) * 255
            
            # 컨투어 찾기
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 불량 픽셀 표시
            for i, contour in enumerate(contours):
                if cv2.contourArea(contour) > 10:  # 최소 면적
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(result_frame, f"D{i+1}", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 결과 텍스트
            defect_count = len(contours)
            cv2.putText(result_frame, f"불량 픽셀: {defect_count}개", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            return result_frame
            
        except Exception as e:
            self.log_result(f"탐지 오류: {str(e)}")
            return frame
    
    def update_camera_display(self):
        """카메라 화면 업데이트"""
        if not self.camera_running:
            return
        
        ret, frame = self.camera.read()
        if not ret:
            return
        
        # 불량 픽셀 탐지
        if self.detection_active:
            frame = self.detect_defects(frame)
        
        # 화면에 표시
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(frame_pil)
        
        self.camera_label.config(image=frame_tk)
        self.camera_label.image = frame_tk
        
        # 다음 프레임 업데이트
        self.root.after(33, self.update_camera_display)  # 30 FPS
    
    def log_result(self, message):
        """결과 로그"""
        timestamp = time.strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        self.result_text.insert(tk.END, log_message)
        self.result_text.see(tk.END)
    
    def on_closing(self):
        """애플리케이션 종료"""
        self.camera_running = False
        if self.camera:
            self.camera.release()
        self.root.destroy()
    
    def run(self):
        """GUI 실행"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """메인 함수"""
    app = DeepLearningDefectDetector()
    app.run()

if __name__ == "__main__":
    main()
