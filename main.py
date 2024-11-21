from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Konfigurasi Database
DATABASE_URL = "mysql+pymysql://root@localhost/fastAPIDTT"

# Koneksi ke Database
engine = create_engine(DATABASE_URL)
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

# Membuat Tabel
Base.metadata.create_all(bind=engine)

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
    return {"Hello": "World"}

@app.get("/customer/{cust_id}")
def read_customer(cust_id: int, db: Session = Depends(get_db)):  # Perbaikan: Hilangkan ()
    customer = db.query(Customer).filter(Customer.id == cust_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"id": customer.id, "name": customer.name, "email": customer.email, "phone": customer.phone}
