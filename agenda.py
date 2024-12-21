from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
from supabase import create_client
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuração do Supabase
supabase_url = 'https://gccxbkoejigwkqwyvcav.supabase.co'
supabase_key = os.getenv(
    'SUPABASE_KEY',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdjY3hia29lamlnd2txd3l2Y2F2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM2OTg5OTYsImV4cCI6MjA0OTI3NDk5Nn0.ADRY3SLagP-NjhAAvRRP8A4Ogvo7AbWvcW-J5gAbyr4'
)
supabase = create_client(supabase_url, supabase_key)

# Criação do Blueprint
agenda_bp = Blueprint('agenda_bp', __name__)

# Validação de Login
def verificar_login():
    if 'user_id' not in session or 'empresa_id' not in session:
        return redirect(url_for('login.login'))  # Redireciona para a página de login se não estiver autenticado
    return None

# Função para obter o ID da empresa da sessão
def obter_id_empresa():
    return session.get('empresa_id')

# Função para enviar e-mails
def enviar_email(destinatario, assunto, mensagem, email_remetente, senha_remetente):
    try:
        servidor_smtp = 'smtp.gmail.com'
        porta_smtp = 587

        msg = MIMEMultipart()
        msg['From'] = email_remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.attach(MIMEText(mensagem, 'plain'))

        servidor = smtplib.SMTP(servidor_smtp, porta_smtp)
        servidor.starttls()
        servidor.login(email_remetente, senha_remetente)
        servidor.sendmail(email_remetente, destinatario, msg.as_string())
        servidor.quit()

        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

# Função para realizar o agendamento
@agenda_bp.route('/api/agendar', methods=['POST'])
def agendar():
    if verificar_login():
        return verificar_login()

    dados = request.get_json()
    empresa_id = obter_id_empresa()

    if not empresa_id:
        return redirect(url_for('login.login'))

    # Inserindo no banco de dados
    response = supabase.table("agenda").insert({
        "cliente_id": dados["cliente_id"],
        "usuario_id": dados["usuario_id"],
        "servico_id": dados["servico_id"],
        "data": dados["data"],
        "horario": dados["horario"],
        "id_empresa": empresa_id  # Associa o agendamento à empresa logada
    }).execute()

    if response.data:
        empresa = supabase.table('empresa').select("email, senha_app").eq('id', empresa_id).execute().data[0]
        cliente = supabase.table("clientes").select("email, nome_cliente").eq("id", dados["cliente_id"]).execute().data[0]
        usuario = supabase.table("usuarios").select("email, nome_usuario").eq("id", dados["usuario_id"]).execute().data[0]
        servico = supabase.table("servicos").select("nome_servico").eq("id", dados["servico_id"]).execute().data[0]

        nome_servico = servico["nome_servico"]
        assunto_cliente = f"Confirmação de Agendamento - {cliente['nome_cliente']}"
        mensagem_cliente = f"""
        Olá {cliente['nome_cliente']},

        Seu agendamento foi confirmado! Aqui estão os detalhes:

        - **Serviço: {nome_servico}
        - **Data: {dados['data']}
        - **Horário: {dados['horario']}
        - **Profissional Responsável**: {usuario['nome_usuario']}

        Em caso de dúvidas ou alterações no agendamento, entre em contato conosco.

        Atenciosamente,
        Equipe de Agendamento.
        """

        assunto_usuario = f"Novo Agendamento - {usuario['nome_usuario']}"
        mensagem_usuario = f"""
        Olá {usuario['nome_usuario']},

        Você recebeu um novo agendamento! Confira os detalhes abaixo:

        - **Serviço**: {nome_servico}
        - **Data**: {dados['data']}
        - **Horário**: {dados['horario']}
        - **Cliente**: {cliente['nome_cliente']}

        Lembre-se de verificar sua agenda regularmente para acompanhar todos os compromissos.

        Atenciosamente,
        Equipe de Agendamento.
        """
        enviar_email(cliente['email'], assunto_cliente, mensagem_cliente, empresa['email'], empresa['senha_app'])
        enviar_email(usuario['email'], assunto_usuario, mensagem_usuario, empresa['email'], empresa['senha_app'])

        return jsonify({"message": "Agendamento realizado com sucesso e e-mails enviados!"}), 201
    else:
        return jsonify({"error": "Erro ao criar agendamento"}), 400

# Rota para retornar JSON com agendamentos
@agenda_bp.route('/agenda/data', methods=['GET'])
def listar_agendamentos():
    if verificar_login():
        return verificar_login()

    empresa_id = obter_id_empresa()

    if not empresa_id:
        return redirect(url_for('login.login'))

    response = supabase.table("agenda").select(
        "id, data, horario, cliente_id, servico_id, clientes!agendamentos_cliente_id_fkey(nome_cliente), servicos!agendamentos_servico_id_fkey(nome_servico)"
    ).eq("id_empresa", empresa_id).execute()

    agendamentos = [
        {
            "id": item["id"],
            "data": item["data"],
            "horario": item["horario"],
            "cliente_nome": item["clientes"]["nome_cliente"],
            "servico_nome": item["servicos"]["nome_servico"]
        }
        for item in response.data
    ]
    return jsonify(agendamentos), 200

