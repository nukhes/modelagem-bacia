# Modelos geológicos 3D na pesquisa educacional em Geociências
O Grupo de Pesquisa 3D Bacias, vinculado ao IG-Unicamp, com apoio do Centro de Tecnologia de Informação Renato Archer (CTI) vem desenvolvendo modelos gerados por impressoras 3D, cuja utilização didática é pesquisada por vários projetos em paralelo. O campo da modelagem tridimensional tem interesse direto a vários campos do conhecimento, básicos e aplicados, mas ainda são escassas as publicações na área de Geociências em Português sobre o tema. O projeto retomará o modelo 3D da Bacia do Paraná, gerado por manufatura aditiva, e aplicá-lo na pesquisa educacional.

---

## Especificações e arquitetura técnica

### Preparação
Os dados de coornadas de poços (ANP) e topografia (INPE) precisam ser consolidados em um arquivo só, isso é feito com Python por meio da biblioteca CSV, de modo que o resultado final é uma seguindo as especificações de colunas abaixo.

| id | x_utm | y_utm | z_surf | formation_top | z_abs
| --------------- | --------------- | --------------- | --------------- | --------------- | --------------- |
| Identificador do poço | Coordenada Leste em metros | Coordenada Norte em metros | Altitude do terreno no topo do poço | Profundida do topo da camada alvo | Cota absoluta (z_surf - formation_top) 

Com esse modelo podemos registrar para cada poço quantas camadas forem necessárias de forma escalável.

Pode parecer redundante manter `z_abs` quanto temos `z_surf` e `formation_top`, entretanto com o valor absoluto pré-cálculado economizamos recursos computacionais com um custo virtualmente nulo de espaço.

### Modelagem
Com o arquivo final da etapa anterior temos todas as informações para modelar a bacia no Blender usando a aba "Scripting" do programa, basta carregar o script de modelagem em `./scripts/blender_model.py` e ajustar o caminho do dataset.

### Educação
PARA FAZER: preciso consultar o Dr. Celso para entender melhor essa parte.

---

## Setup
Para configurar o ambiente clone este repositório em seu computador
```
git clone https://github.com/nukhes/modelagem-bacia
```

### Instalando pacotes pip no Blender
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

