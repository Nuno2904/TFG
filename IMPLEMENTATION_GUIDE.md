"""
📚 BACKEND ARCHITECTURE IMPLEMENTATION GUIDE

Complete guide explaining the time series prediction backend architecture,
why each component exists, and how to implement them.
"""

# ███████████████████████████████████████████████████████████████████████████
# TABLE OF CONTENTS
# ███████████████████████████████████████████████████████████████████████████

"""
1. ARCHITECTURE OVERVIEW
2. FOLDER STRUCTURE EXPLANATION
3. DATABASE SCHEMA DESIGN
4. COMPONENTS & RESPONSIBILITIES
5. IMPLEMENTATION ROADMAP
6. STEP-BY-STEP IMPLEMENTATION GUIDE
7. TESTING STRATEGY
8. DEPLOYMENT CHECKLIST
"""

# ███████████████████████████████████████████████████████████████████████████
# 1. ARCHITECTURE OVERVIEW
# ███████████████████████████████████████████████████████████████████████████

"""
🎯 ARCHITECTURE OVERVIEW

This backend follows a layered, modular architecture:

    ┌─────────────────────────────────────┐
    │     API LAYER (endpoints/)          │  ← User requests
    │  Handles HTTP requests & responses  │
    ├─────────────────────────────────────┤
    │   SERVICE LAYER (services/)         │  ← Business logic
    │  Orchestrates operations            │
    ├─────────────────────────────────────┤
    │  ML LAYER (ml/) + DB LAYER (db/)   │  ← Data & models
    │  Models, preprocessing, predictions│
    ├─────────────────────────────────────┤
    │   UTILITIES (utils/)                │  ← Helpers
    │  Validation, file handling, errors  │
    └─────────────────────────────────────┘

BENEFITS:
✅ Separation of Concerns: Each layer has one job
✅ Testability: Easy to test each layer independently
✅ Maintainability: Clear structure for future developers
✅ Scalability: Can enhance/add layers without breaking others
✅ Reusability: Services can be used by multiple endpoints

DATA FLOW EXAMPLE: User uploading CSV
────────────────────────────────────────
1. User submits file via POST /api/v1/datasets
2. ENDPOINT (datasets.py) validates request & calls service
3. SERVICE (dataset_service.py) calls helpers:
   - CSVHandler saves file to disk
   - CSVHandler validates structure
   - Extracts metadata
4. SERVICE stores Dataset record in DB
5. ENDPOINT returns DatasetOut response
6. User receives dataset details


DATA FLOW EXAMPLE: Creating Prediction
───────────────────────────────────────
1. User requests POST /api/v1/predictions with dataset & model
2. ENDPOINT validates and calls PredictionService
3. SERVICE orchestrates:
   a) Validates dataset exists
   b) Validates model exists
   c) Creates "pending" Prediction record
   d) Loads CSV using CSVHandler
   e) Creates ML model using ModelFactory
   f) Calls model.fit() with historical data
   g) Calls model.predict() for forecast
   h) Stores results in PredictionResult table
   i) Calculates metrics using MetricsCalculator
   j) Updates Prediction status to "completed"
4. SERVICE returns Prediction with results
5. ENDPOINT returns PredictionDetailOut
6. User receives forecast, graphs, metrics
"""

# ███████████████████████████████████████████████████████████████████████████
# 2. FOLDER STRUCTURE EXPLANATION
# ███████████████████████████████████████████████████████████████████████████

"""
📁 PROJECT STRUCTURE - WHY EACH FOLDER EXISTS

app/
├── core/                    ← CONFIGURATION & CONSTANTS
│   ├── config.py           • Type-safe environment settings
│   ├── constants.py        • App-wide enums (ModelType, Status, etc.)
│   └── enums.py            • Additional enumerations
│   
│   WHAT: Centralized configuration
│   WHY: Single source of truth for settings, prevents typos
│   
├── db/                      ← DATABASE LAYER
│   ├── base.py             • SQLAlchemy engine & DeclarativeBase
│   ├── session.py          • Session management & dependencies
│   └── init_db.py          • Database initialization & seeding
│   
│   WHAT: All database setup
│   WHY: Isolates DB concerns, makes switching DB easy
│   
├── models/                  ← ORM MODELS
│   ├── dataset.py          • Dataset table (uploaded CSV info)
│   ├── prediction.py       • Prediction table (job results)
│   ├── model_config.py     • PredictionModel table (available models)
│   ├── metric.py           • PredictionMetric table (performance metrics)
│   └── __init__.py         • Export all models
│   
│   WHAT: SQLAlchemy ORM definitions
│   WHY: Structured DB access, type safety, relationships
│   
├── schemas/                 ← PYDANTIC VALIDATION
│   ├── dataset.py          • Request/response schemas for datasets
│   ├── prediction.py       • Request/response schemas for predictions
│   └── model_config.py     • Schemas for model information
│   
│   WHAT: Input validation & output contracts
│   WHY: Type safety, auto documentation, error handling
│   
├── services/                ← BUSINESS LOGIC
│   ├── dataset_service.py  • Upload, list, delete datasets
│   ├── prediction_service.py • Create predictions, orchestrate ML
│   ├── csv_handler.py      • CSV parsing, validation, storage
│   ├── model_factory.py    • Create appropriate ML model instances
│   └── __init__.py         • Export all services
│   
│   WHAT: Application business logic
│   WHY: Keeps endpoints lean, reusable logic, easy testing
│   
├── ml/                      ← MACHINE LEARNING
│   ├── models/
│   │   ├── base_model.py   • Abstract base class for all models
│   │   ├── prophet_model.py • Prophet implementation
│   │   ├── arima_model.py  • ARIMA implementation
│   │   └── __init__.py     • Export models
│   ├── preprocessing.py    • Data cleaning & normalization
│   ├── metrics.py          • Statistical metrics (MAE, RMSE, etc.)
│   └── __init__.py         • Export ML modules
│   
│   WHAT: Machine learning implementation
│   WHY: Separated from business logic, easy to add new models
│   
├── utils/                   ← UTILITIES & HELPERS
│   ├── file_handler.py     • File upload/storage operations
│   ├── validators.py       • Custom validation logic
│   ├── exceptions.py       • Custom exception classes
│   └── __init__.py         • Export utilities
│   
│   WHAT: Reusable helper functions
│   WHY: DRY principle, centralized error handling
│   
├── api/                     ← API ENDPOINTS
│   └── v1/
│       ├── endpoints/
│       │   ├── datasets.py      • POST/GET/DELETE /api/v1/datasets
│       │   ├── predictions.py   • POST/GET/DELETE /api/v1/predictions
│       │   ├── models.py        • GET /api/v1/models
│       │   └── __init__.py      • Export endpoints
│       ├── dependencies.py      • Shared endpoint dependencies
│       └── __init__.py          • Combine v1 routers
│   
│   WHAT: HTTP endpoints
│   WHY: Exposes service layer to clients
│   NOTE: Future-proof with v1 prefix (v2, v3 possible)
│   
├── config.py                ← MAIN CONFIG
├── security/                ← EXISTS ALREADY
└── api/v1/                  ← EXISTING (User endpoints)
"""

