#!/bin/bash

# Script para deploy do frontend do DataBridge na AWS
# Uso: ./deploy_frontend_aws.sh [BUCKET_NAME] [PROFILE]

# Cores para saída formatada
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sem cor

# Verifica se o AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo -e "${RED}AWS CLI não encontrado. Por favor, instale com:"
    echo -e "pip install awscli${NC}"
    exit 1
fi

# Parâmetros
BUCKET_NAME=${1:-"databridge-frontend"}
PROFILE=${2:-"default"}

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  DEPLOY DO FRONTEND DO DATABRIDGE    ${NC}"
echo -e "${BLUE}======================================${NC}"
echo -e "${YELLOW}Bucket: ${NC}$BUCKET_NAME"
echo -e "${YELLOW}Perfil AWS: ${NC}$PROFILE"
echo ""

# Verifica se o bucket existe
echo -e "${BLUE}[1/5]${NC} Verificando bucket S3..."
if aws s3 ls "s3://$BUCKET_NAME" --profile $PROFILE &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Bucket encontrado!"
else
    echo -e "  ${YELLOW}!${NC} Bucket não encontrado. Criando..."
    aws s3 mb "s3://$BUCKET_NAME" --profile $PROFILE
    
    # Configura o bucket para hospedar um site estático
    echo -e "  ${BLUE}→${NC} Configurando bucket para site estático..."
    aws s3 website "s3://$BUCKET_NAME" --index-document index.html --error-document index.html --profile $PROFILE
    
    # Define política de acesso público
    echo -e "  ${BLUE}→${NC} Configurando permissões do bucket..."
    POLICY="{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"PublicReadGetObject\",\"Effect\":\"Allow\",\"Principal\":\"*\",\"Action\":\"s3:GetObject\",\"Resource\":\"arn:aws:s3:::$BUCKET_NAME/*\"}]}"
    aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy "$POLICY" --profile $PROFILE
    
    echo -e "  ${GREEN}✓${NC} Bucket configurado com sucesso!"
fi

# Sincroniza arquivos
echo -e "${BLUE}[2/5]${NC} Preparando arquivos para deploy..."
FRONTEND_PATH="./databridge/frontend"

# Verifica se o diretório existe
if [ ! -d "$FRONTEND_PATH" ]; then
    echo -e "  ${RED}✗${NC} Diretório do frontend não encontrado: $FRONTEND_PATH"
    exit 1
fi

# Copia o index.html da raiz
echo -e "  ${BLUE}→${NC} Copiando arquivo de redirecionamento..."
cp index.html "$FRONTEND_PATH/redirect.html" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Arquivo de redirecionamento copiado."
else
    echo -e "  ${YELLOW}!${NC} Arquivo index.html não encontrado na raiz."
fi

# Sincroniza com o S3
echo -e "${BLUE}[3/5]${NC} Enviando arquivos para AWS S3..."
aws s3 sync $FRONTEND_PATH "s3://$BUCKET_NAME" --delete --profile $PROFILE

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} Arquivos enviados com sucesso!"
else
    echo -e "  ${RED}✗${NC} Erro ao enviar arquivos."
    exit 1
fi

# Configura tipos MIME corretos
echo -e "${BLUE}[4/5]${NC} Configurando tipos MIME corretos..."
aws s3 cp "s3://$BUCKET_NAME/" "s3://$BUCKET_NAME/" --recursive --content-type "text/html" --exclude "*" --include "*.html" --metadata-directive REPLACE --profile $PROFILE
aws s3 cp "s3://$BUCKET_NAME/" "s3://$BUCKET_NAME/" --recursive --content-type "text/css" --exclude "*" --include "*.css" --metadata-directive REPLACE --profile $PROFILE
aws s3 cp "s3://$BUCKET_NAME/" "s3://$BUCKET_NAME/" --recursive --content-type "application/javascript" --exclude "*" --include "*.js" --metadata-directive REPLACE --profile $PROFILE

echo -e "  ${GREEN}✓${NC} Tipos MIME configurados corretamente."

# Invalida cache no CloudFront se existir
echo -e "${BLUE}[5/5]${NC} Verificando distribuição CloudFront..."
DISTRIBUTION_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[?DomainName=='$BUCKET_NAME.s3.amazonaws.com']].Id" --output text --profile $PROFILE)

if [ -n "$DISTRIBUTION_ID" ]; then
    echo -e "  ${GREEN}✓${NC} Distribuição CloudFront encontrada: $DISTRIBUTION_ID"
    echo -e "  ${BLUE}→${NC} Invalidando cache..."
    aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*" --profile $PROFILE
    
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} Cache invalidado com sucesso!"
    else
        echo -e "  ${YELLOW}!${NC} Não foi possível invalidar o cache."
    fi
    
    # Obtém URL da distribuição
    CF_DOMAIN=$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.DomainName" --output text --profile $PROFILE)
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  DEPLOY CONCLUÍDO COM SUCESSO!       ${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo -e "Acesse seu site em: ${BLUE}https://$CF_DOMAIN${NC}"
else
    # Obtém URL do bucket do S3
    echo -e "  ${YELLOW}!${NC} Nenhuma distribuição CloudFront encontrada para este bucket."
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  DEPLOY CONCLUÍDO COM SUCESSO!       ${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo -e "Acesse seu site em: ${BLUE}http://$BUCKET_NAME.s3-website-$(aws configure get region --profile $PROFILE).amazonaws.com${NC}"
    echo -e ""
    echo -e "${YELLOW}Para melhor performance e HTTPS, considere configurar CloudFront.${NC}"
fi

echo ""
echo -e "${BLUE}Informações adicionais:${NC}"
echo -e "- Para configurar um domínio personalizado, use o Amazon Route 53"
echo -e "- Para configurar HTTPS, use AWS Certificate Manager com CloudFront"
echo -e "- Para monitoramento, ative o Amazon CloudWatch para o bucket S3"
echo ""