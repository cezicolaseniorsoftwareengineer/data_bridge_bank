#!/bin/bash
# Script para fazer deploy da aplicação no Vercel

echo "Iniciando deploy no Vercel..."

# Instalar o Vercel CLI se ainda não estiver instalado
if ! command -v vercel &> /dev/null; then
    echo "Instalando Vercel CLI..."
    npm install -g vercel
fi

# Executar o comando de deploy
echo "Fazendo deploy no Vercel..."
vercel --prod

echo "Deploy no Vercel concluído!"