# ███████████████████████████████████████████████████████████████████████████
# 3. DATABASE SCHEMA DESIGN
# ███████████████████████████████████████████████████████████████████████████

"""
📊 DATABASE SCHEMA - WHY THIS DESIGN

RELATIONSHIP DIAGRAM:
─────────────────────

    ┌─────────┐
    │  User   │ (already exists)
    └────┬────┘
         │ 1:N (user owns datasets)
    ┌────▼──────────┐
    │   Dataset     │ ← CSV files uploaded by users
    │ id, user_id   │
    │ name, path    │
    │ file_info     │
    │ time_range    │
    └────┬──────────┘
         │ 1:N (dataset can have multiple predictions)
    ┌────▼────────────┐      ┌──────────────┐
    │  Prediction     │──────│ PredictionM  │
    │ id, dataset_id  │ N:1  │   odel       │
    │ model_id        │      │ (Prophet,    │
    │ status          │      │  ARIMA, etc.)│
    │ parameters      │      └──────────────┘
    │ results pending │
    │ metrics pending │
    └────┬────┬───────┘
         │    │
         │    └─ 1:N ────┬─────────────────────┐
         │               │   PredictionMetric  │
         │               │ (mae, rmse, mape...)│
         │               └─────────────────────┘
         │
         └─ 1:N ─────────┬──────────────────────┐
                         │  PredictionResult    │
                         │ (forecast points)    │
                         │ period, value, CI    │
                         └──────────────────────┘

TABLE DESIGN RATIONALE:
──────────────────────

1️⃣ DATASET TABLE
   ├─ Why separate from User?
   │  • Users can have multiple datasets
   │  • Each dataset can have multiple predictions
   │  • Allows soft-delete without deleting User
   │
   ├─ Fields explanation:
   │  • file_path: Store path to CSV file on disk
   │  • date_column_name: "date" or "timestamp" from CSV header
   │  • value_column_name: "value" or "sales" from CSV header
   │  • frequency: Auto-detect if data is daily, hourly, etc.
   │  • date_range: Min/max dates for filtering
   │  • status: active/archived/deleted (soft delete)
   │
   └─ Why these fields?
      • Pre-calculated metadata speeds up listing
      • File path allows retrieving CSV anytime
      • Frequency helps model selection

2️⃣ PREDICTION TABLE
   ├─ Why store predictions?
   │  • Audit trail of what was predicted
   │  • Can rerun same prediction with same params
   │  • Track model performance over time
   │
   ├─ Key fields:
   │  • model_id: Which model (Prophet/ARIMA)
   │  • model_parameters: JSON of hyperparameters
   │  • status: pending/processing/completed/failed
   │  • error_message: If failed, what went wrong
   │
   └─ Why JSON for parameters?
      • Different models have different params
      • Easy to store & retrieve
      • Easy to show history

3️⃣ PREDICTION_RESULT TABLE
   ├─ Why separate from Prediction?
   │  • One prediction generates many forecast points
   │  • Separating allows efficient queries
   │  • Can quickly calculate metrics without loading all points
   │
   ├─ Fields:
   │  • period_index: 0=+1 period, 1=+2 periods, etc.
   │  • forecast_date: Predicted timestamp
   │  • predicted_value: Point forecast
   │  • upper/lower_confidence: 95% CI bands
   │
   └─ Why period_index?
      • Makes period-based queries easy
      • Ensures order even if dates are irregular

4️⃣ PREDICTION_METRIC TABLE
   ├─ Why separate?
   │  • Multiple metrics per prediction
   │  • Can add metrics without changing Prediction table
   │  • Names are flexible
   │
   ├─ Metrics stored:
   │  • mae: Mean Absolute Error
   │  • rmse: Root Mean Squared Error
   │  • mape: Mean Absolute Percentage Error
   │  • r_squared: R² score (0-1)
   │
   └─ Why UNIQUE constraint?
      • Prevent duplicate metrics
      • Only one MAE per prediction

INDEXES RECOMMENDED:
───────────────────
CREATE INDEX idx_dataset_user_id ON dataset(user_id);
CREATE INDEX idx_prediction_dataset_id ON prediction(dataset_id);
CREATE INDEX idx_prediction_user_id ON prediction(user_id);
CREATE INDEX idx_prediction_status ON prediction(status);
"""

