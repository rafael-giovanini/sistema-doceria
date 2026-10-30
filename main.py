from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import os

from database import engine, get_db, Base
from models import Ingrediente, Receita, ItemReceita, Venda
from schemas import (
    IngredienteCreate, IngredienteResponse,
    ReceitaCreate, ReceitaResponse,
    VendaCreate, VendaResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Doceria")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ============ INGREDIENTES ============
@app.get("/api/ingredientes", response_model=list[IngredienteResponse])
def listar_ingredientes(db: Session = Depends(get_db)):
    return [
        {**i.__dict__, "custo_unitario": i.custo_total / i.quantidade_embalagem}
        for i in db.query(Ingrediente).all()
    ]


@app.post("/api/ingredientes")
def criar_ingrediente(ing: IngredienteCreate, db: Session = Depends(get_db)):
    db_ing = Ingrediente(**ing.model_dump())
    db.add(db_ing)
    db.commit()
    db.refresh(db_ing)
    return {
        "id": db_ing.id,
        **ing.model_dump(),
        "custo_unitario": ing.custo_total / ing.quantidade_embalagem,
    }


@app.delete("/api/ingredientes/{ing_id}")
def excluir_ingrediente(ing_id: int, db: Session = Depends(get_db)):
    ing = db.query(Ingrediente).get(ing_id)
    if not ing:
        raise HTTPException(404, "Não encontrado")
    db.delete(ing)
    db.commit()
    return {"ok": True}


@app.patch("/api/ingredientes/{ing_id}/estoque")
def atualizar_estoque(ing_id: int, quantidade: float, db: Session = Depends(get_db)):
    ing = db.query(Ingrediente).get(ing_id)
    if not ing:
        raise HTTPException(404, "Não encontrado")
    ing.estoque_atual += quantidade
    db.commit()
    return {"ok": True, "estoque_atual": ing.estoque_atual}


# ============ RECEITAS ============
@app.get("/api/receitas", response_model=list[ReceitaResponse])
def listar_receitas(db: Session = Depends(get_db)):
    return db.query(Receita).order_by(Receita.created_at.desc()).all()


@app.post("/api/receitas")
def criar_receita(rec: ReceitaCreate, db: Session = Depends(get_db)):
    custo_total = 0.0
    for item in rec.itens:
        ing = db.query(Ingrediente).get(item.ingrediente_id)
        if not ing:
            raise HTTPException(404, f"Ingrediente {item.ingrediente_id} não encontrado")
        custo_total += (ing.custo_total / ing.quantidade_embalagem) * item.quantidade_usada

    preco_unitario = (custo_total / rec.rendimento) / (1 - rec.margem_lucro) if rec.rendimento > 0 else 0

    db_rec = Receita(
        nome=rec.nome,
        rendimento=rec.rendimento,
        margem_lucro=rec.margem_lucro,
        custo_total=custo_total,
        preco_venda=preco_unitario * rec.rendimento,
    )
    db.add(db_rec)
    db.flush()

    for item in rec.itens:
        db.add(ItemReceita(receita_id=db_rec.id, **item.model_dump()))

    db.commit()
    db.refresh(db_rec)
    return db_rec


@app.delete("/api/receitas/{rec_id}")
def excluir_receita(rec_id: int, db: Session = Depends(get_db)):
    rec = db.query(Receita).get(rec_id)
    if not rec:
        raise HTTPException(404, "Não encontrado")
    db.delete(rec)
    db.commit()
    return {"ok": True}


# ============ VENDAS ============
@app.post("/api/vendas")
def registrar_venda(venda: VendaCreate, db: Session = Depends(get_db)):
    rec = db.query(Receita).get(venda.receita_id)
    if not rec:
        raise HTTPException(404, "Receita não encontrada")

    valor_unit = rec.preco_venda / rec.rendimento
    valor_total = valor_unit * venda.quantidade
    custo_unit = rec.custo_total / rec.rendimento
    custo_total = custo_unit * venda.quantidade
    lucro = valor_total - custo_total

    for item in rec.itens:
        ing = db.query(Ingrediente).get(item.ingrediente_id)
        if ing:
            uso_por_unidade = item.quantidade_usada / rec.rendimento
            ing.estoque_atual -= uso_por_unidade * venda.quantidade

    db_venda = Venda(
        produto_nome=rec.nome,
        quantidade=venda.quantidade,
        valor_unitario=valor_unit,
        valor_total=valor_total,
        custo_total=custo_total,
        lucro=lucro,
        data=venda.data or datetime.now(),
    )
    db.add(db_venda)
    db.commit()
    db.refresh(db_venda)
    return db_venda


@app.get("/api/vendas", response_model=list[VendaResponse])
def listar_vendas(dias: int = 0, db: Session = Depends(get_db)):
    query = db.query(Venda)
    if dias > 0:
        data_limite = datetime.now() - timedelta(days=dias)
        query = query.filter(Venda.data >= data_limite)
    return query.order_by(Venda.data.desc()).all()


# ============ FINANCEIRO ============
@app.get("/api/resumo-financeiro")
def resumo_financeiro(db: Session = Depends(get_db)):
    vendas = db.query(Venda).all()
    total_vendas = sum(v.valor_total for v in vendas)
    total_custos = sum(v.custo_total for v in vendas)
    total_lucro = sum(v.lucro for v in vendas)
    return {
        "total_vendas": round(total_vendas, 2),
        "total_custos": round(total_custos, 2),
        "total_lucro": round(total_lucro, 2),
        "quantidade_vendas": len(vendas),
    }


# ============ GRÁFICOS ============
@app.get("/api/graficos/vendas-por-dia")
def vendas_por_dia(dias: int = 30, db: Session = Depends(get_db)):
    data_limite = datetime.now() - timedelta(days=dias)
    vendas = db.query(Venda).filter(Venda.data >= data_limite).all()
    por_dia = defaultdict(lambda: {"quantidade": 0, "valor": 0.0})
    for v in vendas:
        chave = v.data.strftime("%d/%m")
        por_dia[chave]["quantidade"] += v.quantidade
        por_dia[chave]["valor"] += v.valor_total
    return [{"dia": d, **val} for d, val in sorted(por_dia.items())]


@app.get("/api/graficos/vendas-por-produto")
def vendas_por_produto(dias: int = 30, db: Session = Depends(get_db)):
    data_limite = datetime.now() - timedelta(days=dias)
    vendas = db.query(Venda).filter(Venda.data >= data_limite).all()
    por_prod = defaultdict(lambda: {"quantidade": 0, "valor": 0.0})
    for v in vendas:
        por_prod[v.produto_nome]["quantidade"] += v.quantidade
        por_prod[v.produto_nome]["valor"] += v.valor_total
    return [
        {"produto": p, **val}
        for p, val in sorted(por_prod.items(), key=lambda x: -x[1]["valor"])
    ]


# ============ EXPORTAÇÃO EXCEL ============
@app.get("/api/exportar/vendas-excel")
def exportar_vendas_excel(db: Session = Depends(get_db)):
    vendas = db.query(Venda).order_by(Venda.data.desc()).all()
    dados = [
        {
            "Data": v.data.strftime("%d/%m/%Y %H:%M"),
            "Produto": v.produto_nome,
            "Quantidade": v.quantidade,
            "Valor Unitário": round(v.valor_unitario, 2),
            "Valor Total": round(v.valor_total, 2),
            "Custos": round(v.custo_total, 2),
            "Lucro": round(v.lucro, 2),
        }
        for v in vendas
    ]
    df = pd.DataFrame(dados)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Vendas")
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=vendas_{datetime.now().strftime('%Y%m%d')}.xlsx"
        },
    )


