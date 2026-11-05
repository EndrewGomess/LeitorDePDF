# Leitor de livros de D&D em PDF

Leitor e sistema de perguntas e respostas para livros de **Dungeons & Dragons 5e (2014) e da revisão de 2024**, executado em um notebook do Google Colab. A ideia é permitir consultar um ou mais livros em linguagem natural, localizar as regras nas páginas originais e apresentar respostas com referências verificáveis.

## Como funciona

O notebook procura recursivamente os PDFs da pasta de livros no Google Drive. Para cada livro, extrai o texto por página e cria um índice de busca persistente. Marcadores e entradas do sumário ajudam a localizar seções relevantes. Quando a numeração impressa pode ser identificada, as referências incluem a página do livro e a posição física correspondente no PDF.

A pesquisa combina correspondências de texto com similaridade semântica multilíngue. Ela prioriza as seções mais prováveis e amplia a busca quando precisa de mais evidências. Em perguntas sobre listas, pode incluir páginas vizinhas da mesma seção, inclusive quando a lista continua em outra página. O Gemini recebe apenas as páginas selecionadas para cada pergunta. As fontes da resposta são conferidas contra o texto enviado ao modelo.

Os índices ficam no Google Drive, separados por livro. O notebook reutiliza os índices quando o arquivo e a configuração não mudaram, processa arquivos novos ou atualizados e permite reconstruir um único livro. A lógica de leitura, indexação, busca e resposta fica no próprio notebook para facilitar o uso no Colab e permitir uma interface futura.

## Começar no Google Colab

1. Abra [\`leitor_pdf_rpg.ipynb\`](leitor_pdf_rpg.ipynb) no Colab.
2. Coloque os PDFs de D&D 5e na pasta desejada do Google Drive.
3. Na seção de configuração do notebook, ajuste \`PASTA_LIVROS\` para essa pasta.
4. Para gerar respostas, crie o segredo \`GOOGLE_API_KEY\` em **Secrets** no Colab e permita o acesso do notebook. A pesquisa direta por páginas funciona sem essa chave.
5. Execute as células em ordem. Depois de configurar o acervo pela primeira vez, sincronize e consulte os livros.

## Configuração dos livros

\`PASTA_LIVROS\` é o caminho da coleção de PDFs. \`PASTA_INDICES\` aponta para a pasta de índices no Drive. Os PDFs podem ficar em subpastas. O identificador de cada livro é seu caminho relativo à coleção, com barras \`/\`.

Se \`2014\` ou \`2024\` estiver no nome do arquivo ou na pasta, o notebook pode identificar a edição automaticamente. Para especificar a edição ou corrigir a numeração de um livro, use \`AJUSTES\`:

\`\`\`python
AJUSTES = {
    "2024/Livro do Jogador.pdf": {
        "edicao": "2024",
        "deslocamento": 2,
    },
}
\`\`\`

O deslocamento é a posição física da página no PDF menos seu número impresso. Quando o notebook não consegue confirmar a correspondência, ele cita a posição física no PDF.

## Pesquisar e perguntar

Preencha \`CONSULTA\` para encontrar e inspecionar páginas. Preencha \`PERGUNTA\` para gerar uma resposta com fontes. \`LIVROS\` restringe a seleção por identificador e \`EDICAO\` pode ser \`"2014"\` ou \`"2024"\`. Para comparar as duas edições, deixe \`EDICAO = None\` e mencione os anos na pergunta.

O objeto \`chat\` permite fazer perguntas de seguimento. Use \`chat.perguntar("...")\` para continuar e \`chat.limpar()\` para apagar o histórico curto da conversa. Para reconstruir o índice de um livro específico, execute \`acervo.reindexar("2024/Livro do Jogador.pdf")\`. Consulte \`acervo.secoes(id_livro)\` para ver as seções mapeadas e \`acervo.sumario(id_livro)\` para inspecionar as entradas detectadas.

## Busca semântica e OCR

A configuração padrão usa o modelo multilíngue \`intfloat/multilingual-e5-small\`. Seus pesos são baixados no primeiro uso em cada ambiente Colab. Defina \`BUSCA_SEMANTICA = False\` para usar somente busca textual.

PDFs digitalizados podem precisar de OCR. O notebook inclui a instalação opcional do Tesseract na primeira célula. Depois de habilitá-la, configure \`OCR = "por+eng"\` para páginas em português e inglês. O OCR só é executado nas páginas com pouco texto extraível.

## Escopo e limites

- O acervo e as respostas são destinados exclusivamente a D&D 5e e à revisão de 2024.
- A qualidade da leitura depende do PDF. OCR, tabelas complexas, colunas e páginas com numeração fora do padrão podem exigir revisão do usuário.
- Se os livros não oferecerem evidências suficientes, o sistema informa isso em vez de tratar uma resposta incerta como regra confirmada.
- Os PDFs ficam na pasta do usuário no Drive. Este repositório contém o notebook e não inclui livros.

## Arquivo principal

- [\`leitor_pdf_rpg.ipynb\`](leitor_pdf_rpg.ipynb) — notebook executável no Google Colab.