# ███████████████████████████████████████████████████████████████████████████
# 4. COMPONENTS & RESPONSIBILITIES
# ███████████████████████████████████████████████████████████████████████████

"""
🔧 KEY COMPONENTS - WHAT & WHY

CORE LAYER (app/core/)
─────────────────────
📄 config.py
   WHAT: Loads environment variables with type checking
   WHY:  
   • All config in one place
   • Type safe (catches config errors early)
   • Works across dev/test/prod with .env files
   
   EXAMPLE CONFIG:
   DATABASE_URL = "postgresql://user:pass@localhost/tfg_db"
   MAX_FILE_SIZE_MB = 50
   DEFAULT_FORECAST_PERIODS = 12

📋 constants.py
   WHAT: Enums and constants
   WHY:
   • Prevents magic strings like "prophet" scattered in code
   • IDE autocomplete: ModelType.PROPHET vs "prophet"
   • Easy to add models: Add to ModelType enum
   
   EXAMPLE:
   class ModelType(str, Enum):
       PROPHET = "prophet"
       ARIMA = "arima"

DATABASE LAYER (app/db/)
────────────────────────
🗄️ base.py
   WHAT: SQLAlchemy engine, session factory, Base class
   WHY:
   • Single place to configure database connection
   • Pool settings for connection management
   • All models inherit from DeclarativeBase
   
   IMPLEMENTS:
   • create_engine() with connection pooling
   • SessionLocal factory for session creation
   • DeclarativeBase for ORM models

🔌 session.py
   WHAT: FastAPI dependency for database sessions
   WHY:
   • Automatic session cleanup after request
   • Dependency injection: @app.get(..., Depends(get_db))
   • Proper error handling & rollback
   
   PATTERN:
   @router.get("/")
   def list_items(db: Session = Depends(get_db)):
       items = db.query(Item).all()
       return items

ORM MODELS (app/models/)
───────────────────────
📊 dataset.py
   WHAT: SQLAlchemy ORM model for datasets table
   WHY:
   • Type-safe database access
   • Relationships defined (user → datasets)
   • Validates data before saving
   
   KEY FIELDS:
   • user_id: Which user owns this
   • file_path: Where CSV is stored
   • date_column_name: CSV header to use for dates
   • value_column_name: CSV header for values
   • frequency: D/H/W/M/Y detected frequency

🔮 prediction.py
   WHAT: ORM model for prediction job results
   WHY:
   • Stores entire job metadata
   • Tracks status (pending → completed)
   • Stores parameters used + execution time
   
   KEY FIELDS:
   • dataset_id: Which dataset was used
   • model_id: Which model was used
   • model_parameters: JSON of {p:1, d:1, q:1} etc.
   • status: To track async job completion
   • error_message: If job failed

SERVICE LAYER (app/services/)
────────────────────────────
📂 dataset_service.py
   WHAT: Business logic for dataset operations
   WHY:
   • Endpoints delegate to services
   • Services contain reusable logic
   • Easy to test independently
   
   METHODS:
   • create_dataset(): Save dataset to DB
   • get_dataset(): Fetch with ownership check
   • list_datasets(): Query user's datasets
   • delete_dataset(): Soft delete + cleanup
   
   EXAMPLE IMPLEMENTATION:
   @staticmethod
   def create_dataset(db, user_id, dataset_create, file_path, ...):
       # Create instance
       dataset = Dataset(
           user_id=user_id,
           name=dataset_create.name,
           file_path=file_path,
           ...
       )
       # Save & return
       db.add(dataset)
       db.commit()
       db.refresh(dataset)
       return dataset

🔮 prediction_service.py
   WHAT: Orchestrates prediction workflow
   WHY:
   • Complex logic: validate → model → store results
   • Should not be in endpoint
   • Can be called from endpoints OR external tasks
   
   WORKFLOW:
   1. Validate dataset exists
   2. Load CSV from file_path
   3. Create model using ModelFactory
   4. model.fit(historical_data)
   5. results = model.predict(periods)
   6. Store results in DB
   7. Calculate metrics
   8. Return completed prediction

📄 csv_handler.py
   WHAT: All CSV file operations
   WHY:
   • Centralized file handling
   • Validation in one place
   • Easy to change storage (file → S3 later)
   
   METHODS:
   • save_uploaded_file(): Store file to disk
   • validate_csv_structure(): Check required columns
   • load_csv_as_dataframe(): Read & clean data
   • extract_metadata(): Get statistics
   • detect_frequency(): Auto-detect D/H/W/M/Y

🏭 model_factory.py
   WHAT: Creates correct ML model instances
   WHY:
   • Centralized model instantiation
   • Easy to add new models
   • Validates parameters before creating
   
   METHODS:
   • create_model(type, params): Factory method
   • get_available_models(db): List active models
   • get_model_defaults(type): Get default params

MACHINE LEARNING (app/ml/)
──────────────────────────
🔧 models/base_model.py
   WHAT: Abstract base class for all models
   WHY:
   • Guarantees all models have same interface
   • Prophet & ARIMA implement differently
   • Interface: fit() → predict()
   
   ABSTRACT METHODS:
   def fit(self, data: pd.DataFrame) -> None
   def predict(self, periods: int) -> Tuple[...]
   def get_model_name(self) -> str

📈 models/prophet_model.py
   WHAT: Implements Prophet-specific prediction
   WHY:
   • Inherits from BasePredictionModel
   • Prophet requires specific data format
   • Handles seasonality, holidays, etc.

📊 models/arima_model.py
   WHAT: Implements ARIMA-specific prediction
   WHY:
   • Different package (statsmodels)
   • Requires (p,d,q) parameters
   • Different confidence interval calculation

📊 preprocessing.py
   WHAT: Data cleaning utilities
   WHY:
   • Different models need different prep
   • Reusable across models
   
   METHODS:
   • clean_data(): Remove NaN, duplicates, sort
   • handle_missing_values(): Interpolate or drop
   • normalize(): 0-1 scaling (optional)

📈 metrics.py
   WHAT: Calculate performance metrics
   WHY:
   • Multiple metrics per prediction
   • Standardized calculations
   • Easy to compare models later
   
   METRICS:
   • MAE: Average absolute error
   • RMSE: Penalizes large errors more
   • MAPE: Error as percentage
   • R²: Goodness of fit

UTILITIES (app/utils/)
──────────────────────
📂 file_handler.py
   WHAT: File operations (upload, delete, validate)
   WHY:
   • Centralized file management
   • Security checks (path traversal protection)
   • Easy to swap storage backend
   
   METHODS:
   • ensure_upload_dir_exists()
   • generate_unique_filename()
   • delete_file()
   • is_safe_path(): Security validation

✅ validators.py
   WHAT: Custom validation logic
   WHY:
   • Beyond Pydantic validation
   • Domain-specific (column names, frequencies)
   
   VALIDATORS:
   • validate_column_names()
   • validate_frequency(): D/H/W/M/Y only
   • validate_forecast_periods()
   • validate_model_parameters()

⚠️ exceptions.py
   WHAT: Custom exception classes
   WHY:
   • Specific error types for error handling
   • Better error messages
   • Endpoints can catch specific errors
   
   EXCEPTIONS:
   • InvalidFileError
   • FileTooLargeError
   • InsufficientDataError
   • ModelNotFittedError
   • PermissionError
   • PredictionError

API ENDPOINTS (app/api/v1/endpoints/)
─────────────────────────────────────
📂 datasets.py
   ENDPOINTS:
   • POST /api/v1/datasets (upload)
   • GET /api/v1/datasets (list)
   • GET /api/v1/datasets/{id} (get one)
   • DELETE /api/v1/datasets/{id} (delete)
   
   FLOW:
   1. Validate input
   2. Call DatasetService
   3. Return response

🔮 predictions.py
   ENDPOINTS:
   • POST /api/v1/predictions (create)
   • GET /api/v1/predictions (list)
   • GET /api/v1/predictions/{id} (get with results)
   • DELETE /api/v1/predictions/{id} (delete)
   
   FLOW:
   1. Validate input
   2. Call PredictionService
   3. Return with results

🎛️ models.py
   ENDPOINTS:
   • GET /api/v1/models (list available)
   • GET /api/v1/models/{id} (get details)
   • GET /api/v1/models/{id}/defaults (get defaults)
"""