# Rota para retornar os clientes
@agenda_bp.route('/api/clientes', methods=['GET'])
def listar_clientes():
    if verificar_login():
        return verificar_login()

    empresa_id = obter_id_empresa()

    response = supabase.table("clientes").select("id, nome_cliente").eq("id_empresa", empresa_id).execute()
    return jsonify(response.data), 200

# Rota para retornar os profissionais (usuários)
@agenda_bp.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    if verificar_login():
        return verificar_login()

    empresa_id = obter_id_empresa()

    response = supabase.table("usuarios").select("id, nome_usuario").eq("id_empresa", empresa_id).execute()
    return jsonify(response.data), 200

# Rota para retornar os serviços
@agenda_bp.route('/api/servicos', methods=['GET'])
def listar_servicos():
    if verificar_login():
        return verificar_login()

    empresa_id = obter_id_empresa()

    response = supabase.table("servicos").select("id, nome_servico").eq("id_empresa", empresa_id).execute()
    return jsonify(response.data), 200

# Rota para checar a disponibilidade de horário
@agenda_bp.route('/api/checagem-horario/<int:usuario_id>/<string:data>/<string:horario>', methods=['GET'])
def checar_horario(usuario_id, data, horario):
    if verificar_login():
        return verificar_login()

    empresa_id = obter_id_empresa()

    response = supabase.table("agenda").select("*").eq("usuario_id", usuario_id).eq("data", data).eq("horario", horario).eq("id_empresa", empresa_id).execute()
    
    if response.data:
        return jsonify({"exists": True}), 200
    else:
        return jsonify({"exists": False}), 200

# Rota para renderizar a página HTML
@agenda_bp.route('/agenda', methods=['GET'])
def renderizar_agenda():
    if verificar_login():
        return verificar_login()

    return render_template('agenda.html')

@agenda_bp.route('/api/agendamento/<int:id>', methods=['DELETE'])
def cancelar_agendamento(id):
    if verificar_login():
        return verificar_login()

    empresa_id = session.get('empresa_id')  # Obter empresa logada

    if not empresa_id:
        return jsonify({"error": "Empresa não encontrada na sessão."}), 401

    try:
        # Buscar informações do agendamento antes de removê-lo
        agendamento = supabase.table("agenda").select(
            "cliente_id, usuario_id, servico_id, data, horario"
        ).eq("id", id).eq("id_empresa", empresa_id).execute()

        if not agendamento.data:
            return jsonify({"error": "Agendamento não encontrado."}), 404

        agendamento = agendamento.data[0]

        # Buscar informações adicionais
        cliente = supabase.table("clientes").select("email, nome_cliente").eq("id", agendamento["cliente_id"]).execute().data[0]
        usuario = supabase.table("usuarios").select("email, nome_usuario").eq("id", agendamento["usuario_id"]).execute().data[0]
        servico = supabase.table("servicos").select("nome_servico").eq("id", agendamento["servico_id"]).execute().data[0]
        empresa = supabase.table("empresa").select("email, senha_app").eq("id", empresa_id).execute().data[0]

        # Remover o agendamento no banco
        supabase.table("agenda").delete().match({"id": id, "id_empresa": empresa_id}).execute()

        # Preparar e-mails
        assunto_cliente = "Cancelamento de Agendamento"
        mensagem_cliente = f"""
        Olá {cliente['nome_cliente']},
        Seu agendamento foi cancelado.
        - Serviço: {servico['nome_servico']}
        - Data: {agendamento['data']}
        - Horário: {agendamento['horario']}
        """

        assunto_usuario = "Cancelamento de Agendamento"
        mensagem_usuario = f"""
        Olá {usuario['nome_usuario']},
        O seguinte agendamento foi cancelado:
        - Cliente: {cliente['nome_cliente']}
        - Serviço: {servico['nome_servico']}
        - Data: {agendamento['data']}
        - Horário: {agendamento['horario']}
        """

        # Enviar e-mails
        enviar_email(cliente['email'], assunto_cliente, mensagem_cliente, empresa['email'], empresa['senha_app'])
        enviar_email(usuario['email'], assunto_usuario, mensagem_usuario, empresa['email'], empresa['senha_app'])

        return jsonify({"message": "Agendamento cancelado com sucesso e e-mails enviados!"}), 200
    except Exception as e:
        print(f"Erro ao cancelar agendamento: {e}")
        return jsonify({"error": "Erro ao cancelar agendamento."}), 500


@agenda_bp.route('/api/agendamento/finalizar/<int:id>', methods=['POST'])
def finalizar_agendamento(id):
    if verificar_login():
        return verificar_login()

    dados = request.get_json()
    valor = dados.get("valor")
    meio_pagamento = dados.get("meio_pagamento")
    empresa_id = obter_id_empresa()

    if not empresa_id:
        return jsonify({"error": "Empresa não encontrada na sessão."}), 401

    try:
        # Insere os dados na tabela "finalizados"
        supabase.table("finalizados").insert({
            "id_agenda": id,
            "meio_pagamento": meio_pagamento,
            "valor": valor,
            "id_empresa": empresa_id
        }).execute()

        return jsonify({"message": "Agendamento finalizado com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao finalizar agendamento: {e}")
        return jsonify({"error": "Erro ao finalizar agendamento."}), 500