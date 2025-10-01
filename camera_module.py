#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카메라 모듈
Camera Module

USB 카메라 연결 및 실시간 영상 캡처
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class CameraModule:
    def __init__(self, camera_index: int = 0):
        """
        카메라 모듈 초기화
        
        Args:
            camera_index: 카메라 인덱스 (기본값: 0)
        """
        self.camera_index = camera_index
        self.cap = None
        self.is_connected_flag = False
        self.current_frame = None
        self.resolution = (1920, 1080)
        self.fps = 30
        
    def connect(self) -> bool:
        """
        카메라 연결
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                return False
                
            # 카메라 설정
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # 자동 노출 설정
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 수동 노출
            self.cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # 노출값 설정
            
            # 자동 초점 설정
            self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # 수동 초점
            
            self.is_connected_flag = True
            return True
            
        except Exception as e:
            print(f"카메라 연결 오류: {e}")
            return False
            
    def disconnect(self):
        """카메라 연결 해제"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected_flag = False
        
    def is_connected(self) -> bool:
        """
        카메라 연결 상태 확인
        
        Returns:
            bool: 연결 상태
        """
        return self.is_connected_flag and self.cap is not None and self.cap.isOpened()
        
    def get_frame(self, convert_to_rgb: bool = True) -> Optional[np.ndarray]:
        """
        현재 프레임 가져오기
        
        Args:
            convert_to_rgb: BGR을 RGB로 변환할지 여부
            
        Returns:
            np.ndarray: 현재 프레임 (RGB 또는 BGR 형식)
        """
        if not self.is_connected():
            return None
            
        try:
            ret, frame = self.cap.read()
            if ret:
                # BGR을 RGB로 변환 (OpenCV는 BGR 형식 사용)
                if convert_to_rgb:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.current_frame = frame
                return frame
            else:
                return None
        except Exception as e:
            print(f"프레임 캡처 오류: {e}")
            return None
            
    def set_resolution(self, width: int, height: int) -> bool:
        """
        해상도 설정
        
        Args:
            width: 가로 해상도
            height: 세로 해상도
            
        Returns:
            bool: 설정 성공 여부
        """
        if not self.is_connected():
            return False
            
        try:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.resolution = (width, height)
            return True
        except Exception as e:
            print(f"해상도 설정 오류: {e}")
            return False
            
    def set_fps(self, fps: int) -> bool:
        """
        FPS 설정
        
        Args:
            fps: 프레임 레이트
            
        Returns:
            bool: 설정 성공 여부
        """
        if not self.is_connected():
            return False
            
        try:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            self.fps = fps
            return True
        except Exception as e:
            print(f"FPS 설정 오류: {e}")
            return False
            
    def set_exposure(self, exposure: float) -> bool:
        """
        노출 설정
        
        Args:
            exposure: 노출값 (-13 ~ 1)
            
        Returns:
            bool: 설정 성공 여부
        """
        if not self.is_connected():
            return False
            
        try:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure)
            return True
        except Exception as e:
            print(f"노출 설정 오류: {e}")
            return False
            
    def set_brightness(self, brightness: float) -> bool:
        """
        밝기 설정
        
        Args:
            brightness: 밝기값 (0 ~ 100)
            
        Returns:
            bool: 설정 성공 여부
        """
        if not self.is_connected():
            return False
            
        try:
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
            return True
        except Exception as e:
            print(f"밝기 설정 오류: {e}")
            return False
            
    def set_contrast(self, contrast: float) -> bool:
        """
        대비 설정
        
        Args:
            contrast: 대비값 (0 ~ 100)
            
        Returns:
            bool: 설정 성공 여부
        """
        if not self.is_connected():
            return False
            
        try:
            self.cap.set(cv2.CAP_PROP_CONTRAST, contrast)
            return True
        except Exception as e:
            print(f"대비 설정 오류: {e}")
            return False
            
    def get_camera_info(self) -> dict:
        """
        카메라 정보 가져오기
        
        Returns:
            dict: 카메라 정보
        """
        if not self.is_connected():
            return {}
            
        try:
            info = {
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                'exposure': self.cap.get(cv2.CAP_PROP_EXPOSURE),
                'brightness': self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.cap.get(cv2.CAP_PROP_CONTRAST),
                'gain': self.cap.get(cv2.CAP_PROP_GAIN)
            }
            return info
        except Exception as e:
            print(f"카메라 정보 가져오기 오류: {e}")
            return {}
            
    def capture_image(self, filename: str) -> bool:
        """
        이미지 캡처 및 저장
        
        Args:
            filename: 저장할 파일명
            
        Returns:
            bool: 저장 성공 여부
        """
        if not self.is_connected():
            return False
            
        frame = self.get_frame()
        if frame is not None:
            try:
                cv2.imwrite(filename, frame)
                return True
            except Exception as e:
                print(f"이미지 저장 오류: {e}")
                return False
        return False
        
    def calibrate_camera(self) -> dict:
        """
        카메라 보정
        
        Returns:
            dict: 보정 결과
        """
        if not self.is_connected():
            return {}
            
        # 체스보드 패턴을 이용한 카메라 보정
        # 실제 구현에서는 체스보드 이미지들을 캡처하여 보정
        try:
            # 보정 매트릭스와 왜곡 계수 계산
            # 여기서는 예시로 더미 데이터 반환
            calibration_result = {
                'camera_matrix': np.eye(3),
                'distortion_coefficients': np.zeros(5),
                'rms_error': 0.0,
                'calibrated': True
            }
            return calibration_result
        except Exception as e:
            print(f"카메라 보정 오류: {e}")
            return {'calibrated': False}
            
    def __del__(self):
        """소멸자"""
        self.disconnect()