# ███████████████████████████████████████████████████████████████████████████
# 5. IMPLEMENTATION ROADMAP
# ███████████████████████████████████████████████████████████████████████████

"""
🗺️ IMPLEMENTATION ROADMAP - STEP BY STEP

PHASE 1: DATABASE & ORM (1-2 days)
─────────────────────────────────
Goal: Set up database tables

✅ Do these first:
1. ✔ Update app/db/base.py
   - Create SQLAlchemy engine
   - Create SessionLocal factory
   - Implement init_db() to create tables

2. ✔ Update app/models/
   - Fix relationships in all model files
   - Add all __repr__ methods
   - Test database creation

3. ✔ Update app/db/init_db.py
   - Implement init_db_with_defaults()
   - Create Prophet & ARIMA default models

PHASE 2: SERVICES & BUSINESS LOGIC (2-3 days)
─────────────────────────────────────────────
Goal: Implement core business operations

1. Implement app/services/dataset_service.py
   - create_dataset()
   - get_dataset()
   - list_datasets()
   - update_dataset()
   - delete_dataset()

2. Implement app/services/csv_handler.py
   - save_uploaded_file()
   - validate_csv_structure()
   - load_csv_as_dataframe()
   - extract_metadata()
   - detect_frequency()

3. Implement app/utils/
   - file_handler.py: File operations
   - validators.py: Custom validation
   - exceptions.py: Already done (or verify)

PHASE 3: ML MODELS (2-3 days)
────────────────────────────
Goal: Implement Prophet & ARIMA

1. Implement app/ml/models/base_model.py
   - Setup abstract base class
   - Implement validate_data()

2. Implement app/ml/models/prophet_model.py
   - __init__: Setup Prophet
   - fit(): Train model
   - predict(): Generate forecast
   - get_model_name()

3. Implement app/ml/models/arima_model.py
   - __init__: Setup ARIMA
   - fit(): Train model
   - predict(): Generate forecast
   - get_model_name()

4. Implement app/ml/preprocessing.py
   - clean_data()
   - handle_missing_values()
   - normalize() & denormalize()

5. Implement app/ml/metrics.py
   - calculate_mae()
   - calculate_rmse()
   - calculate_mape()
   - calculate_r_squared()
   - calculate_all_metrics()

PHASE 4: MODEL FACTORY & PREDICTION SERVICE (1-2 days)
──────────────────────────────────────────────────────
Goal: Connect models to services

1. Implement app/services/model_factory.py
   - create_model()
   - get_available_models()
   - get_model_defaults()

2. Implement app/services/prediction_service.py
   - create_prediction(): THE MAIN ORCHESTRATION
   - get_prediction()
   - list_predictions()
   - delete_prediction()

PHASE 5: API ENDPOINTS (1-2 days)
─────────────────────────────────
Goal: Connect services to HTTP endpoints

1. Update app/api/v1/dependencies.py
   - get_current_user_v1()
   - validate_pagination()

2. Implement app/api/v1/endpoints/datasets.py
   - upload_dataset()
   - list_datasets()
   - get_dataset()
   - delete_dataset()

3. Implement app/api/v1/endpoints/predictions.py
   - create_prediction()
   - list_predictions()
   - get_prediction()
   - delete_prediction()

4. Implement app/api/v1/endpoints/models.py
   - list_models()
   - get_model()
   - get_model_defaults()

5. Update app/api/v1/__init__.py
   - Include all endpoint routers

PHASE 6: TESTING & INTEGRATION (1-2 days)
──────────────────────────────────────────
Goal: Ensure everything works

1. Unit tests for services
2. Integration tests for endpoints
3. ML model tests
4. Database tests

TOTAL ESTIMATED TIME: 8-14 days / 2 weeks
"""

