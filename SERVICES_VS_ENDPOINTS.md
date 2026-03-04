"""
📚 FileService vs Endpoints Architecture

Complete explanation of the difference between business logic (FileService)
and HTTP endpoints (files.py, datasets.py).
"""

# 📚 FileService vs Endpoints - Architecture Explanation

## 🎯 Quick Overview

| Component | Purpose | Handles |
|-----------|---------|---------|
| **FileService** | Business Logic Layer | Pure logic, reusable code |
| **files.py** | HTTP Endpoints | Upload/Delete files, HTTP handling |
| **datasets.py** | HTTP Endpoints | View datasets, HTTP handling |

---

## 🔧 FileService - BUSINESS LOGIC LAYER

### What It Is
A **service class with static methods** that contains **reusable, pure logic** for all file-related operations.

### Location
`app/services/file_service.py`

### Responsibilities

```python
class FileService:
    # 📥 FILE UPLOAD LOGIC
    @staticmethod
    async def upload_file(file, user_id, db):
        """
        Process file upload completely:
        ✅ Validates file type (CSV/XLSX)
        ✅ Validates file size (≤ 5MB)
        ✅ Auto-detects date column
        ✅ Auto-detects numeric column
        ✅ Reads CSV/XLSX into DataFrame
        ✅ Processes and transforms data
        ✅ Saves to database
        ✅ Handles all errors
        
        Returns: Dataset object + Data entries
        """
        # Complex business logic here
        pass
    
    # 📖 GET USER FILES
    @staticmethod
    def get_user_files(user_id, db):
        """
        Get all datasets belonging to user
        Returns: List of Dataset objects
        """
        pass
    
    # 🔍 GET FILE BY ID
    @staticmethod
    def get_file_by_id(file_id, user_id, db):
        """
        Get specific file with ownership verification
        Returns: Dataset object or raises HTTPException
        """
        pass
    
    # 🗑️ DELETE FILE
    @staticmethod
    def delete_file(file_id, user_id, db):
        """
        Delete file with ownership verification
        Returns: Confirmation dictionary
        """
        pass
```

### Key Characteristics

✅ **Does NOT know about HTTP**
- No FastAPI decorators
- No UploadFile objects (only raw bytes)
- No HTTPException needed

✅ **Pure Business Logic**
- Validates data
- Transforms data
- Interacts with database
- Handles errors

✅ **Reusable Everywhere**
- Can be called from endpoints
- Can be called from background jobs
- Can be called from CLI commands
- Can be called from other services

✅ **Testable**
- Easy to unit test
- No HTTP complications
- No external dependencies

---

## 📡 files.py - HTTP ENDPOINTS (Upload/Delete)

### What It Is
FastAPI routes that handle **HTTP requests for file upload and deletion**.

### Location
`app/api/v1/endpoints/files.py`

### Endpoints

```python
# 📥 UPLOAD ENDPOINT
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Responsibilities:
    ✅ Receives HTTP POST request with file
    ✅ Extracts authenticated user via dependency
    ✅ Gets database session
    ✅ Calls FileService.upload_file() to do the work
    ✅ Formats response as JSON
    ✅ Handles HTTP exceptions
    
    Returns: JSON response with dataset info
    """
    result = await FileService.upload_file(file, current_user.id, db)
    return {
        "message": "File uploaded",
        "dataset": result["dataset"],
        "entries_count": len(result["data_entries"])
    }


# 📖 GET MY FILES ENDPOINT
@router.get("/my-files")
def get_my_files(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Responsibilities:
    ✅ Receives HTTP GET request
    ✅ Extracts authenticated user
    ✅ Calls FileService.get_user_files()
    ✅ Formats response
    
    Returns: JSON list of user's files
    """
    files = FileService.get_user_files(current_user.id, db)
    return {
        "user_id": current_user.id,
        "total_files": len(files),
        "data": files
    }


# 🗑️ DELETE ENDPOINT
@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Responsibilities:
    ✅ Receives HTTP DELETE request with file_id
    ✅ Extracts authenticated user
    ✅ Calls FileService.delete_file()
    ✅ Returns HTTP 200 OK response
    
    Returns: JSON confirmation
    """
    result = FileService.delete_file(file_id, current_user.id, db)
    return result
```

