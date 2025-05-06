"""
API simples e independente para o DataBridge Bank com endpoints CRUD.
Este arquivo serve como uma alternativa para testes rápidos no Insomnia.
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import uuid
import os
from pathlib import Path

# Modelos de dados simplificados para a API de teste
class ClientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientRead(ClientBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class TransactionBase(BaseModel):
    origin_account: str
    destination_account: str
    amount: float = Field(..., gt=0)
    currency: str = Field(..., example="BRL")
    transaction_type: str = Field(..., example="transfer")

class TransactionCreate(TransactionBase):
    description: Optional[str] = None
    reference_id: Optional[str] = None

class TransactionRead(TransactionBase):
    id: str
    status: str
    routing_info: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None

class MessageResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str = "online"
    version: str = "1.0.0"
    database: Dict[str, str] = {
        "postgres": "online",
        "mongodb": "online"
    }
    graphql: str = "online"
    messaging: Dict[str, str] = {
        "kafka": "online"
    }
    timestamp: datetime = Field(default_factory=datetime.now)

class FileUploadRead(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None

class FileUploadCreate(BaseModel):
    filename: str
    file_type: str

class DataRecordRead(BaseModel):
    id: str
    record_type: str
    content: str
    status: str
    created_at: datetime

# Armazenamento em memória para os testes
clients_db = {}
transactions_db = {}
files_db = {}
records_db = {}

# Criar aplicação FastAPI
app = FastAPI(
    title="DataBridge Bank API",
    description="API REST para o sistema DataBridge Bank - Ponte de dados financeiros",
    version="1.0.0"
)

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar API Router para versão v1
api_v1 = FastAPI(
    title="DataBridge Bank API",
    description="API REST para o sistema DataBridge Bank - Ponte de dados financeiros",
    version="1.0.0"
)

# Endpoint de boas-vindas na raiz
@app.get("/")
async def root():
    return {
        "name": "DataBridge Bank API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

# Servir arquivos estáticos do frontend
frontend_dir = Path("c:/Users/Cesar/OneDrive/Área de Trabalho/Data-Bridge-Bank/databridge/frontend")
if frontend_dir.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    @app.get("/frontend", response_class=HTMLResponse)
    async def serve_frontend():
        return FileResponse(str(frontend_dir / "index.html"))

# ------ API V1 Endpoints ------

# Endpoint de saúde do sistema
@api_v1.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verifica o status de saúde do sistema e seus componentes.
    """
    return HealthResponse()

# ------ Endpoints de Clientes ------
@api_v1.post("/clients", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate):
    """Cria um novo cliente no sistema."""
    client_id = str(uuid.uuid4())
    now = datetime.now()
    client_data = {
        "id": client_id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "tax_id": client.tax_id,
        "created_at": now,
        "updated_at": now
    }
    clients_db[client_id] = client_data
    return client_data

@api_v1.get("/clients", response_model=List[ClientRead])
async def list_clients(skip: int = 0, limit: int = 100):
    """Lista os clientes cadastrados no sistema."""
    return list(clients_db.values())[skip:skip+limit]

@api_v1.get("/clients/{client_id}", response_model=ClientRead)
async def get_client(client_id: str):
    """Obtém os detalhes de um cliente específico."""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return clients_db[client_id]

@api_v1.put("/clients/{client_id}", response_model=ClientRead)
async def update_client(client_id: str, client: ClientCreate):
    """Atualiza os dados de um cliente."""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    client_data = clients_db[client_id]
    client_data["name"] = client.name
    client_data["email"] = client.email
    client_data["phone"] = client.phone
    client_data["tax_id"] = client.tax_id
    client_data["updated_at"] = datetime.now()
    
    return client_data

@api_v1.delete("/clients/{client_id}", response_model=MessageResponse)
async def delete_client(client_id: str):
    """Remove um cliente do sistema."""
    if client_id not in clients_db:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    del clients_db[client_id]
    return {"message": f"Cliente {client_id} removido com sucesso"}