@app.get("/api/exportar/estoque-excel")
def exportar_estoque_excel(db: Session = Depends(get_db)):
    ing = db.query(Ingrediente).all()
    dados = [
        {
            "Nome": i.nome,
            "Custo Unitário": round(i.custo_total / i.quantidade_embalagem, 4),
            "Estoque Atual": round(i.estoque_atual, 2),
            "Unidade": i.unidade,
        }
        for i in ing
    ]
    df = pd.DataFrame(dados)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Estoque")
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=estoque_{datetime.now().strftime('%Y%m%d')}.xlsx"
        },
    )


@app.get("/api/exportar/receitas-excel")
def exportar_receitas_excel(db: Session = Depends(get_db)):
    recs = db.query(Receita).all()
    dados = [
        {
            "Produto": r.nome,
            "Rendimento": r.rendimento,
            "Margem Lucro %": round(r.margem_lucro * 100, 1),
            "Custo Total": round(r.custo_total, 2),
            "Custo por Unidade": round(r.custo_total / r.rendimento, 2),
            "Preço Venda Total": round(r.preco_venda, 2),
            "Preço por Unidade": round(r.preco_venda / r.rendimento, 2),
        }
        for r in recs
    ]
    df = pd.DataFrame(dados)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Receitas")
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=receitas_{datetime.now().strftime('%Y%m%d')}.xlsx"
        },
    )


# ============ EXPORTAÇÃO PDF ============
@app.get("/api/exportar/vendas-pdf")
def exportar_vendas_pdf(db: Session = Depends(get_db)):
    vendas = db.query(Venda).order_by(Venda.data.desc()).all()
    total_vendas = sum(v.valor_total for v in vendas)
    total_custos = sum(v.custo_total for v in vendas)
    total_lucro = sum(v.lucro for v in vendas)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatorio de Vendas - Doceria", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Data de emissao: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(95, 8, f"Total Vendas: R$ {total_vendas:.2f}", border=1)
    pdf.cell(95, 8, f"Total Custos: R$ {total_custos:.2f}", border=1, ln=True)
    pdf.cell(95, 8, f"Lucro Total: R$ {total_lucro:.2f}", border=1)
    pdf.cell(95, 8, f"Qtd. Vendas: {len(vendas)}", border=1, ln=True)
    pdf.ln(6)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(35, 7, "Data", border=1)
    pdf.cell(55, 7, "Produto", border=1)
    pdf.cell(20, 7, "Qtd", border=1)
    pdf.cell(30, 7, "Total", border=1)
    pdf.cell(30, 7, "Lucro", border=1, ln=True)

    pdf.set_font("Arial", "", 8)
    for v in vendas:
        pdf.cell(35, 6, v.data.strftime("%d/%m/%Y"), border=1)
        pdf.cell(55, 6, v.produto_nome[:25], border=1)
        pdf.cell(20, 6, str(v.quantidade), border=1)
        pdf.cell(30, 6, f"R$ {v.valor_total:.2f}", border=1)
        pdf.cell(30, 6, f"R$ {v.lucro:.2f}", border=1, ln=True)

    output = BytesIO()
    pdf.output(output)
    return Response(
        content=output.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_vendas_{datetime.now().strftime('%Y%m%d')}.pdf"
        },
    )


@app.get("/")
def root():
    return FileResponse(os.path.join(static_dir, "index.html"))