### Key Characteristics

✅ **Handles HTTP Communication**
- Receives FastAPI request objects (UploadFile)
- Returns JSON responses
- HTTP status codes

✅ **Authentication & Authorization**
- Uses `Depends(get_current_user)` to get authenticated user
- Passes user_id to FileService for ownership checks

✅ **Thin Layer**
- Minimal logic (just HTTP handling)
- Delegates real work to FileService

✅ **HTTP-Specific Only**
- Cannot be reused outside HTTP context
- Depends on FastAPI framework

---

## 📊 datasets.py - HTTP ENDPOINTS (Read-Only)

### What It Is
FastAPI routes that handle **HTTP requests for viewing dataset information**.

### Location
`app/api/v1/endpoints/datasets.py`

### Endpoints

```python
# 📖 GET ALL DATASETS
@router.get("")
def get_datasets(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Responsibilities:
    ✅ Receives HTTP GET request
    ✅ Gets authenticated user
    ✅ Calls FileService.get_user_files()
    ✅ Formats response (simplified: only id + name)
    
    Returns: JSON with minimal dataset info
    
    NOTE: Different formatting than files.py!
    """
    datasets = FileService.get_user_files(current_user.id, db)
    
    # Format as simple list of {id, name}
    dataset_list = [
        {
            "id": dataset.id,
            "name": dataset.name
        }
        for dataset in datasets
    ]
    
    return {
        "user_id": current_user.id,
        "total_datasets": len(dataset_list),
        "datasets": dataset_list
    }


# 📊 GET DATASET DATA
@router.get("/id/{dataset_id}/data")
def get_dataset_data(
    dataset_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Responsibilities:
    ✅ Receives HTTP GET request with dataset_id
    ✅ Gets authenticated user
    ✅ Calls FileService.get_file_by_id() for ownership check
    ✅ Extracts data points from dataset
    ✅ Formats response with DS and y fields
    
    Returns: JSON with time series data
    """
    dataset = FileService.get_file_by_id(dataset_id, current_user.id, db)
    
    points_list = [
        {
            "DS": str(data_point.DS),
            "y": data_point.y
        }
        for data_point in dataset.data_entries
    ]
    
    return {
        "dataset_id": dataset_id,
        "total_points": len(points_list),
        "data": points_list
    }
```

### Key Characteristics

