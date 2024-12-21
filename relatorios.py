from flask import Blueprint, render_template, request, jsonify
from datetime import datetime, timedelta
from supabase import create_client
import os

# Configuração do Supabase
supabase_url = 'https://gccxbkoejigwkqwyvcav.supabase.co'
supabase_key = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjY3hia29lamlnd2txd3l2Y2F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM2OTg5OTYsImV4cCI6MjA0OTI3NDk5Nn0.ADRY3SLagP-NjhAAvRRP8A4Ogvo7AbWvcW-J5gAbyr4')
supabase = create_client(supabase_url, supabase_key)

# Definição do Blueprint
relatorios_bp = Blueprint('relatorios', __name__)

def calcular_intervalo(periodo):
    hoje = datetime.today()
    if periodo == 'dia':
        inicio = hoje.replace(hour=0, minute=0, second=0, microsecond=0)
        fim = hoje
    elif periodo == 'semana':
        inicio = hoje - timedelta(days=hoje.weekday())
        fim = hoje
    elif periodo == 'mes':
        inicio = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim = hoje
    else:
        raise ValueError("Período inválido")
    return inicio, fim

@relatorios_bp.route('/api/financeiro')
def financeiro():
    periodo = request.args.get('periodo', 'dia')
    try:
        response = supabase.rpc('financeiro_total', {'periodo': periodo}).execute()
        if response.error:
            raise Exception(response.error.message)
        return jsonify({"total_financeiro": response.data})
    except Exception as e:
        print(f"Erro no endpoint financeiro: {e}")
        return jsonify({"error": str(e)}), 500



@relatorios_bp.route('/api/atendimentos')
def atendimentos():
    periodo = request.args.get('periodo', 'dia')
    try:
        response = supabase.rpc('atendimentos_por_usuario', {'periodo': periodo}).execute()
        if response.error:
            raise Exception(response.error.message)
        return jsonify(response.data)
    except Exception as e:
        print(f"Erro no endpoint atendimentos: {e}")
        return jsonify({"error": str(e)}), 500

@relatorios_bp.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')

# FRONTEND (relatorios.html)

# HTML e JavaScript usando bibliotecas como Chart.js serão criados para:
# - Exibir gráficos de receita total
# - Exibir atendimentos por usuário
# - Adicionar filtros dinâmicos de período
