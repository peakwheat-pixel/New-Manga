---
license: other
library_name: ultralytics
pipeline_tag: image-segmentation
datasets:
- anonimkaq4/synthetic-manga-page-segmentation-sharded
- hal-utokyo/Manga109-s
- MS92/MangaSegmentation
tags:
- yolo
- yolo11
- ultralytics
- instance-segmentation
- manga
- manga109
- comic-analysis
- manga-segmentation
- panel-segmentation
- comic-segmentation
- character-detection
- speech-bubble-detection
---

# Manga Page Element Segmentation

YOLO11m instance-segmentation model for manga pages: characters, panel frames, and speech bubbles.

## What the model recognizes

The model predicts an instance mask, bounding box, class label, and confidence score for every detected object. It has three classes:

| Output label | Meaning | Typical use |
| --- | --- | --- |
| `character` | A visible person or character. | Find people for cropping, composition analysis, or character-aware editing. |
| `frame` | A manga panel/frame. The mask follows the visible panel area or border. | Split a page into panels before reading-order or per-panel analysis. |
| `speech_bubble` | A dialogue/speech balloon. | Send dialogue regions to OCR or exclude them from artwork processing. |

Use the literal labels above when reading `result.names` from Ultralytics. Class IDs are `0: character`, `1: frame`, and `2: speech_bubble`.

**`snapshots/yolo11m_1024_synthetic_mangaseg/best.pt` is the recommended checkpoint.**

## Checkpoints

| Checkpoint | Base model | Training snapshot | Mask mAP50 | Mask mAP50-95 |
| --- | --- | ---: | ---: | ---: |
| `snapshots/yolo11m_1024_synthetic_mangaseg/best.pt` | `yolo11m-seg.pt` | epoch 33 | **0.8689** | **0.6620** |
| `snapshots/yolo11m_1024_b2/manga-yolo11m-seg-validation-best.pt` | `yolo11m-seg.pt` | epoch 15 | 0.8742 | 0.6078 |
| `snapshots/yolo11s_1024_b8/manga-yolo11s-seg-validation-best.pt` | `yolo11s-seg.pt` | epoch 18 | 0.8649 | 0.5895 |

The recommended checkpoint was evaluated at 1024 px on 784 held-out MangaSeg/Manga109-s pages.

| Class | Mask mAP50 | Mask mAP50-95 |
| --- | ---: | ---: |
| `character` | 0.7731 | 0.5829 |
| `frame` | 0.8427 | 0.5164 |
| `speech_bubble` | 0.9908 | 0.8867 |

## Quick start

```bash
pip install ultralytics huggingface_hub
```

```python
from huggingface_hub import hf_hub_download
from ultralytics import YOLO

checkpoint = hf_hub_download(
    repo_id="anonimkaq4/manga-page-element-segmentation",
    filename="snapshots/yolo11m_1024_synthetic_mangaseg/best.pt",
)

model = YOLO(checkpoint)
results = model("manga_page.png", imgsz=1024, conf=0.25)

for result in results:
    print(result.names)  # {0: 'character', 1: 'frame', 2: 'speech_bubble'}
    result.save(filename="prediction.png")
```

Older YOLO11m and YOLO11s snapshots remain available for comparison.

## Usage and license

This model was trained on MangaSeg annotations derived from Manga109-s. This repository does not include or grant rights to the original Manga109-s images or MangaSeg annotations. Review and comply with the MangaSeg, Manga109-s, and Ultralytics licenses before using the underlying datasets, publishing dataset-derived images/results, redistributing this checkpoint, or using it commercially.

If using MangaSeg images or derived visual results, include the credit: **"Copyrighted by Minshan Xie"**.

## Citation

This model was trained using MangaSeg annotations. If you use the model, its training data, or derived results, cite the MangaSeg paper:

```bibtex
@inproceedings{xie2025advancing,
  title={Advancing Manga Analysis: Comprehensive Segmentation Annotations for the Manga109 Dataset},
  author={Xie, Minshan and Lin, Jian and Liu, Hanyuan and Li, Chengze and Wong, Tien-Tsin},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2025}
}
```

Also cite Manga109-s if your work uses or reports results derived from the original Manga109-s pages or layout annotations:

```bibtex
@article{multimedia_aizawa_2020,
  title={Building a Manga Dataset ``Manga109'' with Annotations for Multimedia Applications},
  author={Aizawa, Kiyoharu and Fujimoto, Azuma and Otsubo, Atsushi and Ogawa, Toru and Matsui, Yusuke and Tsubota, Kota and Ikuta, Hikaru},
  journal={IEEE MultiMedia},
  volume={27},
  number={2},
  pages={8--18},
  year={2020},
  doi={10.1109/MMUL.2020.2987895}
}
```
