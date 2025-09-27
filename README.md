# 🤟 Conecta Libras

> Tradutor inteligente que converte a escrita natural de pessoas surdas para português padrão e gera áudio, facilitando a comunicação inclusiva.

## ✨ Funcionalidades

- 📝 **Tradução Inteligente**: Converte escrita natural para português formal
- 🔊 **Geração de Áudio**: Transforma texto traduzido em áudio
- 🤖 **IA Contextual**: Interpretação inteligente do contexto
- 📱 **Interface Responsiva**: Design acessível para todos os dispositivos
- 🎯 **Demonstração Visual**: Exemplo prático de funcionamento

## 🚀 Como Funciona

### Exemplo de Tradução:
```
INPUT:  "EU IR LOJA COMPRAR ROUPA"
OUTPUT: "Eu vou à loja comprar roupa"
ÁUDIO:  🔊 Reprodução do texto traduzido
```

## 🛠️ Tecnologias

- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Tailwind CSS
- **Animações**: CSS Animations
- **Design**: Glassmorphism, Gradients

## 📦 Estrutura do Projeto

```
conecta-libras/
├── index.html/          # Página principal
├── src/
│   ├── styles/
│   │   └── banner.css      # Estilos do banner
│   └── components/         # Componentes futuros
├── package.json            # Configurações do projeto
└── README.md              # Esta documentação
```

## 🔧 Como Executar

### Opção 1: Visualização Simples
1. Clone o repositório:
```bash
git clone https://github.com/wrezende2/conecta-libras.git
cd conecta-libras
```

2. Abra o arquivo `index.html` no navegador

### Opção 2: Servidor Local
1. Instale as dependências:
```bash
npm install
```

2. Execute o servidor de desenvolvimento:
```bash
npm run dev
```

3. Acesse: `http://localhost:3000`

## 🌐 Deploy

### GitHub Pages
1. Configure o repositório no GitHub
2. Execute:
```bash
npm run deploy
```
3. Acesse: `https://wrezende2.github.io/conecta-libras`

## 🎨 Características Visuais

- **Gradiente Azul**: Representa tecnologia e comunicação
- **Animações Suaves**: UX fluida e envolvente
- **Demonstração Prática**: Mostra o funcionamento real
- **Design Inclusivo**: Acessível para pessoas com deficiência

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📋 Roadmap

- [x] Banner principal com demonstração
- [x] Design responsivo
- [ ] Implementação do tradutor funcional
- [ ] Integração com API de IA
- [ ] Sistema de geração de áudio
- [ ] Histórico de traduções
- [ ] Modo offline
- [ ] PWA (Progressive Web App)

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

- **GitHub**: [@wrezende2](https://github.com/wrezende2)
- **Email**: hello@wssstudioart.com

---

<div align="center">
  <p>Feito com para facilitar a comunicação inclusiva</p>
</div>

## Banners e Actions

- Como gerar localmente:

```powershell
pip install -r tools/banner/requirements.txt
powershell -ExecutionPolicy Bypass -File tools/banner/run_exports.ps1
```

- GitHub Actions (Build Social Banners):
  - Dispara a cada push em `tools/banner/**` ou `assets/logo/**`, ou manual via Actions > Run workflow
  - Faz o build dos kits Claro e Escuro e publica como Artifacts (ZIPs)

- GitHub Actions (Release Banners):
  - Disparo manual (workflow_dispatch)
  - Gera os kits e publica um Release anexando os ZIPs
  - Arquivo: `.github/workflows/release-banners.yml`

- Dicas:
  - Para verticais (Stories/TikTok), pode usar `--text-shift -0.08` no gerador
  - Para EXIF nos JPGs: `--exif-artist`, `--exif-copyright`, `--exif-description`