# ------ Endpoints de Transações ------
@api_v1.post("/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate):
    """Cria uma nova transação financeira."""
    transaction_id = str(uuid.uuid4())
    now = datetime.now()
    
    # Roteamento inteligente simplificado
    if transaction.amount > 10000:
        routing = {"route": "high_value", "priority": "high"}
    else:
        routing = {"route": "standard", "priority": "normal"}
    
    transaction_data = {
        "id": transaction_id,
        "origin_account": transaction.origin_account,
        "destination_account": transaction.destination_account,
        "amount": transaction.amount,
        "currency": transaction.currency,
        "transaction_type": transaction.transaction_type,
        "description": transaction.description,
        "reference_id": transaction.reference_id,
        "status": "pending",
        "routing_info": routing,
        "created_at": now,
        "updated_at": now
    }
    
    transactions_db[transaction_id] = transaction_data
    return transaction_data

@api_v1.get("/transactions", response_model=List[TransactionRead])
async def list_transactions(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    type: Optional[str] = None
):
    """Lista as transações financeiras com filtros opcionais."""
    transactions = list(transactions_db.values())
    
    # Aplicar filtros
    if status:
        transactions = [t for t in transactions if t["status"] == status]
    if type:
        transactions = [t for t in transactions if t["transaction_type"] == type]
    
    return transactions[skip:skip+limit]

@api_v1.get("/transactions/{transaction_id}", response_model=TransactionRead)
async def get_transaction(transaction_id: str):
    """Obtém os detalhes de uma transação específica."""
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return transactions_db[transaction_id]

@api_v1.put("/transactions/{transaction_id}", response_model=TransactionRead)
async def update_transaction(transaction_id: str, status: str):
    """Atualiza o status de uma transação."""
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    valid_statuses = ["pending", "processing", "completed", "failed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status inválido. Use um dos seguintes: {', '.join(valid_statuses)}")
    
    transaction_data = transactions_db[transaction_id]
    transaction_data["status"] = status
    transaction_data["updated_at"] = datetime.now()
    
    return transaction_data

@api_v1.delete("/transactions/{transaction_id}", response_model=MessageResponse)
async def delete_transaction(transaction_id: str):
    """Cancela uma transação (marcando como cancelada)."""
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    
    transaction_data = transactions_db[transaction_id]
    transaction_data["status"] = "cancelled"
    transaction_data["updated_at"] = datetime.now()
    
    return {"message": f"Transação {transaction_id} cancelada com sucesso"}

# ------ Endpoints de Arquivos ------
@api_v1.get("/files", response_model=List[FileUploadRead])
async def list_files(status: Optional[str] = None, file_type: Optional[str] = None):
    """Lista os arquivos com filtros opcionais."""
    files = list(files_db.values())
    
    # Aplicar filtros
    if status:
        files = [f for f in files if f["status"] == status]
    if file_type:
        files = [f for f in files if f["file_type"] == file_type]
    
    return files

@api_v1.get("/files/{file_id}", response_model=FileUploadRead)
async def get_file(file_id: str):
    """Obtém os detalhes de um arquivo específico."""
    if file_id not in files_db:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    return files_db[file_id]

@api_v1.post("/files/upload", response_model=List[FileUploadRead])
async def upload_files(files: List[FileUploadCreate]):
    """Faz upload de múltiplos arquivos com suas metainformações."""
    result = []
    
    for file in files:
        file_id = str(uuid.uuid4())
        now = datetime.now()
        
        file_data = {
            "id": file_id,
            "filename": file.filename,
            "file_type": file.file_type,
            "status": "pending",
            "created_at": now,
            "processed_at": None
        }
        
        files_db[file_id] = file_data
        
        # Criar alguns registros de exemplo para este arquivo
        for i in range(3):
            record_id = str(uuid.uuid4())
            record_data = {
                "id": record_id,
                "file_id": file_id,
                "record_type": f"record_type_{i+1}",
                "content": f'{{"field1": "value{i+1}", "field2": {i+10}, "amount": {1000*(i+1)}}}',
                "status": "processed",
                "created_at": now
            }
            records_db[record_id] = record_data
        
        # Atualizar o status do arquivo após criar os registros
        file_data["status"] = "processed"
        file_data["processed_at"] = datetime.now()
        
        result.append(file_data)
    
    return result

@api_v1.post("/files/{file_id}/process", response_model=FileUploadRead)
async def process_file(file_id: str):
    """Processa um arquivo que esteja no status pendente."""
    if file_id not in files_db:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    file_data = files_db[file_id]
    file_data["status"] = "processing"
    
    # Simulação de processamento
    file_data["status"] = "processed"
    file_data["processed_at"] = datetime.now()
    
    return file_data

# ------ Endpoints de Registros ------
@api_v1.get("/records", response_model=List[DataRecordRead])
async def list_records(file_id: Optional[str] = None, record_type: Optional[str] = None):
    """Lista os registros de dados com filtros opcionais."""
    records = list(records_db.values())
    
    # Aplicar filtros
    if file_id:
        records = [r for r in records if r["file_id"] == file_id]
    if record_type:
        records = [r for r in records if r["record_type"] == record_type]
    
    return records

@api_v1.get("/records/{record_id}", response_model=DataRecordRead)
async def get_record(record_id: str):
    """Obtém os detalhes de um registro específico."""
    if record_id not in records_db:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    return records_db[record_id]

# Incluir a API v1 como um submount
app.mount("/api/v1", api_v1)

# Iniciar a API se executada diretamente
if __name__ == "__main__":
    print("\n" + "="*60)
    print(" "*15 + "API DATABRIDGE SIMPLIFICADA" + " "*15)
    print("="*60 + "\n")
    print("Iniciando API de teste do DataBridge Bank...")
    print("URL da API: http://127.0.0.1:8000")
    print("API v1: http://127.0.0.1:8000/api/v1")
    print("Documentação Swagger: http://127.0.0.1:8000/docs")
    print("Frontend disponível em: http://127.0.0.1:8000/frontend")
    print("\nPressione Ctrl+C para encerrar\n")
    print("-"*60 + "\n")
    
    # Iniciar o servidor
    uvicorn.run(app, host="127.0.0.1", port=8000)