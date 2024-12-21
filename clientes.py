from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from supabase import create_client
import os

# Configuração do Supabase
supabase_url = 'https://gccxbkoejigwkqwyvcav.supabase.co'
supabase_key = os.getenv(
    'SUPABASE_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjY3hia29lamlnd2txd3l2Y2F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM2OTg5OTYsImV4cCI6MjA0OTI3NDk5Nn0.ADRY3SLagP-NjhAAvRRP8A4Ogvo7AbWvcW-J5gAbyr4'
)
supabase = create_client(supabase_url, supabase_key)

# Define o Blueprint para as rotas de clientes
clientes_bp = Blueprint('clientes_bp', __name__)

# Função de Verificação de Login
def verificar_login():
    if 'user_id' not in session or 'empresa_id' not in session:
        return redirect(url_for('login.login'))  # Redireciona para o login se não estiver autenticado
    return None

# Rota para listar todos os clientes
@clientes_bp.route('/clientes')
def clientes():
    # Verifica se o usuário está logado
    redirecionar = verificar_login()
    if redirecionar:
        return redirecionar

    query = request.args.get('query', '')  # Obtém o termo de pesquisa da URL
    error = request.args.get('error', '')  # Obtém mensagem de erro, se existir
    
    try:
        # Filtra os clientes pela empresa associada na sessão
        if query:
            response = (supabase.table('clientes')
                        .select('*')
                        .eq('id_empresa', session['empresa_id'])
                        .ilike('nome_cliente', f'%{query}%')
                        .execute())
        else:
            response = (supabase.table('clientes')
                        .select('*')
                        .eq('id_empresa', session['empresa_id'])
                        .execute())

        clientes = response.data if response.data else []
        return render_template('clientes.html', clientes=clientes, query=query, error=error)
    except Exception as e:
        print(f"Erro ao listar clientes: {e}")
        return render_template('clientes.html', clientes=[], query=query, error="Erro ao listar clientes.")

# Rota para cadastrar um novo cliente
@clientes_bp.route('/add_cliente', methods=['POST'])
def cadastrar_cliente():
    # Verifica se o usuário está logado
    redirecionar = verificar_login()
    if redirecionar:
        return redirecionar

    nome_cliente = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']

    try:
        # Insere o cliente com o id_empresa da sessão
        supabase.table('clientes').insert([{
            'nome_cliente': nome_cliente,
            'telefone': telefone,
            'email': email,
            'id_empresa': session['empresa_id']
        }]).execute()

        return redirect(url_for('clientes_bp.clientes'))
    except Exception as e:
        print(f"Erro ao cadastrar cliente: {e}")
        return redirect(url_for('clientes_bp.clientes', error="Erro ao cadastrar cliente."))

# Rota para editar cliente
@clientes_bp.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    # Verifica se o usuário está logado
    redirecionar = verificar_login()
    if redirecionar:
        return redirecionar

    if request.method == 'GET':
        try:
            # Busca o cliente pelo ID e filtra pela empresa
            response = (supabase.table('clientes')
                        .select('*')
                        .eq('id', id)
                        .eq('id_empresa', session['empresa_id'])
                        .execute())
            cliente = response.data[0] if response.data else None

            if not cliente:
                return redirect(url_for('clientes_bp.clientes', error="Cliente não encontrado."))

            return render_template('editar_cliente.html', cliente=cliente)
        except Exception as e:
            print(f"Erro ao buscar cliente: {e}")
            return redirect(url_for('clientes_bp.clientes', error="Erro ao buscar cliente."))

    if request.method == 'POST':
        nome_cliente = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']

        try:
            # Atualiza o cliente apenas se pertence à empresa
            supabase.table('clientes').update({
                'nome_cliente': nome_cliente,
                'telefone': telefone,
                'email': email
            }).eq('id', id).eq('id_empresa', session['empresa_id']).execute()

            return redirect(url_for('clientes_bp.clientes'))
        except Exception as e:
            print(f"Erro ao editar cliente: {e}")
            return redirect(url_for('clientes_bp.clientes', error="Erro ao editar cliente."))

# Rota para excluir cliente
@clientes_bp.route('/excluir_cliente/<int:id>', methods=['GET'])
def excluir_cliente(id):
    # Verifica se o usuário está logado
    redirecionar = verificar_login()
    if redirecionar:
        return redirecionar

    try:
        # Remove o cliente apenas se pertence à empresa
        supabase.table('clientes').delete().eq('id', id).eq('id_empresa', session['empresa_id']).execute()

        return redirect(url_for('clientes_bp.clientes'))
    except Exception as e:
        print(f"Erro ao excluir cliente: {e}")
        return redirect(url_for('clientes_bp.clientes', error="Erro ao excluir cliente."))
