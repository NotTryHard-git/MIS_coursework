# backend/models/all_models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, BigInteger, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Equipment(Base):
    __tablename__ = "equipment"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    place_id = Column(Integer, ForeignKey("public.location.place_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("public.equipment_files.document_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    type_id = Column(Integer, ForeignKey("public.equipment_type.type_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    # Связи - добавьте cascade и passive_deletes
    location = relationship("Location", back_populates="equipment")
    equipment_files = relationship("EquipmentFiles", back_populates="equipment")
    equipment_type = relationship("EquipmentType", back_populates="equipment")
    
    # Измените эти строки
    electric_motor = relationship(
        "ElectricMotor", 
        back_populates="equipment", 
        uselist=False,
        cascade="all, delete-orphan",  # Добавлено
        passive_deletes=True  # Добавлено
    )
    machine_tool = relationship(
        "MachineTool", 
        back_populates="equipment", 
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    pump = relationship(
        "Pump", 
        back_populates="equipment", 
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
class EquipmentFiles(Base):
    __tablename__ = "equipment_files"
    __table_args__ = {"schema": "public"}
    
    document_id = Column(Integer, primary_key=True, autoincrement=True)
    passport_unique_name = Column(String(255), nullable=False, unique=True)
    documentation_unique_name = Column(String(255), nullable=False, unique=True)
    
    # Связи
    equipment = relationship("Equipment", back_populates="equipment_files")
    
    def __repr__(self):
        return f"<EquipmentFiles(document_id={self.document_id}, passport={self.passport_unique_name})>"


class EquipmentType(Base):
    __tablename__ = "equipment_type"
    __table_args__ = {"schema": "public"}
    
    type_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    
    # Связи
    equipment = relationship("Equipment", back_populates="equipment_type")
    
    def __repr__(self):
        return f"<EquipmentType(type_id={self.type_id}, name={self.name})>"


class Location(Base):
    __tablename__ = "location"
    __table_args__ = {"schema": "public"}
    
    place_id = Column(Integer, primary_key=True, autoincrement=True)
    workshop_number = Column(BigInteger, nullable=False)
    warehouse_number = Column(BigInteger, nullable=False)
    
    # Связи
    equipment = relationship("Equipment", back_populates="location")
    
    def __repr__(self):
        return f"<Location(place_id={self.place_id}, workshop={self.workshop_number}, warehouse={self.warehouse_number})>"


class ElectricMotor(Base):
    __tablename__ = "electric_motor"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, ForeignKey("public.equipment.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    power_kw = Column(Float, nullable=False)  # Изменено с Numeric на Float
    rated_current_a = Column(Float, nullable=False)  # Изменено с Numeric на Float
    rated_speed_rpm = Column(Integer, nullable=False)
    shaft_diameter_mm = Column(Integer, nullable=False)
    energy_efficiency_class = Column(String(10), nullable=False)
    
    # Связи
    equipment = relationship("Equipment", back_populates="electric_motor")
    
    def __repr__(self):
        return f"<ElectricMotor(id={self.id}, power={self.power_kw}kW)>"


class MachineTool(Base):
    __tablename__ = "machine_tool"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, ForeignKey("public.equipment.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    table_size_mm = Column(String(30), nullable=False)
    max_workpiece_weight_kg = Column(Float, nullable=False)  # Изменено с Numeric на Float
    rotation_speed_rpm = Column(Integer, nullable=False)
    axis_count = Column(Integer, nullable=False)
    accuracy_class = Column(String(20), nullable=False)
    
    # Связи
    equipment = relationship("Equipment", back_populates="machine_tool")
    
    def __repr__(self):
        return f"<MachineTool(id={self.id}, axis_count={self.axis_count})>"


class Pump(Base):
    __tablename__ = "pump"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, ForeignKey("public.equipment.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    capacity_m3_per_hour = Column(Float, nullable=False)  # Изменено с Numeric на Float
    engine_power_kw = Column(Float, nullable=False)  # Изменено с Numeric на Float
    voltage_v = Column(String(20), nullable=False)
    inlet_diameter_mm = Column(Integer, nullable=False)
    outlet_diameter_mm = Column(Integer, nullable=False)
    
    # Связи
    equipment = relationship("Equipment", back_populates="pump")
    
    def __repr__(self):
        return f"<Pump(id={self.id}, capacity={self.capacity_m3_per_hour}m³/h)>"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(30), nullable=False)
    first_name = Column(String(30), nullable=False)
    middle_name = Column(String(30), nullable=False)
    login = Column(String(30), nullable=False, unique=True)
    is_admin = Column(Boolean, nullable=False)
    hash_password = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, login={self.login}, name={self.last_name} {self.first_name})>"