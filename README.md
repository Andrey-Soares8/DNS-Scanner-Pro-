# DNS Scanner Pro 🔍

Um scanner de subdomínios com interface gráfica desenvolvido em Python usando Tkinter.

## Características ✨

- Interface gráfica moderna e intuitiva
- Suporte a múltiplas threads para scans rápidos
- Barra de progresso em tempo real
- Sistema de retry para maior confiabilidade
- Exportação de resultados
- Log detalhado de operações
- Configurações personalizáveis

## Requisitos 📋

- Python 3.8 ou superior
- Bibliotecas listadas em `requirements.txt`

## Instalação 🚀

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/dns-scanner-pro.git
cd dns-scanner-pro
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como Usar 💡

1. Execute o programa:
```bash
python dnsbrute.py
```

2. Na interface:
   - Digite o domínio alvo (ex: exemplo.com)
   - Selecione uma wordlist (arquivo .txt com subdomínios)
   - Clique em "Iniciar Scan"

3. Resultados:
   - Os subdomínios encontrados serão exibidos em tempo real
   - Use o menu "Arquivo > Exportar Resultados" para salvar

## Configurações ⚙️

- **Threads máximas**: Número de verificações simultâneas (padrão: 10)
- **Timeout**: Tempo limite para cada tentativa (padrão: 3s)
- **Retry**: Número de tentativas por subdomínio (padrão: 2)

## Logs 📝

O programa mantém um arquivo de log (`dns_scanner.log`) com informações detalhadas sobre as operações realizadas.

## Contribuindo 🤝

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## Licença 📄

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. 