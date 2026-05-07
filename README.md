# Modelos geológicos 3D na pesquisa educacional em Geociências
O Grupo de Pesquisa 3D Bacias, vinculado ao IG-Unicamp, com apoio do Centro de Tecnologia de Informação Renato Archer (CTI) vem desenvolvendo modelos gerados por impressoras 3D, cuja utilização didática é pesquisada por vários projetos em paralelo. O campo da modelagem tridimensional tem interesse direto a vários campos do conhecimento, básicos e aplicados, mas ainda são escassas as publicações na área de Geociências em Português sobre o tema. O projeto retomará o modelo 3D da Bacia do Paraná, gerado por manufatura aditiva, e aplicá-lo na pesquisa educacional.

# Configurando ambiente
Para configurar o ambiente clone este repositório em seu computador, é necessário ter o Git LFS instalado.
```
git clone https://github.com/nukhes/modelagem-bacia
pip install -r requirements.txt
```

## Instalando pacotes pip no Blender
O script para modelar as informações no Blender usa os módulos "scipy" e "numpy", para instalar estes em máquinas rodando Ubuntu Linux basta rodar o comando abaixo no terminal

```bash
sudo apt install python3-numpy python3-scipy
```

Em computadores Windows o processo envolve descobrir aonde o binário do Python embutido no Blender procura por módulos e usar o Python do sistema para intalar o módulo lá

1. Descobrir a pasta
Rode esse comando no Shell interativo de Python do Blender
```bash
bpy.utils.user_resource("SCRIPTS", path="modules")
```

2. Instalar com o alvo correto
```bash
pip install numpy scipy --target="<PASTA_MODULES>"
```

# Especificações e arquitetura técnica

## Preparação
Os arquivos já processados estão versionado no repositório, tornando esta etapa opcional, mas caso queira rodar o fluxo de processamento em seu computador insira o comando abaixo no seu terminal.

```bash
python scripts/bacia_parana/main.py 
```

### Modelagem
Com o arquivo 'data/processed/20260503_pocos_parana.csv' temos todas as informações para modelar a bacia no Blender usando a aba "Scripting" do programa, basta carregar o script de modelagem em `./scripts/blender_model.py` e ajustar o caminho do dataset.

### Educação
PARA FAZER: preciso consultar o Dr. Celso para entender melhor essa parte.

