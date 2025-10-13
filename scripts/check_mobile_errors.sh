#!/bin/bash

# Script para verificar erros em cada tela/componente do mobile usando TypeScript typecheck

echo "Entrando no diretório mobile..."
cd /home/vinicius/Downloads/estudo/engenharia-software/gestao_notas/mobile

echo "Executando verificação de tipos TypeScript (typecheck) para detectar erros..."
npm run typecheck

if [ $? -eq 0 ]; then
    echo "Nenhum erro de tipo encontrado."
else
    echo "Erros de tipo detectados. Verifique a saída acima."
fi