# ███████████████████████████████████████████████████████████████████████████
# 6. STEP-BY-STEP IMPLEMENTATION GUIDE
# ███████████████████████████████████████████████████████████████████████████

"""
📖 HOW TO IMPLEMENT EACH COMPONENT

GENERAL PRINCIPLES:
───────────────────
✅ DO:
• Follow the TODO comments in each file
• Write docstrings for all functions
• Use type hints everywhere
• Handle exceptions explicitly
• Test as you go
• Keep functions small & focused

❌ DON'T:
• Skip error handling
• Write giant functions (>50 lines)
• Ignore TODO comments
• Forget type hints
• Copy-paste code (refactor instead)

─────────────────────────────────────────────────────────────────────────────

EXAMPLE IMPLEMENTATION: DatasetService.create_dataset()
────────────────────────────────────────────────────────

WHAT you need to implement:
• Create a new Dataset ORM instance
• Set all required fields
• Save to database
• Return the created dataset

SKELETON PROVIDED:
    @staticmethod
    def create_dataset(
        db: Session,
        user_id: int,
        dataset_create: DatasetCreate,
        file_path: str,
        file_size: int,
        original_filename: str
    ) -> Dataset:
        \"\"\"TODO: Create new dataset in database\"\"\"
        pass

YOUR IMPLEMENTATION:
    @staticmethod
    def create_dataset(
        db: Session,
        user_id: int,
        dataset_create: DatasetCreate,
        file_path: str,
        file_size: int,
        original_filename: str
    ) -> Dataset:
        \"\"\"Create new dataset in database after file upload\"\"\"
        
        # 1. Create ORM instance with data
        dataset = Dataset(
            user_id=user_id,
            name=dataset_create.name,
            description=dataset_create.description,
            file_path=file_path,
            file_size_bytes=file_size,
            original_filename=original_filename,
            date_column_name=dataset_create.date_column_name,
            value_column_name=dataset_create.value_column_name,
            frequency=dataset_create.frequency,
            status="active"
        )
        
        # 2. Add to session
        db.add(dataset)
        
        # 3. Commit to database
        db.commit()
        
        # 4. Refresh to get ID
        db.refresh(dataset)
        
        # 5. Return created instance
        return dataset

WORKFLOW:
────────
Endpoint calls:
    dataset = DatasetService.create_dataset(
        db=db,
        user_id=user_id,      # From token
        dataset_create=request,  # From request body
        file_path=saved_path,  # From CSVHandler
        file_size=file_bytes,  # From uploaded file
        original_filename=filename  # From uploaded file
    )

─────────────────────────────────────────────────────────────────────────────

EXAMPLE IMPLEMENTATION: CSVHandler.save_uploaded_file()
───────────────────────────────────────────────────────

WHAT you need:
• Get uploaded file from FastAPI
• Validate it's a CSV
• Validate file size
• Save to disk with unique name
• Return path & size

YOUR IMPLEMENTATION:
    @staticmethod
    async def save_uploaded_file(file, user_id: int, dataset_name: str) -> Tuple[str, int]:
        \"\"\"Save uploaded CSV file to disk\"\"\"
        from app.core.config import settings
        
        # 1. Validate file extension
        if not file.filename.endswith('.csv'):
            raise InvalidFileError("Only CSV files allowed")
        
        # 2. Validate file size
        file_size = await file.size  # Get uploaded file size
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise FileTooLargeError(f"Max {settings.MAX_FILE_SIZE_MB}MB allowed")
        
        # 3. Generate unique filename
        file_path = FileManager.generate_unique_filename(user_id, dataset_name)
        
        # 4. Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 5. Save file to disk
        contents = await file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)
        
        # 6. Return path & size
        return file_path, len(contents)

─────────────────────────────────────────────────────────────────────────────

EXAMPLE IMPLEMENTATION: ProphetModel.fit()
───────────────────────────────────────────

WHAT you need:
• Validate data
• Format data for Prophet (needs 'ds' & 'y' columns)
• Call fit() on self.model
• Set self.is_fitted = True

YOUR IMPLEMENTATION:
    def fit(self, data: pd.DataFrame) -> None:
        \"\"\"Train Prophet model on data\"\"\"
        from prophet import Prophet
        
        # 1. Validate data
        if not self.validate_data(data):
            raise InsufficientDataError("Not enough historical data")
        
        # 2. Prepare data for Prophet
        prepared_data = data.copy()
        prepared_data.columns = ['ds', 'y']  # Prophet expects these names
        prepared_data['ds'] = pd.to_datetime(prepared_data['ds'])
        prepared_data['y'] = pd.to_numeric(prepared_data['y'])
        
        # 3. Fit model
        try:
            self.model.fit(prepared_data)
            self.is_fitted = True
        except Exception as e:
            raise PredictionError(f"Prophet training failed: {str(e)}")
    
    def predict(self, periods: int) -> Tuple[List[float], List[float], List[float]]:
        \"\"\"Generate forecast using Prophet\"\"\"
        if not self.is_fitted:
            raise ModelNotFittedError("Model not fitted. Call fit() first")
        
        # 1. Create future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq='D')
        
        # 2. Generate forecast
        forecast = self.model.predict(future)
        
        # 3. Extract last 'periods' rows (the forecast)
        forecast = forecast.tail(periods)
        
        # 4. Extract columns
        predictions = forecast['yhat'].tolist()
        upper_ci = forecast['yhat_upper'].tolist()
        lower_ci = forecast['yhat_lower'].tolist()
        
        # 5. Return as tuple
        return predictions, upper_ci, lower_ci

─────────────────────────────────────────────────────────────────────────────

EXAMPLE IMPLEMENTATION: PredictionService.create_prediction()
──────────────────────────────────────────────────────────────

WHAT you need:
• Validate dataset exists
• Validate model exists
• Create Prediction record
• Load CSV
• Create & train model
• Generate & store results
• Calculate & store metrics

YOUR IMPLEMENTATION:
    @staticmethod
    async def create_prediction(db, user_id, prediction_create) -> Prediction:
        \"\"\"Create and execute a prediction\"\"\"
        import time
        
        # 1. Validate dataset exists & belongs to user
        dataset = db.query(Dataset).filter(
            Dataset.id == prediction_create.dataset_id,
            Dataset.user_id == user_id
        ).first()
        if not dataset:
            raise PermissionError("Dataset not found or not owned by user")
        
        # 2. Validate model exists
        model_obj = db.query(PredictionModel).get(prediction_create.model_id)
        if not model_obj:
            raise ModelNotFoundError("Model not available")
        
        # 3. Create Prediction record with pending status
        prediction = Prediction(
            dataset_id=prediction_create.dataset_id,
            model_id=prediction_create.model_id,
            user_id=user_id,
            prediction_name=prediction_create.prediction_name or f"Prediction_{int(time.time())}",
            model_parameters=prediction_create.model_parameters,
            forecast_periods=prediction_create.forecast_periods or 12,
            confidence_level=prediction_create.confidence_level,
            status="pending"
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        try:
            # 4. Load CSV data
            df = CSVHandler.load_csv_as_dataframe(
                dataset.file_path,
                dataset.date_column_name,
                dataset.value_column_name
            )
            
            # 5. Create model
            model = ModelFactory.create_model(model_obj.name, prediction_create.model_parameters)
            
            # 6. Train model
            start_time = time.time()
            model.fit(df)
            
            # 7. Generate forecast
            predictions, upper_ci, lower_ci = model.predict(prediction.forecast_periods)
            end_time = time.time()
            
            # 8. Store results
            for i, (pred, upper, lower) in enumerate(zip(predictions, upper_ci, lower_ci)):
                result = PredictionResult(
                    prediction_id=prediction.id,
                    period_index=i,
                    forecast_date=None,  # TODO: Calculate from dataset frequency
                    predicted_value=pred,
                    upper_confidence_bound=upper,
                    lower_confidence_bound=lower
                )
                db.add(result)
            
            # 9. Calculate metrics
            metrics_dict = MetricsCalculator.calculate_all_metrics(df['y'].tolist()[-50:], predictions)
            for metric_name, metric_value in metrics_dict.items():
                metric = PredictionMetric(
                    prediction_id=prediction.id,
                    metric_name=metric_name,
                    metric_value=metric_value
                )
                db.add(metric)
            
            # 10. Update prediction status
            prediction.status = "completed"
            prediction.execution_time_seconds = end_time - start_time
            prediction.completed_at = datetime.utcnow()
            
        except Exception as e:
            prediction.status = "failed"
            prediction.error_message = str(e)
        
        # 11. Commit everything
        db.commit()
        db.refresh(prediction)
        
        return prediction
"""

