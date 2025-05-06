#!/bin/bash
# Script para deploy na AWS

# Verificar dependências
echo "Verificando AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "AWS CLI não encontrado. Por favor, instale com 'pip install awscli'"
    exit 1
fi

# Configurar variáveis
DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id databridge/db/password --query SecretString --output text)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

# Criar bucket S3 para o frontend
echo "Criando bucket S3 para o frontend..."
aws s3 mb s3://databridge-frontend-$AWS_ACCOUNT_ID

# Upload do frontend
echo "Fazendo upload do frontend para S3..."
aws s3 sync ./databridge/frontend s3://databridge-frontend-$AWS_ACCOUNT_ID --acl public-read

# Configurar CloudFront (opcional)
echo "Configurando CloudFront para o frontend..."
DISTRIBUTION_ID=$(aws cloudfront create-distribution   --origin-domain-name databridge-frontend-$AWS_ACCOUNT_ID.s3.amazonaws.com   --default-root-object index.html   --query "Distribution.Id"   --output text)

echo "Frontend disponível em: https://$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.DomainName" --output text)"

# Criar banco de dados RDS
echo "Criando instância RDS PostgreSQL..."
RDS_ENDPOINT=$(aws rds create-db-instance   --db-instance-identifier databridge-postgres   --db-instance-class db.t3.micro   --engine postgres   --master-username dbadmin   --master-user-password $DB_PASSWORD   --allocated-storage 20   --db-name databridge   --query "DBInstance.Endpoint.Address"   --output text)

echo "Aguardando RDS ficar disponível..."
aws rds wait db-instance-available --db-instance-identifier databridge-postgres

# Configurar Elastic Beanstalk
echo "Configurando Elastic Beanstalk..."
# Substituir placeholders nos arquivos de configuração
sed -i "s/RDS_ENDPOINT_PLACEHOLDER/$RDS_ENDPOINT/g" eb-config.yml
sed -i "s/RDS_USERNAME_PLACEHOLDER/dbadmin/g" eb-config.yml
sed -i "s/RDS_PASSWORD_PLACEHOLDER/$DB_PASSWORD/g" eb-config.yml
sed -i "s/RDS_DATABASE_PLACEHOLDER/databridge/g" eb-config.yml

# Criar aplicação Elastic Beanstalk
aws elasticbeanstalk create-application --application-name databridge-api

# Criar ambiente Elastic Beanstalk
echo "Criando ambiente Elastic Beanstalk..."
EB_CNAME=$(aws elasticbeanstalk create-environment   --application-name databridge-api   --environment-name databridge-api-prod   --solution-stack-name "64bit Amazon Linux 2 v3.5.0 running Python 3.9"   --option-settings file://eb-config.yml   --query "CNAME"   --output text)

echo "Elastic Beanstalk está sendo provisionado..."
aws elasticbeanstalk wait environment-exists --application-name databridge-api --environment-name databridge-api-prod

echo "=== DEPLOY CONCLUÍDO ==="
echo "Frontend: https://$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.DomainName" --output text)"
echo "API: http://$EB_CNAME/api/v1"
echo "Documentação API: http://$EB_CNAME/api/v1/docs"
