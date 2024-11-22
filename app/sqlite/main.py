from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from fastapi.staticfiles import StaticFiles
import os

# Konfigurasi Database (SQLite)
DATABASE_URL = "sqlite:///./DB/fastApi.db"
CustomerMsg = 'Customer not found'

# Koneksi ke Database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base untuk ORM
Base = declarative_base()

# Model untuk Tabel
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(15), index=True)

# Membuat Tabel jika belum ada
Base.metadata.create_all(bind=engine)

# Inisialisasi FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan semua domain (gunakan domain spesifik di produksi)
    allow_credentials=True,
    allow_methods=["*"],  # Mengizinkan semua metode HTTP (GET, POST, PUT, DELETE, dll.)
    allow_headers=["*"],  # Mengizinkan semua header
)

# Dependency untuk Session Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Mount static files untuk file HTML dan assets
app.mount("/static", StaticFiles(directory="./frontend", html=True), name="static")
app.mount("/assets", StaticFiles(directory="./frontend/assets"), name="assets")

# Fungsi untuk membaca file HTML
def get_html(file_name: str) -> HTMLResponse:
    file_path = os.path.join("./frontend", f"{file_name}.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read(), status_code=200)
    return HTMLResponse(content="<h1>404 Not Found</h1>", status_code=404)

# Route utama
@app.get("/pages", response_class=HTMLResponse)
async def read_root():
    return get_html("home")

# Route untuk setiap halaman
@app.get("/pages/{page_name}", response_class=HTMLResponse)
async def read_page(page_name: str):
    return get_html(page_name)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Customer API"}

@app.get("/customers/{cust_id}")
def get_customer(cust_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk mendapatkan detail customer berdasarkan ID.
    """
    customer = db.query(Customer).filter(Customer.id == cust_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=CustomerMsg)
    return {"id": customer.id, "name": customer.name, "email": customer.email, "phone": customer.phone}

@app.get("/customers")
def get_all_customers(db: Session = Depends(get_db)):
    """
    Endpoint untuk mendapatkan semua data customer.
    """
    customers = db.query(Customer).all()
    if not customers:
        raise HTTPException(status_code=404, detail=CustomerMsg)
    return customers

@app.post("/customers")
def create_customer(name: str, email: str, phone: str, db: Session = Depends(get_db)):
    """
    Endpoint untuk menambahkan customer baru.
    """
    existing_customer = db.query(Customer).filter(Customer.email == email).first()
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")

    new_customer = Customer(name=name, email=email, phone=phone)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return {"message": "Customer created successfully", "customer": new_customer}

@app.put("/customers/{cust_id}")
def update_customer(cust_id: int, name: str, email: str, phone: str, db: Session = Depends(get_db)):
    """
    Endpoint untuk memperbarui data customer berdasarkan ID.
    """
    customer = db.query(Customer).filter(Customer.id == cust_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=CustomerMsg)

    customer.name = name
    customer.email = email
    customer.phone = phone
    db.commit()
    db.refresh(customer)
    return {"message": "Customer updated successfully", "customer": customer}

@app.delete("/customers/{cust_id}")
def delete_customer(cust_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk menghapus customer berdasarkan ID.
    """
    customer = db.query(Customer).filter(Customer.id == cust_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=CustomerMsg)

    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
