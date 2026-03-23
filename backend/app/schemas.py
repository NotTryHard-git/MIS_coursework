# backend/schemas/all_schemas.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal


# ==================== EquipmentFiles ====================
class EquipmentFilesCreate(BaseModel):
    """Схема для создания файлов оборудования"""
    passport_unique_name: str = Field(default="", max_length=255, description="Уникальное имя файла паспорта")
    documentation_unique_name: str = Field(default="", max_length=255, description="Уникальное имя файла документации")
    
    @field_validator('passport_unique_name', 'documentation_unique_name')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Проверка безопасности имени файла"""
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Invalid filename: contains path traversal')
        return v
    


class EquipmentFilesResponse(BaseModel):
    """Схема для ответа с файлами оборудования"""
    document_id: int
    passport_unique_name: str
    documentation_unique_name: str
    
    model_config = ConfigDict(from_attributes=True)


# ==================== EquipmentType ====================
class EquipmentTypeCreate(BaseModel):
    """Схема для создания типа оборудования"""
    name: str = Field(..., min_length=1, max_length=50, description="Название типа оборудования")
    


class EquipmentTypeResponse(BaseModel):
    """Схема для ответа с типом оборудования"""
    type_id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Location ====================
class LocationCreate(BaseModel):
    """Схема для создания местоположения"""
    workshop_number: int = Field(..., ge=1, description="Номер цеха")
    warehouse_number: int = Field(..., ge=1, description="Номер склада")
    


class LocationResponse(BaseModel):
    """Схема для ответа с местоположением"""
    place_id: int
    workshop_number: int
    warehouse_number: int
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Equipment ====================
class EquipmentCreate(BaseModel):
    """Схема для создания оборудования"""
    name: str = Field(..., min_length=1, max_length=100, description="Название оборудования")
    place_id: int = Field(..., gt=0, description="ID местоположения")
    document_id: int = Field(..., gt=0, description="ID документа")
    type_id: int = Field(..., gt=0, description="ID типа оборудования")
    


class EquipmentResponse(BaseModel):
    """Схема для ответа с оборудованием"""
    id: int
    name: str
    place_id: int
    document_id: int
    type_id: int
    
    model_config = ConfigDict(from_attributes=True)


# ==================== ElectricMotor ====================
class ElectricMotorCreate(BaseModel):
    """Схема для создания электродвигателя"""
    id: int = Field(..., gt=0, description="ID оборудования")
    power_kw: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Мощность в кВт")
    rated_current_a: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Номинальный ток в А")
    rated_speed_rpm: int = Field(..., gt=0, description="Номинальная скорость в об/мин")
    shaft_diameter_mm: int = Field(..., gt=0, description="Диаметр вала в мм")
    energy_efficiency_class: str = Field(..., max_length=10, description="Класс энергоэффективности")
    


class ElectricMotorResponse(BaseModel):
    """Схема для ответа с электродвигателем"""
    id: int
    power_kw: Decimal
    rated_current_a: Decimal
    rated_speed_rpm: int
    shaft_diameter_mm: int
    energy_efficiency_class: str
    
    model_config = ConfigDict(from_attributes=True)


# ==================== MachineTool ====================
class MachineToolCreate(BaseModel):
    """Схема для создания станка"""
    id: int = Field(..., gt=0, description="ID оборудования")
    table_size_mm: str = Field(..., max_length=30, description="Размер стола в мм")
    max_workpiece_weight_kg: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Максимальный вес заготовки в кг")
    rotation_speed_rpm: int = Field(..., gt=0, description="Скорость вращения в об/мин")
    axis_count: int = Field(..., ge=1, le=10, description="Количество осей")
    accuracy_class: str = Field(..., max_length=20, description="Класс точности")
    


class MachineToolResponse(BaseModel):
    """Схема для ответа со станком"""
    id: int
    table_size_mm: str
    max_workpiece_weight_kg: Decimal
    rotation_speed_rpm: int
    axis_count: int
    accuracy_class: str
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Pump ====================
class PumpCreate(BaseModel):
    """Схема для создания насоса"""
    id: int = Field(..., gt=0, description="ID оборудования")
    capacity_m3_per_hour: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Производительность в м³/час")
    engine_power_kw: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Мощность двигателя в кВт")
    voltage_v: str = Field(..., max_length=20, description="Напряжение в В")
    inlet_diameter_mm: int = Field(..., gt=0, description="Диаметр входного отверстия в мм")
    outlet_diameter_mm: int = Field(..., gt=0, description="Диаметр выходного отверстия в мм")
    


class PumpResponse(BaseModel):
    """Схема для ответа с насосом"""
    id: int
    capacity_m3_per_hour: Decimal
    engine_power_kw: Decimal
    voltage_v: str
    inlet_diameter_mm: int
    outlet_diameter_mm: int
    
    model_config = ConfigDict(from_attributes=True)


# ==================== User ====================
class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    last_name: str = Field(..., min_length=1, max_length=30, description="Фамилия")
    first_name: str = Field(..., min_length=1, max_length=30, description="Имя")
    middle_name: str = Field(..., min_length=1, max_length=30, description="Отчество")
    login: str = Field(..., min_length=3, max_length=30, description="Логин")
    is_admin: bool = Field(..., description="Администратор ")
    hash_password: str = Field(..., min_length=6, max_length=255, description="Хеш пароля")
    
    
    


class UserResponse(BaseModel):
    """Схема для ответа с пользователем (без пароля)"""
    id: int
    last_name: str
    first_name: str
    middle_name: str
    login: str
    is_admin: bool
    
    model_config = ConfigDict(from_attributes=True)


# ==================== Расширенные схемы для Equipment с вложенными данными ====================
class EquipmentWithDetailsResponse(BaseModel):
    """Схема для ответа с оборудованием и всеми связанными данными"""
    id: int
    name: str
    location: LocationResponse
    equipment_files: EquipmentFilesResponse
    equipment_type: EquipmentTypeResponse
    electric_motor: Optional[ElectricMotorResponse] = None
    machine_tool: Optional[MachineToolResponse] = None
    pump: Optional[PumpResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


#class EquipmentFullCreate(BaseModel):
#    """Схема для создания оборудования со всеми связанными данными"""
#    # Основные данные оборудования
#    name: str = Field(..., min_length=1, max_length=100)
#    place_id: int = Field(..., gt=0)
#    type_id: int = Field(..., gt=0)
#    
#    # Данные файлов (опционально, можно создать отдельно)
#    passport_unique_name: Optional[str] = Field(None, max_length=255)
#    documentation_unique_name: Optional[str] = Field(None, max_length=255)
#    
#    # Данные для специфического типа оборудования (только одно из трёх)
#    electric_motor: Optional[ElectricMotorCreate] = None
#    machine_tool: Optional[MachineToolCreate] = None
#    pump: Optional[PumpCreate] = None
#    
#    @field_validator('electric_motor', 'machine_tool', 'pump')
#    @classmethod
#    def validate_only_one_type(cls, v, info):
#        """Проверка, что указан только один тип оборудования"""
#        values = info.data
#        types_count = sum([
#            1 if values.get('electric_motor') else 0,
#            1 if values.get('machine_tool') else 0,
#            1 if values.get('pump') else 0
#        ])
#        if types_count > 1:
#            raise ValueError('Only one equipment type (electric_motor, machine_tool, or pump) can be specified')
#        return v
    