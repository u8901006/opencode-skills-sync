# Calculate Midface Volume Skill

## Overview

This skill provides comprehensive knowledge and implementation guidance for automatic midface region segmentation and volume loss detection using MediaPipe Face Mesh.

## Research Foundation

### Key Literature

1. **Boehm et al., 2021 (Plastic and Reconstructive Surgery)**
   - Longitudinal CT study over 11 years
   - Key data:
     - Superficial fat loss: 11.3% (26.10 cc → 23.15 cc)
     - Deep fat loss: 18.4% (11.01 cc → 8.98 cc)
     - Deep fat loss exceeds superficial

2. **Gosain MRI Study (2005)**
   - High-resolution MRI volumetric analysis
   - Muscle and subcutaneous tissue distribution differences

3. **Lambros Longitudinal Study (2007)**
   - Long-term photo tracking of same individuals
   - 554 citations (high impact)

4. **Berends et al., 2024 (Nature Scientific Reports)**
   - Fully automated landmarking and facial segmentation
   - DiffusionNet for prediction

### Standardized Assessment Scales

#### Merz Aesthetics Scales (Validated Clinical Tools)

| Scale | Range | Application |
|-------|-------|-------------|
| Upper Cheek Fullness Scale | 0-4 | Malar region |
| Lower Cheek Fullness Scale | 0-4 | Lower cheek |
| Infraorbital Hollow Scale | 0-4 | Under-eye area |
| Midface Volume Scale (Medicis) | 0-4 | Overall midface |

#### Scoring Criteria:
- 0: No volume loss
- 1: Mild loss
- 2: Moderate loss
- 3: Noticeable loss
- 4: Severe loss

## MediaPipe Face Mesh Landmark Indices

### Midface Region Definitions

```javascript
const MIDFACE_LANDMARKS = {
  // Upper Cheek (Malar prominence)
  upperCheek: {
    left: [116, 117, 118, 119, 120, 121, 187, 205, 36, 142],
    right: [345, 346, 347, 348, 349, 350, 411, 425, 266, 371]
  },
  
  // Lower Cheek
  lowerCheek: {
    left: [50, 101, 187, 205, 36, 142, 126, 217, 174, 196],
    right: [280, 330, 411, 425, 266, 371, 356, 437, 399, 420]
  },
  
  // Deep Malar Fat
  deepMalar: {
    left: [118, 119, 120, 121, 188, 114, 217, 174],
    right: [347, 348, 349, 350, 412, 339, 437, 399]
  },
  
  // SOOF (Sub-Orbicularis Oculi Fat)
  soof: {
    left: [98, 99, 100, 114, 188, 189, 190, 191, 192, 193],
    right: [327, 328, 329, 339, 412, 413, 414, 415, 416, 417]
  },
  
  // Infraorbital
  infraorbital: {
    left: [98, 99, 100, 101, 102, 113, 225, 224, 223, 222],
    right: [327, 328, 329, 330, 331, 342, 445, 444, 443, 442]
  },
  
  // Nasolabial Fold
  nasolabial: {
    left: [98, 121, 205, 206, 216, 212, 202, 204, 200, 201],
    right: [327, 350, 425, 426, 436, 432, 422, 424, 420, 421]
  },
  
  // Zygomatic Arch
  zygomatic: {
    left: [50, 101, 118, 119, 120, 234, 93, 132],
    right: [280, 330, 347, 348, 349, 454, 323, 361]
  },
  
  // Boundaries
  boundaries: {
    superior: 10,
    inferior: 152,
    lateralLeft: 234,
    lateralRight: 454,
    medial: 1
  }
};
```

## 3D Measurement Algorithms

### Key Algorithms from Literature

| Algorithm | Purpose | Source |
|-----------|---------|--------|
| ICP (Iterative Closest Point) | 3D mesh alignment | Zhao et al., 2017 |
| Coherent Point Drift | Personalized template deformation | Tuin et al., 2020 |
| Best-fit Algorithm | Mesh comparison | Revilla-Leon et al., 2021 |
| RMS Error Calculation | Error assessment | Multiple studies |

### Volume Calculation Methods

1. **Z-Depth Based Estimation**
   - Relative depth from reference point (nose tip)
   - Volume score = avgDepth × areaEstimate

2. **Shoelace Formula for Area**
   - Polygon area calculation
   - 2D projection estimation

3. **3D Volumetric Analysis**
   - Requires 3D scanning (stereophotogrammetry)
   - Accuracy: up to 0.2mm

## Reference Data for Programming

### Normal Values (30-65 years old)
- Total midface fat: ~46.47 cc
- Annual loss rate: Deep ~18%/11 years vs Superficial ~11%/11 years

### Anatomical Regions
```
Midface Regions:
- Malar prominence (superficial/deep)
- Deep fat pads
- SOOF (Sub-Orbicularis Oculi Fat)
- Buccal fat pad
```

### Key Measurement Points
- Inferior orbital rim
- Nasal base
- Tragion
- Mouth corner

## Implementation Checklist

When implementing midface volume detection:

- [ ] Define facial region boundaries using landmarks
- [ ] Implement point-in-polygon detection
- [ ] Calculate relative depth (z-coordinate analysis)
- [ ] Estimate regional volume scores
- [ ] Map to standardized scales (Merz 0-4)
- [ ] Calculate left-right symmetry
- [ ] Generate visualization (masks/heatmaps)
- [ ] Track changes over time

## Related Research Papers

- Carruthers et al., 2012 - Validated assessment scales for midface
- Tower et al., 2020 - Deep cheek fat volumes and midfacial aging
- Ramesh et al., 2021 - Gravity in midfacial aging (3D study)
- Coleman & Grover, 2006 - Anatomy of aging face: volume loss
- Shaw & Kahn, 2007 - Midface bony elements aging (CT study)

## Tools and Libraries

- MediaPipe Face Mesh (468 landmarks)
- TensorFlow.js face-landmarks-detection
- 3DDFA (3D Dense Face Alignment)
- Deep3DFaceRecon
