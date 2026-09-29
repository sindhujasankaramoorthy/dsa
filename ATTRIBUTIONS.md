# ATTRIBUTIONS & LICENSING NOTICE

## FreshGrade AI — Produce Quality Intelligence Platform

This project incorporates, adapts, and builds upon code, models, and datasets from open-source repositories and public machine learning benchmark datasets.

---

### 1. Kaggle Fruits Fresh and Rotten Dataset
- **Dataset Link**: [https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification](https://www.kaggle.com/datasets/sriramr/fruits-fresh-and-rotten-for-classification)
- **Author/Creator**: Sriram Reddy K. (`sriramr`)
- **Dataset Structure**: ~13,500 produce images categorized across 6 benchmark classes:
  - `freshapples` (Fresh Apple)
  - `freshoranges` (Fresh Orange)
  - `freshbananas` (Fresh Banana)
  - `rottenapples` (Rotten Apple)
  - `rottenoranges` (Rotten Orange)
  - `rottenbananas` (Rotten Banana)
- **Usage**: Integrated as a primary training benchmark dataset for fruit quality classification.

---

### 2. VegQual Dataset & Research
- **Repository**: [https://github.com/tarekrahamn/VegQual](https://github.com/tarekrahamn/VegQual)
- **Paper**: *A Multiclass Dataset for Real-Time Detection of Fresh and Defective Vegetables Using Deep Learning* (Nature Scientific Data / Figshare)
- **Authors**: Tarek Rahman et al.
- **License**: MIT License
- **Dataset Structure**: 4,736 annotated produce images across 14 classes for 7 vegetables:
  - Tomato (`Fresh` / `Defective`)
  - Potato (`Fresh` / `Defective`)
  - Bitter Gourd (`Fresh` / `Defective`)
  - Pointed Gourd (`Fresh` / `Defective`)
  - Onion (`Fresh` / `Defective`)
  - Capsicum (`Fresh` / `Defective`)
  - Brinjal (`Fresh` / `Defective`)

---

### 3. Fruit Quality Detector for SMS
- **Repository**: [https://github.com/mohammednafees1007-hub/fruit-quality-detector-for-sms](https://github.com/mohammednafees1007-hub/fruit-quality-detector-for-sms)
- **Author/Maintainer**: Mohammed Nafees (`mohammednafees1007-hub`)
- **Components Reused**:
  - Fruit classification architecture concepts and Keras MobileNetV2 fruit quality classifier (`models/fruit_quality_grader.keras`).
  - Fruit class labels mapping (`quality_classes.json`).
  - OpenCV image decoding and preprocessing routines.

---

### 4. Third-Party Libraries & Dependencies
- **FastAPI** (MIT License) - Web framework and API layer
- **OpenCV** (Apache 2.0 License) - Computer vision and image processing
- **Pillow / PIL** (HPND License) - Image file handling
- **NumPy** (BSD 3-Clause) - Array operations
- **PyMongo** (Apache 2.0) - MongoDB driver
- **Scikit-Learn / SciPy** (BSD License) - Feature extraction and statistical analytics

---

### 5. FreshGrade AI Original Contributions
FreshGrade AI unifies fruit and vegetable quality inspection into a single smartphone-first application, introducing the following original software components:
- **Unified Inference Architecture**: Single API & model abstraction (`ProduceModel`, `QualityModel`, `InferenceService`) supporting both fruits and vegetables dynamically.
- **Image Reliability Layer**: Pre-inspection image quality check validating blur, lighting, brightness, and produce framing before running ML inference.
- **Anatomical Stem & Specular Glare Masking**: Filters green calyx/stem leaves ($35 \le H \le 85$) and specular reflections ($V > 235$) to ensure stem leaves are not misread as surface lesions.
- **Explainable Quality Score & Measured Evidence**: Transparency engine calculating measured rot ratio %, discoloration %, lesion texture density %, colour score, and surface smoothness.
- **Batch-Level Inspection & Aggregation Engine**: Multi-image processing, batch statistical breakdown, defect distribution, and grade donut visualization.
- **Business-Oriented Sorting Recommendation System**: Channel routing guidance (Premium Retail, Standard Retail, Food Processing / Lower-value channels).
- **Quality History & Trend Analytics**: Historical tracking and cross-batch quality trajectory reporting.
- **Smartphone-First B2B SaaS Dashboard**: Unified responsive frontend interface featuring live camera capture, instant grading feedback, demo mode, and admin produce management.