✅ **Read-Only Operations**
- No file upload here (that's in files.py)
- No deletion here (that's in files.py)
- Only GET endpoints

✅ **Different Response Format**
- `get_datasets()` returns simplified {id, name} list
- `get_dataset_data()` returns {DS, y} data points
- Different from files.py responses!

✅ **Reuses FileService**
- Same `FileService.get_user_files()`
- Same `FileService.get_file_by_id()`
- But formats differently for different purpose

---

## 🎯 Architecture Diagram

```
┌────────────────────────────────────────────────────┐
│           CLIENT (Frontend/Postman)                │
└────────────────────────────────────────────────────┘
                         ↓
                    HTTP Requests
                         ↓
    ┌────────────────────────────────────────────────┐
    │  ENDPOINTS LAYER (files.py, datasets.py)       │
    ├────────────────────────────────────────────────┤
    │                                                │
    │  files.py (Upload/Delete)                      │
    │  ├─ POST /files/upload                         │
    │  ├─ GET /files/my-files                        │
    │  └─ DELETE /files/{id}                         │
    │                                                │
    │  datasets.py (Read-Only)                       │
    │  ├─ GET /datasets                              │
    │  └─ GET /datasets/id/{id}/data                 │
    │                                                │ ← HTTP HANDLING
    │  Responsibilities:                             │
    │  • Receive HTTP requests                       │
    │  • Extract authenticated user                  │
    │  • Format JSON responses                       │
    │  • Handle HTTP errors                          │
    │                                                │
    └────────────────────────────────────────────────┘
                         ↓
                 Calls FileService
                         ↓
    ┌────────────────────────────────────────────────┐
    │  BUSINESS LOGIC LAYER (file_service.py)        │
    ├────────────────────────────────────────────────┤
    │                                                │
    │  FileService (Reusable Logic)                  │
    │  ├─ upload_file() → Validate, process, save   │
    │  ├─ get_user_files() → Query & return files   │
    │  ├─ get_file_by_id() → Query with ownership   │
    │  ├─ delete_file() → Delete with verification  │
    │  └─ ... other methods                          │
    │                                                │ ← BUSINESS LOGIC
    │  Characteristics:                              │
    │  • Pure logic (no HTTP)                        │
    │  • Reusable everywhere                         │
    │  • Validates & transforms data                 │
    │  • Handles errors                              │
    │  • Interacts with database                     │
    │                                                │
    └────────────────────────────────────────────────┘
                         ↓
              Database Operations
                         ↓
    ┌────────────────────────────────────────────────┐
    │  DATABASE (PostgreSQL/SQLite)                  │
    │  ├─ usuarios table                             │
    │  ├─ datasets table                             │
    │  ├─ data table                                 │
    │  └─ ml_models table                            │
    └────────────────────────────────────────────────┘
```

---

## 📋 Detailed Comparison Table

| Aspect | FileService | files.py | datasets.py |
|--------|------------|----------|------------|
| **File Location** | `app/services/file_service.py` | `app/api/v1/endpoints/files.py` | `app/api/v1/endpoints/datasets.py` |
| **Type** | Service Class | FastAPI Routes | FastAPI Routes |
| **Knows HTTP** | ❌ No | ✅ Yes | ✅ Yes |
| **HTTP Methods** | N/A | POST, GET, DELETE | GET only |
| **Reusable** | ✅ Yes (anywhere) | ❌ No (HTTP only) | ❌ No (HTTP only) |
| **Validation** | ✅ Complete | ✅ Delegates to service | ✅ Delegates to service |
| **Data Processing** | ✅ Transforms | ❌ Not here | ❌ Not here |
| **Database Ops** | ✅ Direct | ❌ Via service | ❌ Via service |
| **Response Format** | Returns Python objects | Formats to JSON | Formats to simplified JSON |
| **Error Handling** | Raises HTTPException | Catches & returns HTTP errors | Catches & returns HTTP errors |
| **Authentication** | ❌ Doesn't know about it | ✅ Uses dependency injection | ✅ Uses dependency injection |
| **Testable** | ✅ Easy (pure functions) | ⚠️ Harder (FastAPI deps) | ⚠️ Harder (FastAPI deps) |

---

## 🎓 Design Pattern: "Services Layer"

This architecture follows the **Services Layer pattern**:

```
┌─────────────────────────────────────┐
│  PRESENTATION LAYER                 │
│  (HTTP Endpoints)                   │
│  - Receive requests                 │
│  - Handle authentication            │
│  - Format responses                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  BUSINESS LOGIC LAYER               │
│  (Services)                         │
│  - Validate data                    │
│  - Transform data                   │
│  - Execute business rules           │
│  - Interact with data layer         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  DATA ACCESS LAYER                  │
│  (Database/Models)                  │
│  - Define models                    │
│  - Execute queries                  │
└─────────────────────────────────────┘
```

### Benefits of This Pattern

✅ **Separation of Concerns**
- Each layer has single responsibility
- Endpoints don't contain business logic
- Services don't know about HTTP

✅ **Reusability**
- Services can be called from multiple places
- Same logic for HTTP, CLI, background jobs
- Easy to share between endpoints

✅ **Testability**
- Services are easy to unit test
- No HTTP framework dependencies
- Can mock database for testing

✅ **Maintainability**
- Changes to business logic don't affect endpoints
- Changes to HTTP format don't affect logic
- Clear structure for new developers

✅ **Scalability**
- Easy to add new endpoints
- Easy to add new services
- Easy to refactor without breaking

---

## 🔄 Real-World Example

### Scenario: Upload a CSV file

```
1. FRONTEND sends HTTP POST request
   POST /api/v1/files/upload
   file: sales_data.csv

2. files.py endpoint receives it
   @router.post("/upload")
   async def upload_file(file: UploadFile, current_user, db):
       # ✅ Got the request
       # ✅ Got authenticated user: user_id=5
       # ✅ Call the service to do the work
       result = await FileService.upload_file(file, 5, db)
       
       # ✅ Format response
       return {
           "message": "File uploaded",
           "dataset": result["dataset"],
           "entries_count": 1000
       }

3. FileService.upload_file() does the work
   @staticmethod
   async def upload_file(file, user_id=5, db):
       # ✅ Read file bytes
       file_content = await file.read()
       
       # ✅ Validate type
       if not validate_file_type(file.filename):
           raise HTTPException(...)
       
       # ✅ Validate size
       if not validate_file_size(file_content):
           raise HTTPException(...)
       
       # ✅ Parse file (CSV/XLSX)
       df = pd.read_csv(BytesIO(file_content))
       
       # ✅ Auto-detect columns
       date_col = find_date_column(df)
       numeric_col = find_numeric_column(df)
       
       # ✅ Create dataset in database
       dataset = Dataset(user_id=5, name=file.filename)
       db.add(dataset)
       db.commit()
       
       # ✅ Create data entries
       for idx, row in df.iterrows():
           data = Data(
               dataset_id=dataset.id,
               DS=row[date_col],
               y=row[numeric_col]
           )
           db.add(data)
       db.commit()
       
       return {"dataset": dataset, "data_entries": data_list}

4. Response sent back to frontend
   {
       "message": "File uploaded",
       "dataset": {
           "id": 42,
           "user_id": 5,
           "name": "sales_data.csv"
       },
       "entries_count": 1000
   }
```

---

## 🎯 When to Use Each

### FileService
Use when:
- Implementing business logic
- Multiple endpoints need same logic
- Writing unit tests
- Creating background jobs
- Building CLI commands
- Any reusable operation

### Endpoints (files.py, datasets.py)
Use when:
- Defining HTTP routes
- Handling HTTP-specific concerns
- Authentication & authorization
- Formatting JSON responses
- Mapping HTTP to business logic

---

## 💡 Key Takeaway

```
FileService = WHAT TO DO (business logic)
Endpoints = HOW TO COMMUNICATE (HTTP protocol)

FileService is reusable everywhere.
Endpoints are specific to HTTP.
```

---

## 🔗 Application to ML System

The same pattern applies to your ML models:<br/>

**MLStorageService** (business logic - what to do)
```python
class MLStorageService:
    @staticmethod
    def create_model_directory(user_id, dataset_id, model_name):
        # Pure logic: create directory structure
        pass
    
    @staticmethod
    def delete_model_directory(user_id, dataset_id, model_name):
        # Pure logic: delete directory
        pass
```

**ml.py endpoints** (HTTP - how to communicate)
```python
@router.post("")
async def create_ml_model(model_data, current_user, db):
    # ✅ Handle HTTP request
    # ✅ Call MLStorageService to do work
    # ✅ Format JSON response
    pass
```

This is the **same architecture pattern**!

---

## 📚 Summary

| Layer | Purpose | Example |
|-------|---------|---------|
| **Endpoints** | HTTP Communication | Route handler that receives request |
| **Services** | Business Logic | Validation, transformation, database ops |
| **Models** | Data Storage | SQLAlchemy ORM classes |

When building new features:

1. **Define the logic** in services (reusable)
2. **Expose via endpoints** (HTTP-specific)
3. **Trust they work together** seamlessly