# ███████████████████████████████████████████████████████████████████████████
# 7. DATABASE SETUP
# ███████████████████████████████████████████████████████████████████████████

"""
🗄️ DATABASE SETUP INSTRUCTIONS

STEP 1: PostgreSQL Installation
────────────────────────────────
For Windows:
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run installer, remember password for 'postgres' user
3. Choose port 5432 (default)

For macOS:
brew install postgresql@15

For Linux:
sudo apt-get install postgresql

STEP 2: Create Database
─────────────────────
Using psql command line:
1. psql -U postgres
2. CREATE DATABASE tfg_db;
3. \\l  (list databases - verify tfg_db exists)

STEP 3: Set Environment Variables
──────────────────────────────────
In .env file:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/tfg_db

STEP 4: Initialize Database
────────────────────────────
From Python:
from app.db.base import init_db
init_db()

This creates all tables automatically.

STEP 5: Verify Setup
───────────────────
psql -U postgres -d tfg_db -l

Tables should be:
- user
- dataset
- prediction_model
- prediction
- prediction_result
- prediction_metric
"""

# ███████████████████████████████████████████████████████████████████████████
# 8. TESTING STRATEGY
# ███████████████████████████████████████████████████████████████████████████

"""
🧪 TESTING STRATEGY - HOW TO TEST EACH COMPONENT

UNIT TESTS (test individual functions)
──────────────────────────────────────

1. Test CSV Handler:
   • test_save_uploaded_file_valid_csv()
   • test_save_uploaded_file_invalid_extension()
   • test_save_uploaded_file_too_large()
   • test_validate_csv_structure()
   • test_load_csv_as_dataframe()

2. Test Services:
   • test_create_dataset()
   • test_get_dataset_ownership()
   • test_list_datasets()
   • test_create_prediction()
   • test_delete_dataset()

3. Test ML Models:
   • test_prophet_fit_predict()
   • test_arima_fit_predict()
   • test_model_with_insufficient_data()

4. Test Metrics:
   • test_calculate_mae()
   • test_calculate_rmse()
   • test_calculate_all_metrics()

INTEGRATION TESTS (test workflows)
──────────────────────────────────

1. Complete dataset upload workflow:
   • POST /datasets with CSV
   • GET /datasets to verify
   • Verify file saved
   • Verify metadata extracted

2. Complete prediction workflow:
   • POST /predictions with dataset & model
   • Poll GET /predictions/{id} for completion
   • Verify results stored
   • Verify metrics calculated

SAMPLE TEST:
───────────
import pytest
from app.services.dataset_service import DatasetService
from app.models import Dataset

def test_create_dataset(db_session):
    \"\"\"Test dataset creation\"\"\"
    # Create dataset
    dataset = DatasetService.create_dataset(
        db=db_session,
        user_id=1,
        dataset_create=DatasetCreateRequest(
            name="test_data",
            description="Test dataset",
            date_column_name="date",
            value_column_name="value",
            frequency="D"
        ),
        file_path="/uploads/test.csv",
        file_size=1024,
        original_filename="test.csv"
    )
    
    # Assertions
    assert dataset.id is not None
    assert dataset.name == "test_data"
    assert dataset.user_id == 1
    assert dataset.status == "active"
    
    # Verify in database
    fetched = db_session.query(Dataset).get(dataset.id)
    assert fetched is not None
    assert fetched.name == "test_data"
"""

