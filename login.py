from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from supabase import create_client
import os

# Configuração do Supabase
supabase_url = 'https://gccxbkoejigwkqwyvcav.supabase.co'
supabase_key = os.getenv(
    'SUPABASE_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjY3hia29lamlnd2txd3l2Y2F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM2OTg5OTYsImV4cCI6MjA0OTI3NDk5Nn0.ADRY3SLagP-NjhAAvRRP8A4Ogvo7AbWvcW-J5gAbyr4'
)
supabase = create_client(supabase_url, supabase_key)

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        empresa = request.form.get('empresa').strip()
        usuario = request.form.get('usuario').strip()
        senha = request.form.get('senha').strip()

        try:
            # Verifica se a empresa existe
            empresa_data = supabase.table('empresa').select('id').eq('nome_empresa', empresa).single().execute()
            if not empresa_data.data:
                flash('Empresa não encontrada.', 'danger')
                return redirect(url_for('login.login'))

            id_empresa = empresa_data.data['id']

            # Verifica se o usuário e a senha são válidos
            usuario_data = supabase.table('usuarios').select('id, nome_usuario').eq('nome_usuario', usuario).eq(
                'senha', senha).eq('id_empresa', id_empresa).single().execute()
            if not usuario_data.data:
                flash('Usuário ou senha inválidos.', 'danger')
                return redirect(url_for('login.login'))

            # Armazena os dados do usuário na sessão
            session['user_id'] = usuario_data.data['id']
            session['user_name'] = usuario_data.data['nome_usuario']
            session['empresa_id'] = id_empresa

            # Login bem-sucedido, redireciona para a página da agenda
            return redirect(url_for('agenda_bp.renderizar_agenda'))  # Corrigido para usar o blueprint correto

        except Exception as e:
            flash(f'Erro ao realizar login: {str(e)}', 'danger')
            return redirect(url_for('login.login'))

    return render_template('login.html')

# Adicione uma rota de logout
@login_bp.route('/logout')
def logout():
    session.clear()  # Limpa os dados da sessão
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('login.login'))
