import os
import sys
import django

# Configurar Django
# O caminho para o projeto Django precisa ser ajustado para o ambiente do contêiner/sandbox
# Supondo que o script seja executado da raiz do repositório.
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
try:
    django.setup()
except ImportError as e:
    print(f"Error setting up Django: {e}")
    print("Please ensure the DJANGO_SETTINGS_MODULE is correct and the project path is in sys.path.")
    sys.exit(1)


from apps.empresa.models import EmpresaNaoClassificada

def create_test_data():
    """Cria dados de teste para o ambiente de desenvolvimento."""

    # Limpar dados existentes
    EmpresaNaoClassificada.objects.all().delete()

    # Criar empresas não classificadas de teste
    empresas_teste = [
        {
            'cnpj': '11.111.111/0001-11',
            'nome_fantasia': 'Empresa Teste 1',
            'razao_social': 'Empresa Teste 1 Ltda',
            'logradouro': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'uf': 'SP'
        },
        {
            'cnpj': '22.222.222/0001-22',
            'nome_fantasia': 'Empresa Teste 2',
            'razao_social': 'Empresa Teste 2 Ltda',
            'logradouro': 'Av. Teste, 456',
            'cidade': 'Rio de Janeiro',
            'uf': 'RJ'
        },
        {
            'cnpj': '33.333.333/0001-33',
            'nome_fantasia': 'Empresa Teste 3',
            'razao_social': 'Empresa Teste 3 Ltda',
            'logradouro': 'Praça Teste, 789',
            'cidade': 'Belo Horizonte',
            'uf': 'MG'
        }
    ]

    for empresa_data in empresas_teste:
        EmpresaNaoClassificada.objects.create(**empresa_data)

    print(f"Criadas {len(empresas_teste)} empresas de teste")

if __name__ == '__main__':
    create_test_data()