# ███████████████████████████████████████████████████████████████████████████
# 9. COMMON PITFALLS & SOLUTIONS
# ███████████████████████████████████████████████████████████████████████████

"""
⚠️ COMMON MISTAKES & HOW TO AVOID THEM

PITFALL 1: Not Validating File Uploads
───────────────────────────────────────
WRONG:
    def upload_file(file):
        contents = file.read()
        with open('uploads/' + file.filename) as f:
            f.write(contents)

PROBLEMS:
• No extension check → .exe malware could be uploaded
• Path traversal: filename="../../admin.csv" → overwrites system files
• No size limit → DOS attack: 100GB file fills disk

RIGHT:
    def upload_file(file):
        if not file.filename.endswith('.csv'):
            raise InvalidFileError()
        if file.size > MAX_SIZE:
            raise FileTooLargeError()
        path = FileManager.generate_unique_filename(user_id, name)
        if not FileManager.is_safe_path(path, UPLOAD_DIR):
            raise InvalidFileError()
        # ... save

─────────────────────────────────────────────────────────────────────────────

PITFALL 2: Forgetting Authorization Checks
───────────────────────────────────────────
WRONG:
    def get_dataset(dataset_id):
        dataset = db.query(Dataset).get(dataset_id)
        return dataset

PROBLEM:
• User A can access User B's private datasets via GET /datasets/999

RIGHT:
    def get_dataset(dataset_id, user_id):
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()
        if not dataset:
            raise PermissionError()
        return dataset

─────────────────────────────────────────────────────────────────────────────

PITFALL 3: Not Handling Async Operations
─────────────────────────────────────────
PROBLEM:
• Prediction takes 30 seconds
• Client waits 30 seconds → timeout
• User has bad experience

SOLUTION OPTIONS:

Option A: Async Jobs (Recommended)
    @app.post("/predictions")
    async def create_prediction(request, db, user):
        prediction = Prediction(status="pending")
        db.add(prediction)
        db.commit()
        
        # Send to background job queue
        celery_app.send_task('run_prediction', args=[prediction.id])
        
        return {"prediction_id": prediction.id, "status": "pending"}
    
    # Later, user polls:
    # GET /predictions/123 → returns status & results when done

Option B: Sync for MVP
    # Acceptable for Graduation Project
    # Just add timeout handling:
    @app.post("/predictions", timeout=60)
    async def create_prediction(...):
        # Will run for up to 60 seconds
        pass

─────────────────────────────────────────────────────────────────────────────

PITFALL 4: Missing Error Handling
─────────────────────────────────
WRONG:
    def calculate_metrics(actual, predicted):
        mae = mean_absolute_error(actual, predicted)
        return mae

PROBLEMS:
• What if actual/predicted lengths don't match?
• What if they're empty lists?
• What if all values are NaN?

RIGHT:
    def calculate_metrics(actual, predicted):
        if len(actual) != len(predicted):
            raise ValidationError("Lengths don't match")
        if len(actual) == 0:
            raise ValidationError("No data to calculate metrics")
        if all(pd.isna(actual)) or all(pd.isna(predicted)):
            raise ValidationError("All values are NaN")
        
        mae = mean_absolute_error(actual, predicted)
        if pd.isna(mae):
            raise PredictionError("Metric calculation resulted in NaN")
        
        return mae

─────────────────────────────────────────────────────────────────────────────

PITFALL 5: Not Using Type Hints
───────────────────────────────
WRONG:
    def get_dataset(dataset_id):
        dataset = db.query(Dataset).get(dataset_id)
        return dataset

RIGHT:
    def get_dataset(dataset_id: int) -> Optional[Dataset]:
        dataset = db.query(Dataset).get(dataset_id)
        return dataset

BENEFITS:
• IDE autocomplete works
• Type checker catches mistakes early
• Self-documenting code

─────────────────────────────────────────────────────────────────────────────

PITFALL 6: SQLAlchemy Session Management
─────────────────────────────────────────
WRONG:
    def list_datasets(db):
        return db.query(Dataset).all()

PROBLEM:
• After function returns, session closes lazy-loaded relationships fail

RIGHT:
    def list_datasets(db):
        datasets = db.query(Dataset).all()
        # Access relationships BEFORE returning:
        for d in datasets:
            _ = d.predictions  # Force load
        return datasets
    
    # OR use joinedload:
    def list_datasets(db):
        from sqlalchemy.orm import joinedload
        return db.query(Dataset).options(
            joinedload(Dataset.predictions)
        ).all()

─────────────────────────────────────────────────────────────────────────────

PITFALL 7: CSV Encoding Issues
──────────────────────────────
PROBLEM:
• UTF-8 BOM, Latin-1, etc. → Cannot parse CSV properly

SOLUTION:
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    # or
    df = pd.read_csv(file_path, encoding='latin-1')
    # Handle common text encoding issues

─────────────────────────────────────────────────────────────────────────────

PITFALL 8: Not Cleaning Data
───────────────────────────
PROBLEM:
• CSV has "N/A", "NULL", "" → models fail silently

SOLUTION:
    df = pd.read_csv(...)
    df = df.dropna()  # Remove rows with NaN
    df = df.drop_duplicates()  # Remove duplicates
    df = df.sort_values(by='date')  # Ensure sorted
    df['value'] = pd.to_numeric(df['value'], 'coerce')  # Force numeric
"""

