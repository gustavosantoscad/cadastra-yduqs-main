# Attachments - Arquivos Complementares

Este diretório armazena anexos e arquivos complementares que suportam documentação e desenvolvimento do projeto Yduqs. Aqui residem assets visuais, planilhas de referência, designs, mockups e outros materiais não-textuais que complementam documentação técnica ou servem como recursos para desenvolvimento.

## Propósito

O objetivo deste espaço é centralizar arquivos de suporte que não se enquadram em categorias mais específicas como código ou documentação técnica formal. Estes materiais auxiliam compreensão de requisitos, comunicação de ideias e desenvolvimento de soluções, mas não são necessariamente artefatos de código ou especificações técnicas formais.

Organizar estes materiais de forma estruturada facilita localização quando necessário e evita duplicação de arquivos. Manutenção apropriada deste diretório garante que recursos permaneçam acessíveis e relevantes ao longo do tempo.

## Tipos de Conteúdo

Este diretório pode conter diversos tipos de arquivos complementares. Designs e mockups visuais de interfaces ou arquiteturas ajudam comunicação de ideias e requisitos visuais. Planilhas com dados de referência, cálculos ou especificações técnicas fornecem informações estruturadas complementares à documentação.

Diagramas originais em formatos editáveis permitem manutenção e evolução de representações visuais de sistemas. Imagens e assets utilizados em documentação garantem que recursos visuais estejam versionados junto com conteúdo que os referencia. Templates de documentos e apresentações padronizam comunicação e facilitam criação de novos materiais.

## Organização e Nomenclatura

Organize arquivos em subdiretórios lógicos baseados em projeto, sistema ou tipo de conteúdo. Utilize nomenclatura descritiva facilitando identificação do propósito e conteúdo de cada arquivo sem necessidade de abri-lo.

Evite caracteres especiais ou espaços em nomes de arquivos, preferindo hífens ou underscores para separação de palavras. Inclua datas ou números de versão em nomes de arquivo quando relevante, especialmente para materiais que evoluem frequentemente.

## Controle de Versão

Arquivos binários como imagens, planilhas Excel ou arquivos de design podem ser desafiadores para versionamento efetivo. Git rastreia mudanças mas não permite merge automático ou visualização fácil de diferenças.

Para arquivos que mudam frequentemente, considere manter apenas versão mais recente no repositório e utilizar sistemas especializados como Google Drive ou Figma para colaboração e versionamento mais granular. Inclua links para estes sistemas externos na documentação quando apropriado.

## Tamanho e Performance

Arquivos binários grandes podem impactar negativamente performance do repositório git. Limite tamanho de arquivos individuais a alguns megabytes quando possível. Para arquivos maiores como vídeos, apresentações complexas ou datasets, considere armazenamento em sistemas externos como Google Cloud Storage, referenciando-os via URLs na documentação.

Revise periodicamente o diretório removendo arquivos obsoletos ou não mais utilizados. Arquivos históricos importantes podem ser movidos para storage de longo prazo mantendo repositório enxuto e performático.

## Formatos Recomendados

Quando possível, utilize formatos abertos e amplamente suportados facilitando acesso por diferentes membros da equipe independente de ferramentas específicas instaladas. Para imagens, PNG ou SVG são preferíveis a formatos proprietários. Para planilhas, CSV ou formatos do Google Sheets são mais acessíveis que Excel quando não há necessidade de funcionalidades avançadas.

Para diagramas técnicos, considere formatos baseados em texto como PlantUML ou Mermaid que podem ser versionados efetivamente e renderizados sob demanda. Estes formatos facilitam colaboração e permitem visualização de mudanças ao longo do tempo.
