"""
Configuração para deploy do DataBridge na AWS
Este script fornece instruções e configurações para migrar para a infraestrutura AWS
"""

import json
import os
import sys

# Configurações de AWS para serviços DataBridge
AWS_CONFIG = {
    "region": "us-east-1",  # Região padrão, pode ser alterada conforme necessário
    
    # RDS para PostgreSQL
    "rds": {
        "instance_type": "db.t3.micro",  # Instância de nível gratuito
        "storage_gb": 20,
        "engine": "postgres",
        "engine_version": "14.6",
        "database_name": "databridge",
        "master_username": "dbadmin",
        "port": 5432,
        "multi_az": False,  # Configurar como True para produção
        "backup_retention_days": 7
    },
    
    # DocumentDB para MongoDB (compatível com MongoDB 4.0)
    "documentdb": {
        "instance_type": "db.t3.medium",  # Tipo mínimo para DocumentDB
        "cluster_size": 1,  # Para produção, recomenda-se 3 para redundância
        "engine_version": "4.0.0",
        "database_name": "databridge",
        "port": 27017
    },
    
    # Alternativa: MongoDB Atlas via AWS Marketplace
    "mongodb_atlas": {
        "tier": "M0",  # Gratuito, ideal para desenvolvimento
        "cluster_type": "REPLICASET",
        "region": "US_EAST_1"
    },
    
    # Amazon MSK (Managed Streaming for Kafka)
    "msk": {
        "instance_type": "kafka.t3.small",
        "broker_count": 2,
        "kafka_version": "2.8.1",
        "storage_gb": 100
    },
    
    # Elastic Beanstalk para API
    "elastic_beanstalk": {
        "solution_stack": "64bit Amazon Linux 2 v3.5.0 running Python 3.9",
        "instance_type": "t3.micro",
        "load_balancer": True,
        "environment_type": "LoadBalanced"
    },
    
    # Lambda + API Gateway (alternativa ao Elastic Beanstalk)
    "lambda": {
        "runtime": "python3.9",
        "timeout": 30,  # segundos
        "memory": 512  # MB
    },
    
    # S3 + CloudFront para Frontend
    "frontend": {
        "s3_bucket_region": "us-east-1",
        "cloudfront_price_class": "PriceClass_100"  # Mais barato, apenas América do Norte e Europa
    }
}

def generate_terraform_config():
    """Gera um arquivo de configuração Terraform para AWS"""
    terraform_config = {
        "provider": {
            "aws": {
                "region": AWS_CONFIG["region"]
            }
        },
        "resource": {
            "aws_db_instance": {
                "databridge_postgres": {
                    "allocated_storage": AWS_CONFIG["rds"]["storage_gb"],
                    "engine": AWS_CONFIG["rds"]["engine"],
                    "engine_version": AWS_CONFIG["rds"]["engine_version"],
                    "instance_class": AWS_CONFIG["rds"]["instance_type"],
                    "name": AWS_CONFIG["rds"]["database_name"],
                    "username": AWS_CONFIG["rds"]["master_username"],
                    "password": "${var.db_password}",
                    "parameter_group_name": "default.postgres14",
                    "skip_final_snapshot": True,
                    "publicly_accessible": True
                }
            },
            "aws_s3_bucket": {
                "databridge_frontend": {
                    "bucket": "databridge-frontend",
                    "acl": "public-read",
                    "website": {
                        "index_document": "index.html",
                        "error_document": "error.html"
                    }
                }
            },
            "aws_elastic_beanstalk_application": {
                "databridge_api": {
                    "name": "databridge-api",
                    "description": "DataBridge API Application"
                }
            },
            "aws_elastic_beanstalk_environment": {
                "databridge_api_env": {
                    "name": "databridge-api-env",
                    "application": "${aws_elastic_beanstalk_application.databridge_api.name}",
                    "solution_stack_name": AWS_CONFIG["elastic_beanstalk"]["solution_stack"],
                    "setting": [
                        {
                            "namespace": "aws:autoscaling:launchconfiguration",
                            "name": "InstanceType",
                            "value": AWS_CONFIG["elastic_beanstalk"]["instance_type"]
                        },
                        {
                            "namespace": "aws:elasticbeanstalk:application:environment",
                            "name": "POSTGRES_SERVER",
                            "value": "${aws_db_instance.databridge_postgres.address}"
                        },
                        {
                            "namespace": "aws:elasticbeanstalk:application:environment",
                            "name": "POSTGRES_USER",
                            "value": "${aws_db_instance.databridge_postgres.username}"
                        },
                        {
                            "namespace": "aws:elasticbeanstalk:application:environment",
                            "name": "POSTGRES_PASSWORD",
                            "value": "${var.db_password}"
                        },
                        {
                            "namespace": "aws:elasticbeanstalk:application:environment",
                            "name": "POSTGRES_DB",
                            "value": "${aws_db_instance.databridge_postgres.name}"
                        },
                        {
                            "namespace": "aws:elasticbeanstalk:application:environment",
                            "name": "ENVIRONMENT",
                            "value": "production"
                        }
                    ]
                }
            }
        },
        "output": {
            "postgres_endpoint": {
                "value": "${aws_db_instance.databridge_postgres.endpoint}"
            },
            "api_endpoint": {
                "value": "${aws_elastic_beanstalk_environment.databridge_api_env.cname}"
            },
            "frontend_url": {
                "value": "${aws_s3_bucket.databridge_frontend.website_endpoint}"
            }
        },
        "variable": {
            "db_password": {
                "description": "PostgreSQL master password",
                "type": "string",
                "sensitive": True
            }
        }
    }
    
    # Salvar em arquivo
    with open("terraform_aws_databridge.tf.json", "w") as f:
        json.dump(terraform_config, f, indent=2)
    
    print("✓ Arquivo de configuração Terraform gerado: terraform_aws_databridge.tf.json")

