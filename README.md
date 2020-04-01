# Wasabi

`Wasabi` é uma plataforma que permite o desenvolvimento de pipeline customizada. Utilizando uma estrutura simples no formato `yml`, 
o desenvolvedor escreve a esturura que deseja da pipeline e o `wasabi` transforma o template em `cloudformation` e aplica na conta.

`Wasabi` permite que o desenvolvimento das pipelines adicione e remova `actions` e `stages` em uma pipeline no momento que desejar, mantendo o histórico 
e assim gerando autonomia para os desenvolvedores.
 
## Api do Wasabi

`Wasabi` habilitou as seguintes `API`

## Provisionando o Wasabi

## Templates

O desenvolvimento da pipeline é realizada através do arquivo `pipeline.yml` no diretório  `pipeline`. A estrutura do arquivo deve
seguir a seguinte estrutura:  

```
---
version: 1
template: app-ecs
runtime: python37
provider: aws
Parameter:
    - Projeto: Pipeline-Python
pipeline:
    - source
    - ci
    - security
    - publish
    - deploy
callback:
    protocolo: email
    endpoint: clodonil@nisled.org
```

Explicação do arquivo linha a linha:

### Cabeçalho do arquivo:

* **version: 1** : Versão do arquivo `pipeline.yml` suportado pelo `wasabi`;
* **template: `app-ecs`** : Template utilizado pelo `Wasabi` para desenvolvimento da pipeline. Consulte [Api](), para conhecer todos os templates;
* **runtime: `python37`**: Runtime suportado pelo `Wasabi`. Consulte [Api](), para conhecer todos os runtimes disponiveis;
* **provider: `aws`**: Provider suportado pelo `Wasabi`. Atualmente apenas o provider `AWS` está disponibilizado.

### Parâmetros da pipeline:

* **Parameter**:
* **Projeto: `Pipeline-Python`**: Nome da pipeline.
* **AprovadorBO: `email_do_aprovador_negocio`**: Email do aprovador B.O
* **AprovadorPO: `email_do_aprovador_tecnico`**: Email do aprovador técnico.

### Estrutura da pipeline

A estrutura da pipeline está relacionando com o parâmetros `template` definido no cabeçalho. Cada tipo de template tem 
uma estrutura diferente. Consulte a [API]() para obter os exemplos de cada template.

* **pipeline**: Definição da estrutura da pipeline, todos os `stages` abaixo são obrigatórios.
* **- source**: Adiciona o source padrão do projeto. O nome do repositório é o mesmo definido no projeto
* **- ci** :  Adiciona os `stages` de CI.
* **- security**: Adiciona os `stages` de segurança do containner
* **- publish**: Adiciona o Publish do container no ECR
* **- deploy**: Realiza o deploy do container no ECS
    
FeedBack do Provisionamento da Pipeline
 
* **callback:** : Os campo de callback é a forma que o `Wasabi` utiliza para dar retorno em caso de falha no provisiomento da pipeline. 
* **protocolo: email**: Protocolo suportado para realizar o feedback. 
* **endpoint: `email_para_feedback**: Email para envio do feedback

## Customização do template

Utilizado um template definido no arquivo `pipeline.yml` é possivel customizar de acordo com a necessidade do projeto. 
A customização é realizada nos `stages` da pipeline, vamos utilizando os seguintes `stages` como exemplo:

```
pipeline:
    - source
    - ci
    - security
    - publish
    - deploy
```

### Customizando o Source
Vamos customizar a pipeline adicionando um novo `source` no projeto. Com o parâmetro `RepositoryName` e `BranchName` são definidos
o nome do repositório e a branch que será utilizada. Se a branch não for definidos será utilizada a `develop` para a pipeline de 
desenvolvimento e `master` para a pipeline de produção. 

`Wasabi` não cria os repositórios, é necessários que eles já estevam criados e sincronizados.

```
pipeline:
    - source
    - source::custom:
        - BranchName: master
        - RepositoryName: Tools                
    - ci
    - security
    - publish
    - deploy
