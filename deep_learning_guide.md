# 딥러닝 불량 픽셀 탐지 가이드

## 🤖 **딥러닝 알고리즘 비교**

### **1. U-Net (추천) ⭐⭐⭐⭐⭐**
**장점:**
- 🎯 **픽셀 단위 정확도**: 불량 픽셀의 정확한 위치 파악
- 🔬 **의료 영상 특화**: 결함 탐지에 최적화
- 📐 **세밀한 분석**: 픽셀 단위 세밀한 분할
- 🏥 **검증된 성능**: 의료 영상에서 검증된 성능

**단점:**
- 🐌 **속도**: 상대적으로 느림
- 💾 **메모리**: 높은 메모리 요구사항

**불량 픽셀 탐지 적합도: ⭐⭐⭐⭐⭐**

### **2. YOLO ⭐⭐☆☆☆**
**장점:**
- ⚡ **실시간 처리**: 매우 빠른 추론 속도
- 🎯 **단일 단계**: Detection과 Classification을 동시에
- 📱 **경량화**: 모바일/임베디드 환경에 적합

**단점:**
- 🔍 **작은 객체**: 픽셀 단위 작은 객체 감지 어려움
- 📏 **해상도**: 고해상도 이미지에서 성능 저하

**불량 픽셀 탐지 적합도: ⭐⭐☆☆☆**

### **3. Faster R-CNN ⭐⭐⭐⭐☆**
**장점:**
- 🎯 **정확도**: 높은 정확도로 작은 객체 감지
- 🔍 **세밀함**: 픽셀 단위 세밀한 분석 가능
- 📊 **성능**: 검증된 2-stage 알고리즘

**단점:**
- 🐌 **속도**: 상대적으로 느린 처리 속도
- 💾 **메모리**: 높은 메모리 사용량

**불량 픽셀 탐지 적합도: ⭐⭐⭐⭐☆**

### **4. Mask R-CNN ⭐⭐⭐⭐☆**
**장점:**
- 🎯 **정확도**: 매우 높은 정확도
- 🔍 **세밀함**: 픽셀 단위 정확한 분할
- 📊 **성능**: 검증된 3-stage 알고리즘

**단점:**
- 🐌 **속도**: 가장 느린 처리 속도
- 💾 **메모리**: 매우 높은 메모리 사용량

**불량 픽셀 탐지 적합도: ⭐⭐⭐⭐☆**

## 🏆 **추천 알고리즘: U-Net**

### **이유:**
1. **픽셀 단위 정확도**: 불량 픽셀의 정확한 위치 파악
2. **의료 영상 특화**: 결함 탐지에 최적화
3. **세밀한 분석**: 픽셀 단위 세밀한 분할
4. **검증된 성능**: 의료 영상에서 검증된 성능

## 🛠️ **구현 방법**

### **1. U-Net 아키텍처**
```python
class UNet(nn.Module):
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
        
        # ... (나머지 decoder layers)
        
        # Final layer
        self.final = nn.Conv2d(64, out_channels, kernel_size=1)
```

### **2. 데이터 전처리**
```python
transform = transforms.Compose([
    transforms.Resize((512, 512)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                       std=[0.229, 0.224, 0.225])
])
```

### **3. 훈련 설정**
```python
# 손실 함수
criterion = nn.BCELoss()

# 옵티마이저
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 학습률 스케줄러
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
```

## 📊 **성능 비교**

### **속도 (FPS)**
- **U-Net**: 15-20 FPS
- **YOLO**: 30-60 FPS
- **Faster R-CNN**: 5-10 FPS
- **Mask R-CNN**: 2-5 FPS

### **정확도 (mIoU)**
- **U-Net**: 0.85-0.95
- **YOLO**: 0.60-0.75
- **Faster R-CNN**: 0.80-0.90
- **Mask R-CNN**: 0.85-0.95

### **메모리 사용량**
- **U-Net**: 4-8 GB
- **YOLO**: 2-4 GB
- **Faster R-CNN**: 6-12 GB
- **Mask R-CNN**: 8-16 GB

