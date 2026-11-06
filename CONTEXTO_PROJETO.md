# Contexto do projeto

## Objetivo

Criar um leitor e mecanismo de perguntas e respostas sobre livros em PDF de RPG, executado no Google Colab. O escopo é estritamente Dungeons & Dragons (D&D) 5ª edição e 5.5 (2024).

O sistema deve permitir fazer perguntas sobre um ou vários livros e responder usando o conteúdo encontrado, com referências ao livro e às páginas. Deve evitar inventar regras quando não houver evidência suficiente.

## Ambiente e uso

- A execução será feita no Google Colab.
- Os livros estarão no Google Drive do usuário. O usuário fornecerá/configurará o caminho da pasta ou dos livros no Drive.
- O programa deve processar todos os livros encontrados nesse local para formar um acervo pesquisável.
- O projeto deve permanecer simples de usar no Colab e preparado para receber uma interface de usuário posteriormente.

## Decisões sobre leitura e busca

- Usar o sumário/índice do começo de cada livro como mapa inicial de navegação.
- Para cada entrada do sumário, registrar título, página e intervalo provável até o início da seção seguinte.
- Considerar que a numeração impressa pode não corresponder à posição física no PDF; essa correspondência precisa ser tratada durante a implementação.
- Associar palavras-chave relevantes a cada seção para localizar temas mesmo quando a pergunta não repete exatamente o título.
- Ao receber uma pergunta, identificar as seções e livros mais prováveis e pesquisar primeiro nas páginas correspondentes.
- Se a busca restrita não trouxer evidência suficiente, ampliar para outras seções ou para o acervo completo.
- Responder com base nos trechos recuperados e citar livro e página. Se não encontrar suporte adequado, informar isso claramente.
- Processar todos os PDFs para que fiquem disponíveis à consulta, mas enviar ao modelo somente os trechos relevantes para cada pergunta; não carregar todos os livros integralmente no contexto de cada resposta.

## Persistência e atualização

- Salvar no Google Drive os dados processados para que sessões futuras do Colab possam reutilizá-los sem reler todos os PDFs.
- Persistir, por livro, ao menos os metadados do arquivo, páginas extraídas, mapa de seções, palavras-chave e índice de busca com referência às páginas.
- Detectar arquivos novos ou alterados e processar apenas os que precisarem de atualização.
- Permitir reconstruir o índice de um livro individual sem reprocessar toda a coleção.

## Direção técnica acordada

- Continuar em Python sempre que possível.
- A base atual é um notebook Colab com LlamaIndex, Gemini para geração de respostas, embeddings locais multilíngues, PyMuPDF para leitura de PDF e citações por página.
- A evolução planejada acrescenta catálogo de múltiplos livros, mapa de seções orientado pelo sumário e armazenamento persistente no Drive.
- Manter a lógica de catálogo, indexação, recuperação e resposta desacoplada da futura interface.

## Estado atual

O repositório remoto contém o notebook inicial `leitor_pdf_rpg.ipynb`, que implementa leitura de um PDF, divisão em trechos, índice vetorial, perguntas com citações de páginas, busca direta e chat com memória. O planejamento acordado é evoluir essa base para múltiplos PDFs no Drive, persistência entre sessões e recuperação guiada pelo sumário.