```

### Adicinando um novo Action

Nessa customização vamos adicionar um novo `Action` em um stage já existente. No exemplo, vamos utilizar o `stage` do CI, 
o mesmo processo pode ser realizado em qualquer outro `stage`.

No `stage` que deseja customizar, adicione a tag ::custom para sinalizar para o `Wasabi` que um novo `action` será adicionado,
como no exemplo `ci::custom:`.

Dentro do `stage` customizado, adicione o nome do stage, a origin dos artefatos e as variáveis de ambiente. Também é possível
utilizar uma imagem customizada.

Segue a descrição linha a linha do exemplo:

* **- testmultant:** : Nome do `Stage` que será adicionando;
* **- source: Build** : Origim dos artefatos, pode ser um `source` ou outros `Actions`;
* **- environment:** : Define a variável de ambiente quer será utilizado no codebuild;
* **- imagecustom: linuxcustom** : Opcional, pode ser definido uma imagem customizada, caso não seja definido, o amazonlinux, será utilizado;
* **- runorder: 2** : Posicionamento do `Action` no stage.

O exemplo: 

```
pipeline:
    - source
    - ci::custom:
        - testmultant:
            - source: Build
            - environment:
                - Name : chave
                - Value: valor
            - imagecustom: linuxcustom
            - runorder: 2
    - security
    - publish
    - deploy
```
Para cada `action` é necessário ter um arquivo de `buildspec` que descreve os comandos que serão executado. Portanto é necessário 
criar o arquivo com o `nome_do_stage_buildspec.yml` no diretório `pipeline`. No exemplo o arquivo ficaria com o seguinte nome `testmultant_buildspec.yml`.

### Adicinando um novo Stage

Nessa customização vamos adicionar um novo `Stage` na pipeline. No exemplo, vamos adicionar um novo `stage` entre os `stages` Publish e Deploy.
Para criar um novo `Stage` adicione uma nova linha com `custom::nome_do_stage`.
Dentro do `Action` customizado, adicione o nome dos `stage` a origin dos artefatos e as variáveis de ambiente. Também é possível
utilizar uma imagem customizada.

Segue a descrição linha a linha do exemplo:

* **- testmultant:** : Nome do `Stage` que será adicionando;
* **- source: Build** : Origim dos artefatos, pode ser um `source` ou outros `Actions`;
* **- environment:** : Define a variável de ambiente quer será utilizado no codebuild;
* **- imagecustom: linuxcustom** : Opcional, pode ser definido uma imagem customizada, caso não seja definido, o amazonlinux, será utilizado;
* **- runorder: 2** : Pocionamento do `Action` no stage.

O exemplo: 

```
pipeline:
    - source
    - ci
    - security
    - publish
    - custom::Seguranca:
        - seguranca1:
            - source: Build
            - environment:
                - Name : chave
                - Value: valor
            - imagecustom: linuxcustom
            - runorder: 1
        - seguranca2:
            - source: Build
            - environment:
                - Name : chave
                - Value: valor
            - imagecustom: linuxcustom
            - runorder: 2           
    - deploy
```

## Validando o template


## Aplicando o template e criando a Pipeline

Após a criação/alteração do  template no formato `yml` estar pronto, é importante validar antes de enviar para o `Wasabi`.

Utilize a `API` do `Wasabi` para fazer uma validação completa do template. Pode ser utilizado o `curl` ou o `PostMan` para essa validação.

`curl  xxxxx payload`

Após a validação validação do template, 

```
git add pipeline/pipeline.yml
git commit -am "wasabi.run()"
```

Ao realizar o `commit`, um validação prévia é realizada na conta de `tools` do projeto e uma mensagem de status é enviado no comentário do `commit` no `codecommit`.

![codecommit][url]

Ao passar pela analise prévia, o template `yml` é enviado para processamento pelo `Wasabi` e em caso de erro, uma mensagem é enviado para o campo cadastrado no  `callback` do template.

```
callback:
    protocolo: email
    endpoint: clodonil@nisled.org
```