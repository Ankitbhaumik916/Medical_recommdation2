# Architecture Overview

## System Components

### 1. Frontend Layer (Streamlit)
- **Multi-page Application**
  - Authentication Pages (Login, Signup)
  - Dashboard
  - Disease Prediction Interface
  - Medicine Recommendation Interface
  - Analytics Dashboard
  - Admin Panel
  - User Profile Management

### 2. Authentication & Security Layer
- **User Authentication** (auth.py)
  - JWT token generation and validation
  - Password hashing and verification
  - Session management
  - Role-based access control (Admin, User)

### 3. ML/DL Models Layer (models.py)
- **Disease Prediction Models**
  - Random Forest Classifier
  - Gradient Boosting Classifier
  - Logistic Regression
  - Support Vector Machines (SVM)
  - K-Nearest Neighbors (KNN)
  - Ensemble Methods
  - Neural Networks (TensorFlow)

- **Medicine Recommendation Engines**
  - Content-Based Filtering
  - Collaborative Filtering (Surprise library)
  - Hybrid Approaches

- **Analytics & Insights**
  - User statistics
  - Disease trends
  - Medicine effectiveness metrics

### 4. Data Processing & Utilities Layer (utils.py)
- Data cleaning and preprocessing
- Feature engineering
- Data validation
- Utility functions

### 5. Data Storage Layer
- **SQLite Database** - User data, activity logs
- **CSV Files** - Disease-symptom mapping, drug information
- **Caching** - Session state, temporary data

## Data Flow Diagram

```
┌─────────────────┐
│  User Input     │ (Streamlit Pages)
│  - Symptoms     │
│  - Demographics │
│  - Medical Hx   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Input Validation & Auth    │ (auth.py)
│  - JWT verification         │
│  - Permission check         │
└────────┬────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  Data Preprocessing            │ (utils.py)
│  - Cleaning                    │
│  - Feature Engineering         │
│  - Encoding                    │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  ML Model Processing           │ (models.py)
│  - Feature transformation      │
│  - Model inference             │
│  - Post-processing             │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  Result Formatting             │
│  - Predictions                 │
│  - Recommendations             │
│  - Confidence scores           │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  Visualization & Output        │ (Streamlit)
│  - Charts                      │
│  - Tables                      │
│  - Recommendations             │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  Data Persistence              │
│  - User data (SQLite)          │
│  - Activity logs               │
│  - User feedback               │
└────────────────────────────────┘
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    age INTEGER,
    gender TEXT,
    blood_group TEXT,
    allergies TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    is_admin INTEGER DEFAULT 0
);
```

### User Activity Logs Table
```sql
CREATE TABLE user_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### User Preferences Table
```sql
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    preference_key TEXT,
    preference_value TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Model Training Pipeline

### Training Data
- Source: Disease-Symptom dataset (dataset.csv)
- Size: Typically 1000+ records
- Features: Symptoms, Demographics, Health Metrics

### Preprocessing Steps
1. Data Cleaning (handle missing values)
2. Categorical Encoding (LabelEncoder)
3. Feature Scaling (StandardScaler)
4. Feature Selection
5. Train-Test Split (80-20)

### Model Training
1. Hyperparameter Tuning (GridSearchCV)
2. Cross-validation
3. Model selection based on accuracy
4. Feature importance analysis

### Model Evaluation
- Accuracy Score
- Precision, Recall, F1-Score
- Confusion Matrix
- Classification Report

### Model Persistence
- Saved using joblib
- Includes scalers and encoders
- Version control for model updates

## Recommendation Algorithm

### Content-Based Filtering
```
1. Extract disease features
2. Extract medicine features
3. Calculate similarity (TF-IDF + Cosine)
4. Rank medicines by similarity
5. Filter by user constraints
6. Return top N recommendations
```

### Collaborative Filtering
```
1. Build user-medicine interaction matrix
2. Find similar users (SVD)
3. Get recommendations from similar users
4. Rank by relevance
5. Return top N recommendations
```

### Hybrid Approach
```
Combine content-based + collaborative results
Weight by user preference patterns
Apply medicine safety filters
Return final recommendations
```

## Scalability Considerations

### Current Limitations
- Single-instance deployment
- SQLite (not suitable for 1000+ concurrent users)
- All models loaded in memory

### Future Improvements
- PostgreSQL database
- Redis caching layer
- Model serving (TensorFlow Serving)
- API layer (FastAPI)
- Load balancing
- Microservices architecture

## Security Measures

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based access control
3. **Data Protection**: Password hashing (bcrypt)
4. **Input Validation**: Sanitization and type checking
5. **HTTPS**: In production
6. **Database**: Parameterized queries to prevent SQL injection

## Performance Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Prediction Latency | <2s | <500ms |
| Recommendation Latency | <3s | <1s |
| Database Query Time | <100ms | <50ms |
| Model Accuracy | 85-92% | >95% |
| Concurrent Users | 50+ | 1000+ |

## Technology Decisions & Rationale

| Component | Choice | Why |
|-----------|--------|-----|
| Frontend | Streamlit | Rapid development, data viz |
| Backend | Python | ML libraries, quick prototyping |
| Database | SQLite | Development simplicity |
| ML | scikit-learn | Proven, efficient for tabular data |
| DL | TensorFlow | Flexible, production-ready |
| Recommendations | Surprise | Purpose-built for CF |
| Deployment | Streamlit Cloud | Easy hosting |

## Future Architecture Evolution

```
Current: Monolithic Streamlit App
                ↓
Phase 1: Separate Backend API (FastAPI)
                ↓
Phase 2: Microservices (Prediction, Recommendation, Analytics)
                ↓
Phase 3: Distributed ML (Kubernetes)
                ↓
Phase 4: Real-time Processing (Kafka, Spark)
```
