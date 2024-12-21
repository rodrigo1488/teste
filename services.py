from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash
from supabase import create_client
import os

# Configuração do Supabase
supabase_url = 'https://gccxbkoejigwkqwyvcav.supabase.co'
supabase_key = os.getenv(
    'SUPABASE_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjY3hia29lamlnd2txd3l2Y2F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM2OTg5OTYsImV4cCI6MjA0OTI3NDk5Nn0.ADRY3SLagP-NjhAAvRRP8A4Ogvo7AbWvcW-J5gAbyr4'
)
supabase = create_client(supabase_url, supabase_key)

app = Flask(__name__)
services_bp = Blueprint('services', __name__)

# Função de verificação de login
def verificar_login():
    if 'user_id' not in session or 'empresa_id' not in session:
        flash('Você precisa estar logado para acessar essa página.', 'danger')
        return redirect(url_for('login.login'))  # Redireciona para a página de login
    return None

# Página de serviços com funcionalidade de pesquisa
@services_bp.route('/servicos', methods=['GET', 'POST'])
def index():
    # Verifica se o usuário está logado
    if verificar_login():
        return verificar_login()

    search_query = request.form.get('search_query') if request.method == 'POST' else None
    services = get_services(search_query)
    return render_template('servicos.html', services=services)

# Função para buscar serviços
def get_services(search_query=None):
    try:
        empresa_id = session['empresa_id']  # Pega a empresa logada da sessão
        if search_query:
            response = (supabase.table('servicos')
                        .select('*')
                        .eq('id_empresa', empresa_id)
                        .ilike('nome_servico', f'%{search_query}%')
                        .execute())
        else:
            response = (supabase.table('servicos')
                        .select('*')
                        .eq('id_empresa', empresa_id)
                        .execute())
        return response.data if response.data else []
    except Exception as e:
        print(f"Erro ao buscar serviços: {e}")
        return []

# Função para adicionar um novo serviço
@services_bp.route('/add_service', methods=['POST'])
def add_service():
    # Verifica se o usuário está logado
    if verificar_login():
        return verificar_login()

    try:
        nome_servico = request.form['nome_servico']
        preco = float(request.form['preco'])
        tempo = int(request.form['tempo'])

        # Adiciona o id_empresa associado à sessão
        supabase.table('servicos').insert([{
            'nome_servico': nome_servico,
            'preco': preco,
            'tempo': tempo,
            'id_empresa': session['empresa_id']  # Associa o serviço à empresa logada
        }]).execute()
    except Exception as e:
        print(f"Erro ao adicionar serviço: {e}")
        flash('Erro ao adicionar serviço. Tente novamente.', 'danger')
    return redirect(url_for('services.index'))

# Função para excluir um serviço
@services_bp.route('/excluir_servico/<int:service_id>', methods=['GET'])
def excluir_servico(service_id):
    # Verifica se o usuário está logado
    if verificar_login():
        return verificar_login()

    try:
        # Exclui apenas se o serviço pertence à empresa logada
        supabase.table('servicos').delete().eq('id', service_id).eq('id_empresa', session['empresa_id']).execute()
    except Exception as e:
        print(f"Erro ao excluir serviço: {e}")
        flash('Erro ao excluir serviço. Tente novamente.', 'danger')
    return redirect(url_for('services.index'))

# Registra o blueprint no app principal
app.register_blueprint(services_bp)

if __name__ == '__main__':
    app.secret_key = 'sua_chave_secreta'  # Necessário para usar sessões e flash messages
    app.run(debug=True)
