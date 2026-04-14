from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from functools import wraps
import json
from typing import Any
# Именованные импорты из schemas
from backend.app.schemas import (
    UserCreate,
    UserResponse,
    EquipmentWithDetailsResponse,
    LocationResponse,
    EquipmentTypeResponse,
    LocationCreate,
    EquipmentFullCreate,
    ElectricMotorCreate,
    MachineToolCreate,
    PumpCreate,
    SUserAuth,
    EquipmentTypeSearch,
    EquipmentFullUpdate,
    EquipmentSearch
)

# Именованные импорты из models
from backend.app.models import (
    User,
    Equipment,
    Location,
    EquipmentType,
    EquipmentFiles,
    ElectricMotor,
    MachineTool,
    Pump
)
from backend.app.database import engine, SessionLocal
from typing import List
from sqlalchemy.orm import Session, joinedload

import uuid
import os
import aiofiles
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _convert_value_for_comparison(value_str: str, target_value: Any) -> Any:
    """
    Преобразует строковое значение в тип, соответствующий целевому значению.
    
    Args:
        value_str: Строковое значение для преобразования
        target_value: Целевое значение для определения типа
    
    Returns:
        Any: Преобразованное значение
    """
    if target_value is None:
        return value_str
    
    # Пробуем преобразовать в int
    if isinstance(target_value, int):
        try:
            return int(value_str)
        except ValueError:
            return value_str
    
    # Пробуем преобразовать в float
    if isinstance(target_value, float):
        try:
            return float(value_str)
        except ValueError:
            return value_str
    
    # Пробуем преобразовать в bool
    if isinstance(target_value, bool):
        if value_str.lower() in ('true', '1', 'yes', 'on'):
            return True
        if value_str.lower() in ('false', '0', 'no', 'off'):
            return False
        return value_str
    
    # Оставляем как строку
    return value_str

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# по хорошему тут должена быть имортация Secret Key из .env, но я просто вставил сам сескрет для простоты
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode,'gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt')
    return encode_jwt

def authenticate_user(login: str, password: str, db):
    user =  db.query(User).filter(User.login == login).first()
    if not user or verify_password(plain_password=password, hashed_password=user.hash_password) is False:
        return None
    return user

def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token
def get_current_user( db: Session = Depends(get_db), token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, 'gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен не валидный!')

    expire = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Токен истек')

    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Не найден ID пользователя')

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    return user
# Функция для получения сессии БД (будем использовать в зависимостях FastAPI)
def token_admin_req(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        if request.method == "OPTIONS":
            return await func(request, *args, **kwargs)
        try:
            token = request.cookies.get('users_access_token')
            if not token:  # добавить эту проверку
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Токен не найден'
                )
            payload = jwt.decode(token, 'gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt')
            user_is_admin = payload.get('rule')
            if user_is_admin == False:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Требуются права администратора!'
                )
            return await func(request, *args, **kwargs)
        except HTTPException:
            raise

    return wrapper

