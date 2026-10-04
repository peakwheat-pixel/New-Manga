---
license: mit
tags:
  - yolo
  - instance-segmentation
  - manga
  - text-detection
  - onnx
---

# YOLO11s Manga Segmentation Model

Fine-tuned YOLO11s-seg model optimized for comic book and manga processing.

## Classes
- **0:** bubble
- **1:** panel
- **2:** sfx
- **3:** text

## Input Size & Preprocessing
This model was trained on **1024px inputs using rectangular training (`rect=True`)**. 

To get optimal segmentation and bounding box accuracy during inference, input images should be preprocessed following these rules:
1. **Resize:** Scale the longest edge of the image to **1024px** while preserving the original aspect ratio.
2. **Padding:** Pad the resulting resized image to the closest multiple of the model's stride (**32**), using a neutral gray fill (`[114, 114, 114]`).