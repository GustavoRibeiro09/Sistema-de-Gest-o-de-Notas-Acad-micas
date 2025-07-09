import psycopg2
from psycopg2 import sql


def criar_banco_dados():
    """
    Cria o banco de dados e as tabelas necessárias para o sistema de notas.
    """
    # Parâmetros de conexão
    params = {
        'dbname': 'postgres',  # Banco padrão para conexão inicial
        'user': 'postgres',
        'password': 'JulietaeLana1',
        'host': 'localhost',
        'port': '5432'
    }

    conn = None
    try:
        # Conectar ao banco de dados padrão
        print("Conectando ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cursor = conn.cursor()

        # Verificar se o banco de dados já existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'sistema_notas'")
        banco_existe = cursor.fetchone()

        # Criar o banco de dados se não existir
        if not banco_existe:
            print("Criando banco de dados 'sistema_notas'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier('sistema_notas')))
        else:
            print("Banco de dados 'sistema_notas' já existe.")

        # Fechar conexão com o banco padrão
        cursor.close()
        conn.close()

        # Conectar ao banco de dados sistema_notas
        params['dbname'] = 'sistema_notas'
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        cursor = conn.cursor()

        # Criar tabela de alunos
        print("Criando tabela de alunos...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL
            )
        """)

        # Criar tabela de notas
        print("Criando tabela de notas...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notas (
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER REFERENCES alunos(id) ON DELETE CASCADE,
                semestre INTEGER NOT NULL,
                portugues NUMERIC(4,2),
                matematica NUMERIC(4,2),
                ciencias NUMERIC(4,2),
                historia NUMERIC(4,2),
                geografia NUMERIC(4,2),
                educacao_fisica NUMERIC(4,2),
                arte NUMERIC(4,2),
                media NUMERIC(4,2),
                aprovado BOOLEAN,
                UNIQUE(aluno_id, semestre)
            )
        """)

        print("Estrutura do banco de dados criada com sucesso!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Erro: {error}")
    finally:
        if conn is not None:
            conn.close()
            print("Conexão com o banco de dados fechada.")


if __name__ == "__main__":
    criar_banco_dados()