app = FastAPI(
    title="Warehouse Catalog"
)
# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8000",  # Добавить бэкенд адреса
        "http://localhost:8000",
    ],
    allow_credentials=True,  # ВАЖНО: для работы с cookie
    allow_methods=["*"],      # Разрешаем все методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],      # Разрешаем все заголовки
    expose_headers=["Content-Disposition"],  
)
@app.post("/login/")
async def auth_user(response: Response, user_data: SUserAuth, db:  Session = Depends(get_db)):
    check = authenticate_user(login=user_data.login, password=user_data.password, db=db)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')
    access_token = create_access_token({"sub": str(check.id), "rule": bool(check.is_admin)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {'access_token': access_token, 'refresh_token': None}

@app.post("/logout/")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {'message': 'Пользователь успешно вышел из системы'}

@app.get("/me/", response_model=UserResponse)
async def get_me( user_data: User = Depends(get_current_user))-> UserResponse:
    return user_data
# Базовый эндпоинт для проверки работы
@app.get("/")
async def root():
    return {
        "message": "Warehouse Catalog API",
        "status": "running"
    }

@app.get("/health")
@token_admin_req
async def health_check(request: Request):
    return {"status": "healthy"}


#вывод всех записей в соответсвующих таблицах 
@app.get("/users", response_model=List[UserResponse])
@token_admin_req
async def show_users(request: Request, db: Session = Depends(get_db))-> List[UserResponse]:
    return db.query(User).all()

# предоставляет полную информацию про оборудование(местоположение, тип, файлы, вторичные характеристики)
@app.get("/equipment", response_model=List[EquipmentWithDetailsResponse])
async def show_equipment(db: Session = Depends(get_db)) -> List[EquipmentWithDetailsResponse]:
    equipment= db.query(Equipment).options(joinedload(Equipment.location),
                                           joinedload(Equipment.equipment_files),
                                           joinedload(Equipment.equipment_type),
                                           joinedload(Equipment.electric_motor),
                                           joinedload(Equipment.machine_tool),
                                           joinedload(Equipment.pump)).all()
    return equipment



#вывод всех записей в соответсвующих таблицах + считает сколько хранитися на складе( счиате количесво своих id в общей таблице с оборудованием)
@app.get("/locations", response_model=List[LocationResponse])
async def show_locations(db: Session = Depends(get_db))-> List[LocationResponse]:
    return db.query(Location).order_by(Location.workshop_number).all()

#вывод всех записей в соответсвующих таблицах 
@app.get("/types", response_model=List[EquipmentTypeResponse])
async def show_types(db: Session = Depends(get_db))-> List[EquipmentTypeResponse]:
    return db.query(EquipmentType).all()

# --- Новые эндпоинты для работы с файлами ---

@app.post("/equipment/{equipment_id}/upload/passport")
#@token_admin_req
async def upload_passport(
    request: Request,
    equipment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Загрузка паспорта оборудования"""
    return await _upload_file(request, equipment_id, file, db, file_type="passport")


@app.post("/equipment/{equipment_id}/upload/documentation")
#@token_admin_req
async def upload_documentation(
    request: Request,
    equipment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Загрузка документации оборудования"""
    return await _upload_file(request, equipment_id, file, db, file_type="documentation")


async def _upload_file(request: Request, equipment_id: int, file: UploadFile, db: Session, file_type: str):
    """Общая логика загрузки файла"""
    # Проверяем существование оборудования
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Проверяем расширение файла
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}")

    # Проверяем размер файла
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл слишком большой. Максимум 20 МБ")

    # Генерируем уникальное имя
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # Сохраняем файл на диск
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Получаем запись о файлах оборудования
    equipment_files = db.query(EquipmentFiles).filter(
        EquipmentFiles.document_id == equipment.document_id
    ).first()

    # Удаляем старый файл с диска если он был
    old_name = getattr(equipment_files, f"{file_type}_unique_name")
    if old_name:
        old_path = os.path.join(UPLOAD_DIR, old_name)
        if os.path.exists(old_path):
            os.remove(old_path)

    # Обновляем имя в БД
    setattr(equipment_files, f"{file_type}_unique_name", unique_name)
    db.commit()

    return {
        "message": "Файл успешно загружен",
        "unique_name": unique_name,
        "original_name": file.filename,
        "file_type": file_type
    }


@app.get("/equipment/{equipment_id}/download/passport")
async def download_passport(equipment_id: int, db: Session = Depends(get_db)):
    """Скачивание паспорта оборудования"""
    return _download_file(equipment_id, db, file_type="passport")


@app.get("/equipment/{equipment_id}/download/documentation")
async def download_documentation(equipment_id: int, db: Session = Depends(get_db)):
    """Скачивание документации оборудования"""
    return _download_file(equipment_id, db, file_type="documentation")


def _download_file(equipment_id: int, db: Session, file_type: str):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    equipment_files = db.query(EquipmentFiles).filter(
        EquipmentFiles.document_id == equipment.document_id
    ).first()

    unique_name = getattr(equipment_files, f"{file_type}_unique_name")
    if not unique_name:
        raise HTTPException(status_code=404, detail="Файл не найден")

    file_path = os.path.join(UPLOAD_DIR, unique_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл отсутствует на сервере")

    # Расширение берём из UUID-имени которое хранится в БД
    ext = os.path.splitext(unique_name)[1]  # например .pdf
    download_filename = f"{file_type}_{equipment_id}{ext}"  # passport_5.pdf
    return FileResponse(
        path=file_path,
        filename=download_filename,
        media_type="application/octet-stream"
    )

@app.delete("/equipment/{equipment_id}/delete/passport")
@token_admin_req
async def delete_passport(request: Request, equipment_id: int, db: Session = Depends(get_db)):
    return _delete_file(equipment_id, db, file_type="passport")


@app.delete("/equipment/{equipment_id}/delete/documentation")
@token_admin_req
async def delete_documentation(request: Request, equipment_id: int, db: Session = Depends(get_db)):
    return _delete_file(equipment_id, db, file_type="documentation")


def _delete_file(equipment_id: int, db: Session, file_type: str):
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    equipment_files = db.query(EquipmentFiles).filter(
        EquipmentFiles.document_id == equipment.document_id
    ).first()

    unique_name = getattr(equipment_files, f"{file_type}_unique_name")
    if not unique_name:
        raise HTTPException(status_code=404, detail="Файл уже отсутствует")

    file_path = os.path.join(UPLOAD_DIR, unique_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    setattr(equipment_files, f"{file_type}_unique_name", "")
    db.commit()

    return {"message": "Файл успешно удалён"}

# поиск по названию оборудования
@app.post("/search")
async def search(name: EquipmentSearch , db: Session = Depends(get_db))-> List[EquipmentWithDetailsResponse]:
    """
    Находит оборудование по названию
    
    """
    equipment_list=   db.query(Equipment).where(Equipment.name.like(f"%{name.name}%")).all()
    return equipment_list

# поиск по характеристикам оборудования внутри категории
@app.post("/search/type")
async def search_in_type(search_parametr: EquipmentTypeSearch , db: Session = Depends(get_db))-> List[EquipmentWithDetailsResponse]:
    
    """
    Находит оборудование по указанному полю и значению.
    
    Args:
        equipment_list: Список объектов Equipment для поиска
        key: Имя поля (например, "inlet_diameter_mm")
        value: Значение поля в виде строки
    
    Returns:
        List[Equipment]: Список найденных объектов
    """
    result = []
    equipment_list=  db.query(Equipment).options(joinedload(Equipment.location),
                                           joinedload(Equipment.equipment_files),
                                           joinedload(Equipment.equipment_type),
                                           joinedload(Equipment.electric_motor),
                                           joinedload(Equipment.machine_tool),
                                           joinedload(Equipment.pump)).all()
    for equipment in equipment_list:
        # Получаем значение атрибута из объекта
        if hasattr(equipment, search_parametr.key):
            attr_value = getattr(equipment, search_parametr.key)
            
            # Преобразуем значение из строки в соответствующий тип для сравнения
            converted_value = _convert_value_for_comparison(search_parametr.value, attr_value)
            
            # Сравниваем значения
            if attr_value == converted_value:
                result.append(equipment)
        else:
            # Проверяем в связанных объектах (например, electric_motor, machine_tool, pump)
            related_objects = ['electric_motor', 'machine_tool', 'pump']
            for related in related_objects:
                related_obj = getattr(equipment, related, None)
                if related_obj and hasattr(related_obj, search_parametr.key):
                    attr_value = getattr(related_obj, search_parametr.key)
                    converted_value = _convert_value_for_comparison(search_parametr.value, attr_value)
                    if attr_value == converted_value:
                        result.append(equipment)
                        break
    
    return result




    

# авторизация
@app.get("/auth")
async def auth()-> UserResponse:
    pass

# добавление записи в таблицу с пользователями
@app.post("/user/add", response_model=UserResponse)
@token_admin_req
async def add_user(request: Request, user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    # Проверка уникальности логина
    existing_user = db.query(User).filter(User.login == user.login).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Login already exists")
    
    db_user=User(last_name=user.last_name,first_name=user.first_name,middle_name=user.middle_name,login=user.login,hash_password= get_password_hash(user.password), is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
from sqlalchemy.exc import SQLAlchemyError

## добавление записи в таблицу с оборудованием + сразу же добавление записи в таблицу со вторичной информацией + загружается файл(не добавлено).
@app.post("/equipment/add", response_model=EquipmentWithDetailsResponse)
#@token_admin_req
async def add_equipment(request: Request, equipment: EquipmentFullCreate, db: Session = Depends(get_db)) -> EquipmentWithDetailsResponse:
    # Начинаем транзакцию
    try:
        # Проверка существования локации
        existing_place = db.query(Location).filter(Location.place_id == equipment.place_id).first()
        if existing_place is None:
            raise HTTPException(status_code=400, detail="Location not exists")
        
        # Проверка существования типа
        existing_type = db.query(EquipmentType).filter(EquipmentType.type_id == equipment.type_id).first()
        if existing_type is None:
            raise HTTPException(status_code=400, detail="Type not exists")
        
        # 1. Создаем запись о файлах
        db_file = EquipmentFiles(
            passport_unique_name=equipment.passport_unique_name,
            documentation_unique_name=equipment.documentation_unique_name
        )
        db.add(db_file)
        db.flush()  # Получаем ID без коммита
        
        # 2. Создаем запись об оборудовании
        db_equipment = Equipment(
            name=equipment.name,
            document_id=db_file.document_id,
            type_id=equipment.type_id,
            place_id=equipment.place_id,
            is_used=equipment.is_used 
        )
        db.add(db_equipment)
        db.flush()  # Получаем ID без коммита
        
        # 3. Создаем запись специфического типа оборудования
        if existing_type.name == 'electric_motor':
            db_specific = ElectricMotor(
                id=db_equipment.id,
                **equipment.electric_motor.model_dump()
            )
            db.add(db_specific)
        elif existing_type.name == 'machine_tool':
            db_specific = MachineTool(
                id=db_equipment.id,
                **equipment.machine_tool.model_dump()
            )
            db.add(db_specific)
        elif existing_type.name == 'pump':
            db_specific = Pump(
                id=db_equipment.id,
                **equipment.pump.model_dump()
            )
            db.add(db_specific)
        else:
            raise HTTPException(status_code=400, detail="Unknown equipment type")
        
        # Все операции успешны - делаем коммит
        db.commit()
        
        # Обновляем объекты после коммита
        db.refresh(db_file)
        db.refresh(db_equipment)
        if db_specific:
            db.refresh(db_specific)
        
        # Возвращаем созданное оборудование со всеми связями
        result = db.query(Equipment).options(
            joinedload(Equipment.location),
            joinedload(Equipment.equipment_files),
            joinedload(Equipment.equipment_type),
            joinedload(Equipment.electric_motor),
            joinedload(Equipment.machine_tool),
            joinedload(Equipment.pump)
        ).filter(Equipment.id == db_equipment.id).first()
        
        return result
        
    except SQLAlchemyError as e:
        # В случае любой ошибки БД - откатываем транзакцию
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        # Для HTTP исключений тоже откатываем
        db.rollback()
        raise
    except Exception as e:
        # Для всех остальных ошибок
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
## добавление записи в таблицу с оборудованием + сразу же добавление записи в таблицу со вторичной информацией + загружается файл. 
#@app.post("/equipment/add", response_model=EquipmentWithDetailsResponse)
#async def add_equipment(equipment: EquipmentFullCreate, db: Session = Depends(get_db)) -> EquipmentWithDetailsResponse:
#    existing_place = db.query(Location).filter(Location.place_id==equipment.place_id).first()
#    if existing_place is None:
#        raise HTTPException(status_code=400, detail="Location not exists")
#    
#    existing_type = db.query(EquipmentType).filter(EquipmentType.type_id==equipment.type_id).first()
#    if existing_type is None:
#        raise HTTPException(status_code=400, detail="Type not exists")
#    db_file=EquipmentFiles(passport_unique_name=equipment.passport_unique_name, documentation_unique_name=equipment.documentation_unique_name)
#    db.add(db_file)
#    db.commit()
#    db.refresh(db_file)
#
#    db_equipment=Equipment(name= equipment.name, document_id=db_file.document_id, type_id=equipment.type_id, place_id=equipment.place_id)
#    db.add(db_equipment)
#    db.commit()
#    db.refresh(db_equipment)
#
#    if existing_type.name=='electric_motor':
#        db_electric_motor=ElectricMotor(id=db_equipment.id,**equipment.electric_motor.model_dump())
#        db.add(db_electric_motor)
#        db.commit()
#        db.refresh(db_electric_motor)
#    elif existing_type.name=='machine_tool':
#        db_machine_tool=MachineTool(id=db_equipment.id,**equipment.machine_tool.model_dump())
#        db.add(db_machine_tool)
#        db.commit()
#        db.refresh(db_machine_tool)
#    elif existing_type.name=='pump':
#        db_pump=Pump(id=db_equipment.id,**equipment.pump.model_dump())
#        db.add(db_pump)
#        db.commit()
#        db.refresh(db_pump)
#    return db.query(Equipment).options(joinedload(Equipment.location),
#                                           joinedload(Equipment.equipment_files),
#                                           joinedload(Equipment.equipment_type),
#                                           joinedload(Equipment.electric_motor),
#                                           joinedload(Equipment.machine_tool),
#                                           joinedload(Equipment.pump)).where(Equipment.id==db_equipment.id).first()
#    
#
# добавление записи в таблицу с местоположением с новым номером цеха(ищется максимальный существующий номер цеха и увеличивается на 1) + у цеха сразу создаётся один склад
@app.post("/location/add_workshop", response_model=LocationResponse)
@token_admin_req
async def add_workshop(request: Request, location: LocationCreate, db: Session = Depends(get_db)) -> LocationResponse:
    new_workshop_number=db.query(func.max(Location.workshop_number)).scalar()+1
    db_location=Location(workshop_number=new_workshop_number, warehouse_number= 1)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

# добавление записи в таблицу с местоположением с текущим номером цеха(передаётся в параметрах) нового склада(ищется максимальный существующий номер склада и увеличивается на 1)
@app.post("/location/add_warehouse", response_model=LocationResponse)
@token_admin_req
async def add_warehouse(request: Request, location: LocationCreate, db: Session = Depends(get_db)) -> LocationResponse:
    existing_workshop = db.query(Location).filter(Location.workshop_number==location.workshop_number).first()
    if existing_workshop is None:
        raise HTTPException(status_code=400, detail="Workshop not exists")
    new_warehouse_number=db.query(func.max(Location.warehouse_number)).filter(Location.workshop_number==location.workshop_number).scalar()+1
    db_location=Location(workshop_number=location.workshop_number, warehouse_number= new_warehouse_number)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@app.put("/equipment/{equipment_id}", response_model=EquipmentWithDetailsResponse)
#@token_admin_req
async def change_equipment(
    request: Request,
    equipment_id: int,
    equipment_data: EquipmentFullUpdate,
    db: Session = Depends(get_db)
) -> EquipmentWithDetailsResponse:
    try:
        # Загружаем оборудование
        db_equipment = db.query(Equipment).options(
            joinedload(Equipment.location),
            joinedload(Equipment.equipment_files),
            joinedload(Equipment.equipment_type),
            joinedload(Equipment.electric_motor),
            joinedload(Equipment.machine_tool),
            joinedload(Equipment.pump)
        ).filter(Equipment.id == equipment_id).first()

        if not db_equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        if equipment_data.is_used is not None:
            db_equipment.is_used = equipment_data.is_used
        # Обновляем название
        if equipment_data.name is not None:
            db_equipment.name = equipment_data.name

        # Обновляем местоположение
        if equipment_data.place_id is not None:
            existing_place = db.query(Location).filter(
                Location.place_id == equipment_data.place_id
            ).first()
            if not existing_place:
                raise HTTPException(status_code=400, detail="Location not exists")
            db_equipment.place_id = equipment_data.place_id

        # Обновляем тип и характеристики
        if equipment_data.type_id is not None:
            existing_type = db.query(EquipmentType).filter(
                EquipmentType.type_id == equipment_data.type_id
            ).first()
            if not existing_type:
                raise HTTPException(status_code=400, detail="Type not exists")

            old_type_name = db_equipment.equipment_type.name
            new_type_name = existing_type.name

            # Если тип изменился — удаляем старые характеристики
            if old_type_name != new_type_name:
                if old_type_name == 'electric_motor' and db_equipment.electric_motor:
                    db.delete(db_equipment.electric_motor)
                elif old_type_name == 'machine_tool' and db_equipment.machine_tool:
                    db.delete(db_equipment.machine_tool)
                elif old_type_name == 'pump' and db_equipment.pump:
                    db.delete(db_equipment.pump)
                db.flush()

            db_equipment.type_id = equipment_data.type_id

            # Создаём или обновляем характеристики
            if new_type_name == 'electric_motor' and equipment_data.electric_motor:
                if db_equipment.electric_motor and old_type_name == 'electric_motor':
                    for k, v in equipment_data.electric_motor.model_dump().items():
                        setattr(db_equipment.electric_motor, k, v)
                else:
                    db.add(ElectricMotor(
                        id=equipment_id,
                        **equipment_data.electric_motor.model_dump()
                    ))
            elif new_type_name == 'machine_tool' and equipment_data.machine_tool:
                if db_equipment.machine_tool and old_type_name == 'machine_tool':
                    for k, v in equipment_data.machine_tool.model_dump().items():
                        setattr(db_equipment.machine_tool, k, v)
                else:
                    db.add(MachineTool(
                        id=equipment_id,
                        **equipment_data.machine_tool.model_dump()
                    ))
            elif new_type_name == 'pump' and equipment_data.pump:
                if db_equipment.pump and old_type_name == 'pump':
                    for k, v in equipment_data.pump.model_dump().items():
                        setattr(db_equipment.pump, k, v)
                else:
                    db.add(Pump(
                        id=equipment_id,
                        **equipment_data.pump.model_dump()
                    ))

        db.commit()

        # Возвращаем обновлённый объект
        return db.query(Equipment).options(
            joinedload(Equipment.location),
            joinedload(Equipment.equipment_files),
            joinedload(Equipment.equipment_type),
            joinedload(Equipment.electric_motor),
            joinedload(Equipment.machine_tool),
            joinedload(Equipment.pump)
        ).filter(Equipment.id == equipment_id).first()

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@app.delete("/equipment/{equipment_id}")
#@token_admin_req
async def delete_equipment(request: Request, equipment_id: int, db: Session = Depends(get_db)):
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # Удаляем файлы с диска
    files = db.query(EquipmentFiles).filter(
        EquipmentFiles.document_id == db_equipment.document_id
    ).first()
    if files:
        for name in [files.passport_unique_name, files.documentation_unique_name]:
            if name:
                path = os.path.join(UPLOAD_DIR, name)
                if os.path.exists(path):
                    os.remove(path)

    db.delete(db_equipment)
    db.commit()
    return {"message": "Оборудование удалено"}