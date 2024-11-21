from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Konfigurasi Database (Postgresql)
DATABASE_URL = "postgresql+psycopg2://gugugaga:password@localhost:5432/fastAPIDTT"

# Koneksi ke Database
engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Jumlah koneksi di pool
    max_overflow=20,  # Jumlah koneksi tambahan saat pool penuh
)

# Pastikan koneksi berhasil
with engine.connect() as connection:
    connection.execute(text("SELECT 1"))

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
Base.metadata.create_all(bind=engine,)

# Inisialisasi FastAPI
app = FastAPI()

# Dependency untuk Session Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"id": customer.id, "name": customer.name, "email": customer.email, "phone": customer.phone}

@app.get("/customers")
def get_all_customers(db: Session = Depends(get_db)):
    """
    Endpoint untuk mendapatkan semua data customer.
    """
    customers = db.query(Customer).all()
    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")
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
        raise HTTPException(status_code=404, detail="Customer not found")
    
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
        raise HTTPException(status_code=404, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