def generate_cloudformation_template():
    """Gera um template CloudFormation para AWS"""
    # Template básico simplificado
    template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "DataBridge Bank Infrastructure",
        "Parameters": {
            "DBPassword": {
                "NoEcho": "true",
                "Description": "PostgreSQL database password",
                "Type": "String",
                "MinLength": "8",
                "MaxLength": "41",
                "AllowedPattern": "[a-zA-Z0-9]*",
                "ConstraintDescription": "must contain only alphanumeric characters"
            }
        },
        "Resources": {
            "PostgreSQLInstance": {
                "Type": "AWS::RDS::DBInstance",
                "Properties": {
                    "AllocatedStorage": str(AWS_CONFIG["rds"]["storage_gb"]),
                    "DBInstanceClass": AWS_CONFIG["rds"]["instance_type"],
                    "Engine": AWS_CONFIG["rds"]["engine"],
                    "EngineVersion": AWS_CONFIG["rds"]["engine_version"],
                    "MasterUsername": AWS_CONFIG["rds"]["master_username"],
                    "MasterUserPassword": {"Ref": "DBPassword"},
                    "DBName": AWS_CONFIG["rds"]["database_name"],
                    "PubliclyAccessible": True
                }
            },
            "DataBridgeFrontendBucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "AccessControl": "PublicRead",
                    "WebsiteConfiguration": {
                        "IndexDocument": "index.html",
                        "ErrorDocument": "error.html"
                    }
                }
            },
            "BucketPolicy": {
                "Type": "AWS::S3::BucketPolicy",
                "Properties": {
                    "PolicyDocument": {
                        "Id": "PublicReadPolicy",
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Sid": "PublicReadGetObject",
                                "Effect": "Allow",
                                "Principal": "*",
                                "Action": "s3:GetObject",
                                "Resource": {
                                    "Fn::Join": [
                                        "",
                                        [
                                            "arn:aws:s3:::",
                                            {"Ref": "DataBridgeFrontendBucket"},
                                            "/*"
                                        ]
                                    ]
                                }
                            }
                        ]
                    },
                    "Bucket": {"Ref": "DataBridgeFrontendBucket"}
                }
            }
        },
        "Outputs": {
            "WebsiteURL": {
                "Description": "URL for the DataBridge frontend",
                "Value": {"Fn::GetAtt": ["DataBridgeFrontendBucket", "WebsiteURL"]}
            },
            "PostgreSQLEndpoint": {
                "Description": "Endpoint of the PostgreSQL database",
                "Value": {"Fn::GetAtt": ["PostgreSQLInstance", "Endpoint.Address"]}
            }
        }
    }
    
    # Salvar em arquivo
    with open("cloudformation_databridge.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("✓ Template CloudFormation gerado: cloudformation_databridge.json")

def configure_aws_amplify():
    """Gera configuração para AWS Amplify (alternativa para frontend + backend)"""
    amplify_config = {
        "providers": {
            "awscloudformation": {
                "AuthRoleName": "databridge-auth-role",
                "UnauthRoleName": "databridge-unauth-role",
                "AuthRoleArn": "arn:aws:iam::ACCOUNT_ID:role/databridge-auth-role",
                "UnauthRoleArn": "arn:aws:iam::ACCOUNT_ID:role/databridge-unauth-role",
                "Region": AWS_CONFIG["region"],
                "DeploymentBucketName": "databridge-deployment",
                "StackName": "databridge-amplify-stack",
                "StackId": "STACK_ID"
            }
        },
        "api": {
            "databridge": {
                "service": "AppSync",
                "output": {
                    "authConfig": {
                        "defaultAuthentication": {
                            "authenticationType": "API_KEY"
                        }
                    }
                }
            },
            "restapi": {
                "service": "API Gateway",
                "paths": {
                    "/api": {
                        "lambdaFunction": "databridgeFunction"
                    }
                }
            }
        },
        "function": {
            "databridgeFunction": {
                "build": True,
                "providerPlugin": "awscloudformation",
                "service": "Lambda",
                "dependsOn": [
                    {
                        "category": "storage",
                        "resourceName": "databridgedb",
                        "attributes": ["Name"]
                    }
                ]
            }
        },
        "storage": {
            "databridgedb": {
                "service": "RDS",
                "providerPlugin": "awscloudformation",
                "engine": "postgres",
                "engineVersion": AWS_CONFIG["rds"]["engine_version"],
                "instanceClass": AWS_CONFIG["rds"]["instance_type"],
                "storagetype": "gp2",
                "allocatedstorage": AWS_CONFIG["rds"]["storage_gb"],
                "name": AWS_CONFIG["rds"]["database_name"],
                "username": AWS_CONFIG["rds"]["master_username"]
            },
            "databridgestorage": {
                "service": "S3",
                "providerPlugin": "awscloudformation"
            }
        }
    }
    
    # Salvar em arquivo
    with open("amplify_config.json", "w") as f:
        json.dump(amplify_config, f, indent=2)
    
    print("✓ Configuração AWS Amplify gerada: amplify_config.json")

def generate_aws_deployment_files():
    """Gera arquivos de configuração para deployment AWS"""
    # Gerar configuração para Elastic Beanstalk
    eb_config = """
# Elastic Beanstalk Configuration
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: databridge/app/main:app
  aws:elasticbeanstalk:application:environment:
    PYTHONPATH: /var/app
    POSTGRES_SERVER: RDS_ENDPOINT_PLACEHOLDER
    POSTGRES_USER: RDS_USERNAME_PLACEHOLDER
    POSTGRES_PASSWORD: RDS_PASSWORD_PLACEHOLDER
    POSTGRES_DB: RDS_DATABASE_PLACEHOLDER
    MONGODB_URI: MONGODB_URI_PLACEHOLDER
    ENVIRONMENT: production
  aws:elasticbeanstalk:environment:
    EnvironmentType: LoadBalanced
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.micro
    SecurityGroups: SECURITY_GROUP_PLACEHOLDER
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 4
"""
    with open("eb-config.yml", "w") as f:
        f.write(eb_config)
    
    # Gerar Dockerfile para containerização
    dockerfile = """
FROM python:3.9-slim

WORKDIR /app

COPY ./databridge ./databridge
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Configuração de porta
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "databridge.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    with open("Dockerfile.aws", "w") as f:
        f.write(dockerfile)
    
    # Gerar scripts para deploy
    deploy_script = """#!/bin/bash
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
DISTRIBUTION_ID=$(aws cloudfront create-distribution \
  --origin-domain-name databridge-frontend-$AWS_ACCOUNT_ID.s3.amazonaws.com \
  --default-root-object index.html \
  --query "Distribution.Id" \
  --output text)

echo "Frontend disponível em: https://$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.DomainName" --output text)"