## 🎯 **불량 픽셀 탐지 최적화**

### **1. 데이터 증강**
```python
augmentation = transforms.Compose([
    transforms.RandomRotation(10),
    transforms.RandomHorizontalFlip(0.5),
    transforms.RandomVerticalFlip(0.5),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1))
])
```

### **2. 손실 함수 최적화**
```python
# Dice Loss for 불량 픽셀 탐지
def dice_loss(pred, target, smooth=1e-5):
    pred = torch.sigmoid(pred)
    intersection = (pred * target).sum()
    dice = (2. * intersection + smooth) / (pred.sum() + target.sum() + smooth)
    return 1 - dice
```

### **3. 후처리 최적화**
```python
def post_process(mask, min_area=50, min_aspect_ratio=2.0):
    # 노이즈 제거
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # 최소 면적 필터링
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered_contours = [c for c in contours if cv2.contourArea(c) > min_area]
    
    # 종횡비 필터링
    final_contours = []
    for contour in filtered_contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = max(w, h) / min(w, h)
        if aspect_ratio > min_aspect_ratio:
            final_contours.append(contour)
    
    return final_contours
```

## 🚀 **실제 구현 단계**

### **1단계: 데이터 준비**
```bash
# 훈련 데이터 구조
data/
├── images/
│   ├── normal_001.jpg
│   ├── normal_002.jpg
│   └── ...
├── masks/
│   ├── normal_001_mask.png
│   ├── normal_002_mask.png
│   └── ...
└── annotations.json
```

### **2단계: 모델 훈련**
```python
# 훈련 루프
for epoch in range(num_epochs):
    model.train()
    for batch_idx, (images, masks) in enumerate(dataloader):
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, masks)
        loss.backward()
        optimizer.step()
```

### **3단계: 모델 평가**
```python
# 평가 메트릭
def evaluate_model(model, dataloader):
    model.eval()
    total_iou = 0
    total_dice = 0
    
    with torch.no_grad():
        for images, masks in dataloader:
            outputs = model(images)
            iou = calculate_iou(outputs, masks)
            dice = calculate_dice(outputs, masks)
            total_iou += iou
            total_dice += dice
    
    return total_iou / len(dataloader), total_dice / len(dataloader)
```

## 📈 **성능 향상 팁**

### **1. 하이퍼파라미터 튜닝**
- **학습률**: 0.001 → 0.0001
- **배치 크기**: 4 → 8 → 16
- **에포크**: 50 → 100 → 200

### **2. 모델 앙상블**
```python
# 여러 모델의 예측 결합
def ensemble_predict(models, image):
    predictions = []
    for model in models:
        pred = model(image)
        predictions.append(pred)
    
    # 평균 또는 투표
    final_pred = torch.mean(torch.stack(predictions), dim=0)
    return final_pred
```

### **3. 전이 학습**
```python
# 사전 훈련된 모델 사용
pretrained_model = torchvision.models.segmentation.deeplabv3_resnet50(
    pretrained=True, progress=True
)

# 마지막 레이어만 재훈련
for param in pretrained_model.parameters():
    param.requires_grad = False

# 분류기만 재훈련
pretrained_model.classifier = nn.Conv2d(2048, 1, kernel_size=1)
```

## 🎯 **결론**

### **불량 픽셀 탐지에 최적화된 알고리즘:**
1. **U-Net**: 픽셀 단위 정확도, 의료 영상 특화
2. **Faster R-CNN**: 높은 정확도, 작은 객체 감지
3. **Mask R-CNN**: 매우 높은 정확도, 정확한 분할

### **실제 구현 권장사항:**
- **U-Net**을 기본으로 사용
- **전이 학습**으로 성능 향상
- **데이터 증강**으로 일반화 성능 향상
- **앙상블**로 최종 성능 향상

### **성능 목표:**
- **정확도**: 95% 이상
- **속도**: 15-20 FPS
- **메모리**: 4-8 GB
- **신뢰도**: 0.9 이상