# ███████████████████████████████████████████████████████████████████████████
# 10. DEPLOYMENT CHECKLIST
# ███████████████████████████████████████████████████████████████████████████

"""
✅ DEPLOYMENT CHECKLIST - BEFORE GOING TO PRODUCTION

SECURITY
────────
□ All user inputs validated
□ File upload restrictions (size, extension, path traversal)
□ Authentication on all endpoints
□ Authorization checks (user owns resource)
□ No sensitive data in logs
□ CORS configured properly
□ SQL injection protection (use ORM, parameters)
□ Rate limiting implemented
□ HTTPS enabled in production

PERFORMANCE
───────────
□ Database indexes created (user_id, dataset_id, etc.)
□ Pagination implemented (limit max results)
□ Lazy loading vs eager loading optimized
□ Large file handling (streaming, not loading into memory)
□ Caching for static data (models list)
□ Async jobs for long-running predictions
□ Database connection pooling configured

RELIABILITY
───────────
□ Error handling for all edge cases
□ Logging implemented and monitored
□ Database backups automated
□ Upload directory permissions correct
□ File cleanup on delete (don't leave orphaned CSVs)
□ Graceful degradation if ML library fails
□ Status codes appropriate (400, 403, 404, 500)

TESTING
───────
□ Unit tests pass
□ Integration tests pass
□ Edge cases tested (empty CSV, huge file, etc.)
□ Manual smoke tests (upload, predict, delete)
□ Load testing done
□ Concurrent user testing done

DOCUMENTATION
──────────────
□ API documentation complete
□ README updated
□ Environment variables documented
□ Setup instructions clear
□ Database schema documented

MONITORING
──────────
□ Error tracking setup (Sentry, etc.)
□ Performance monitoring (APM)
□ Log aggregation (ELK, etc.)
□ Alerts configured
□ Health checks working

DEPLOYMENT
──────────
□ Docker image created
□ Environment variables set in production
□ Database migrated to production
□ Initial data (models) seeded
□ Static files served correctly
□ CORS whitelist configured
□ SSL certificate configured

POST-DEPLOYMENT
────────────────
□ Smoke tests run manually
□ Logs monitored for errors
□ Performance baseline established
□ Database performance monitored
□ User feedback collected
"""

print(__doc__)