# Criar banco de dados RDS
echo "Criando instância RDS PostgreSQL..."
RDS_ENDPOINT=$(aws rds create-db-instance \
  --db-instance-identifier databridge-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username dbadmin \
  --master-user-password $DB_PASSWORD \
  --allocated-storage 20 \
  --db-name databridge \
  --query "DBInstance.Endpoint.Address" \
  --output text)

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
EB_CNAME=$(aws elasticbeanstalk create-environment \
  --application-name databridge-api \
  --environment-name databridge-api-prod \
  --solution-stack-name "64bit Amazon Linux 2 v3.5.0 running Python 3.9" \
  --option-settings file://eb-config.yml \
  --query "CNAME" \
  --output text)

echo "Elastic Beanstalk está sendo provisionado..."
aws elasticbeanstalk wait environment-exists --application-name databridge-api --environment-name databridge-api-prod

echo "=== DEPLOY CONCLUÍDO ==="
echo "Frontend: https://$(aws cloudfront get-distribution --id $DISTRIBUTION_ID --query "Distribution.DomainName" --output text)"
echo "API: http://$EB_CNAME/api/v1"
echo "Documentação API: http://$EB_CNAME/api/v1/docs"
"""
    with open("deploy_aws.sh", "w") as f:
        f.write(deploy_script)
    
    # Tornar o script executável
    os.chmod("deploy_aws.sh", 0o755)
    
    print("✓ Arquivos de configuração AWS gerados:")
    print("  - eb-config.yml (configuração Elastic Beanstalk)")
    print("  - Dockerfile.aws (para containerização)")
    print("  - deploy_aws.sh (script de automação do deploy)")

def print_aws_instructions():
    """Imprime instruções detalhadas para deploy na AWS"""
    print("\n==== INSTRUÇÕES PARA DEPLOY DO DATABRIDGE NA AWS ====\n")
    
    print("1. PRÉ-REQUISITOS")
    print("   - Conta AWS ativa")
    print("   - AWS CLI instalado e configurado ('pip install awscli')")
    print("   - Credenciais configuradas ('aws configure')")
    print("   - Permissões para criar RDS, S3, Elastic Beanstalk, CloudFront")
    
    print("\n2. OPÇÕES DE DEPLOY")
    print("   A. Deploy Automatizado:")
    print("      - Execute o script 'deploy_aws.sh' (requer AWS CLI)")
    print("      - O script criará toda a infraestrutura necessária")
    
    print("   B. Terraform (infraestrutura como código):")
    print("      - Instale o Terraform: https://www.terraform.io/downloads.html")
    print("      - Execute: terraform init")
    print("      - Execute: terraform apply")
    
    print("   C. AWS Management Console (manual):")
    print("      - Siga as etapas detalhadas abaixo")
    
    print("\n3. ETAPAS PARA DEPLOY MANUAL")
    print("   3.1 Banco de Dados PostgreSQL (RDS):")
    print("       - Acesse o AWS Console > RDS")
    print("       - Crie uma instância PostgreSQL (t3.micro para nível gratuito)")
    print("       - Configure o nome do banco, usuário e senha")
    print("       - Anote o endpoint para usar na configuração da API")
    
    print("   3.2 MongoDB (DocumentDB ou MongoDB Atlas):")
    print("       - Opção AWS nativa: Crie um cluster DocumentDB")
    print("       - Opção parceiro: Use MongoDB Atlas via AWS Marketplace")
    print("       - Anote a URI de conexão")
    
    print("   3.3 Deploy do Backend (Elastic Beanstalk):")
    print("       - Acesse o AWS Console > Elastic Beanstalk")
    print("       - Crie uma nova aplicação 'databridge-api'")
    print("       - Use a plataforma Python 3.9")
    print("       - Faça upload do código (ZIP com toda a pasta databridge)")
    print("       - Configure variáveis de ambiente:")
    print("         * POSTGRES_SERVER=<endpoint-rds>")
    print("         * POSTGRES_USER=<usuário-rds>")
    print("         * POSTGRES_PASSWORD=<senha-rds>")
    print("         * POSTGRES_DB=databridge")
    print("         * MONGODB_URI=<uri-mongodb>")
    print("         * ENVIRONMENT=production")
    
    print("   3.4 Deploy do Frontend (S3 + CloudFront):")
    print("       - Crie um bucket S3 (ex: databridge-frontend)")
    print("       - Habilite hospedagem de site estático")
    print("       - Configure documento de índice: index.html")
    print("       - Configure políticas para acesso público")
    print("       - Upload de todos os arquivos da pasta databridge/frontend")
    print("       - Atualize api-config.js para apontar para a URL do Elastic Beanstalk")
    print("       - Opcional: Configure CloudFront para CDN e HTTPS")
    
    print("\n4. VERIFICAÇÃO")
    print("   - Frontend: Acesse a URL do S3 ou CloudFront")
    print("   - API: Teste a URL do Elastic Beanstalk /api/v1/health")
    print("   - Documentação: Acesse /api/v1/docs")
    
    print("\n5. MONITORAMENTO E MANUTENÇÃO")
    print("   - Configure alarmes no CloudWatch")
    print("   - Considere habilitar backups automáticos para RDS")
    print("   - Implemente estratégia de CI/CD com AWS CodePipeline")
    
    print("\nObs: Para ambiente de produção, considere implementar:")
    print("  - AWS WAF para proteção de aplicação web")
    print("  - Route 53 para gestão de domínio personalizado")
    print("  - AWS Secrets Manager para armazenar senhas e chaves")
    print("  - Multi-AZ para alta disponibilidade de bancos de dados")

def main():
    print("\nConfiguração do DataBridge Bank para AWS\n")
    
    # Gerar arquivos de configuração
    generate_terraform_config()
    generate_cloudformation_template()
    configure_aws_amplify()
    generate_aws_deployment_files()
    
    # Imprimir instruções
    print_aws_instructions()
    
    print("\nTodos os arquivos de configuração para AWS foram gerados.")
    print("Use estes arquivos para fazer o deploy da aplicação DataBridge na AWS.")
    print("Para mais detalhes, consulte a documentação da AWS.")

if __name__ == "__main__":
    main()