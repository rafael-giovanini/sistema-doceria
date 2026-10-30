from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Ingrediente(Base):
    __tablename__ = "ingredientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    custo_total = Column(Float, nullable=False)
    quantidade_embalagem = Column(Float, nullable=False)
    unidade = Column(String, nullable=False)
    estoque_atual = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Receita(Base):
    __tablename__ = "receitas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    rendimento = Column(Integer, nullable=False)
    margem_lucro = Column(Float, default=0.4)
    custo_total = Column(Float, default=0)
    preco_venda = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    itens = relationship("ItemReceita", back_populates="receita", cascade="all, delete-orphan")


class ItemReceita(Base):
    __tablename__ = "itens_receita"
    id = Column(Integer, primary_key=True, index=True)
    receita_id = Column(Integer, ForeignKey("receitas.id"))
    ingrediente_id = Column(Integer, ForeignKey("ingredientes.id"))
    quantidade_usada = Column(Float, nullable=False)
    receita = relationship("Receita", back_populates="itens")


class Venda(Base):
    __tablename__ = "vendas"
    id = Column(Integer, primary_key=True, index=True)
    produto_nome = Column(String, nullable=False)
    quantidade = Column(Integer, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)
    custo_total = Column(Float, nullable=False)
    lucro = Column(Float, nullable=False)
    data = Column(DateTime(timezone=True), server_default=func.now())
