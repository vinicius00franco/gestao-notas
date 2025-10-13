#!/bin/bash

# Script para inicializar o mobile: instalar dependências e iniciar o servidor Expo

echo "Entrando no diretório mobile..."
cd /home/vinicius/Downloads/estudo/engenharia-software/gestao_notas/mobile

echo "Instalando dependências com npm install..."
npm install

if [ $? -eq 0 ]; then
    echo "Dependências instaladas com sucesso."
    echo "Iniciando o servidor Expo com npm start..."
    npm start
else
    echo "Erro ao instalar dependências."
    exit 1
fi