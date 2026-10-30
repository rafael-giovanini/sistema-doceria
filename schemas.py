from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class IngredienteBase(BaseModel):
    nome: str
    custo_total: float
    quantidade_embalagem: float
    unidade: str
    estoque_atual: float = 0


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteResponse(IngredienteBase):
    id: int
    custo_unitario: float

    class Config:
        from_attributes = True


class ItemReceitaBase(BaseModel):
    ingrediente_id: int
    quantidade_usada: float


class ReceitaCreate(BaseModel):
    nome: str
    rendimento: int
    margem_lucro: float = 0.4
    itens: List[ItemReceitaBase]


class ReceitaResponse(BaseModel):
    id: int
    nome: str
    rendimento: int
    margem_lucro: float
    custo_total: float
    preco_venda: float
    created_at: datetime

    class Config:
        from_attributes = True


class VendaCreate(BaseModel):
    receita_id: int
    quantidade: int
    data: Optional[datetime] = None


class VendaResponse(BaseModel):
    id: int
    produto_nome: str
    quantidade: int
    valor_unitario: float
    valor_total: float
    custo_total: float
    lucro: float
    data: datetime

    class Config:
        from_attributes = True
