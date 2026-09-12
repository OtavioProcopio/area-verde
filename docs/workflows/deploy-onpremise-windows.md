# Deploy on-premise no notebook do bar (Windows)

Guia para colocar o Area Verde rodando de verdade no notebook Windows do bar,
com acesso remoto seguro para manutenção — sem expor o sistema na internet.

Relacionado: issue [#28](https://github.com/OtavioProcopio/area-verde/issues/28).

> O Docker Desktop no Windows exige virtualização (VT-x/AMD-V) via WSL2 ou
> Hyper-V. Se o notebook não suportar ou não permitir habilitar isso na
> BIOS, use o [deploy em VPS com Tailscale](./deploy-vps-tailscale.md) —
> mesma stack, mesmo modelo de acesso privado, rodando numa VPS Linux (que
> não precisa de virtualização aninhada) em vez do notebook.

## Arquitetura da solução

```text
┌─────────────────────────────┐        Tailscale         ┌──────────────────┐
│  Notebook do bar (Windows)  │◄──────(rede privada)─────►│  Seu computador  │
│                              │                            │  / celular       │
│  Docker Desktop              │                            └──────────────────┘
│  ├─ frontend (nginx :80)     │
│  ├─ api (interno, sem porta  │
│  │   publicada no host)      │
│  └─ db (Postgres, interno)   │
│                              │
│  OpenSSH Server (só          │
│  acessível via Tailscale)    │
└──────────────┬───────────────┘
               │ backup diário (scp)
               ▼
     ┌───────────────────┐
     │  Sua VPS           │   <- só recebe dumps .zip.
     │  (sem app rodando) │      Nunca hospeda o sistema.
     └───────────────────┘
```

Pontos-chave:

- O sistema **nunca fica exposto na internet**. O notebook não abre nenhuma
  porta no roteador do bar.
- Quem usa o sistema no dia a dia (você, seu pai, funcionários) acessa pelo
  navegador, na rede local do bar, em `http://<ip-do-notebook>`.
- Você faz manutenção remota entrando na mesma rede privada via
  [Tailscale](https://tailscale.com) e usando SSH — não precisa estar
  fisicamente lá.
- A VPS não hospeda nada do Area Verde. Ela só recebe uma cópia criptografada
  do backup do banco todo dia, como segurança extra caso o notebook tenha
  problema físico (furto, queda, HD morto).

## Pré-requisitos no notebook

- Windows 10 64-bit (versão 2004+) ou Windows 11.
- Virtualização habilitada na BIOS/UEFI (necessária para WSL2). Na maioria
  dos notebooks já vem habilitada; se o Docker Desktop reclamar disso na
  instalação, é só entrar na BIOS e ativar "Intel VT-x" / "AMD-V".
- Pelo menos 4 GB de RAM livres e 10 GB de disco livres.
- Conexão de internet (só é necessária para instalar, atualizar e enviar
  backup — o sistema funciona offline no dia a dia).

## Passo 1 — Instalar Docker Desktop

1. Baixe e instale o [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop/).
   O instalador já cuida de habilitar o WSL2 se necessário (pode pedir um
   reinício).
2. Abra o Docker Desktop uma vez para confirmar que ele inicia sem erro.
3. Em **Settings → General**, deixe marcado "Start Docker Desktop when you
   log in".

## Passo 2 — Trazer o código para o notebook

Instale o [Git para Windows](https://git-scm.com/download/win) e, num
PowerShell, clone os dois repositórios lado a lado — o compose espera essa
estrutura de pastas:

```powershell
mkdir C:\area-verde
cd C:\area-verde
git clone https://github.com/OtavioProcopio/area-verde.git backend
git clone https://github.com/OtavioProcopio/area-verde-frontend.git area-verde-frontend
```

Repare que a pasta do frontend precisa se chamar exatamente
`area-verde-frontend` (é o nome que `docker-compose.prod.yml` usa em
`context: ../area-verde-frontend/app`), enquanto a do backend pode ter
qualquer nome — aqui chamamos de `backend`.

## Passo 3 — Configurar o ambiente

```powershell
cd C:\area-verde\backend
copy .env.prod.example .env
notepad .env
```

No `.env`, defina uma `POSTGRES_PASSWORD` forte de verdade (o compose recusa
subir sem isso). Os demais valores padrão já servem para o cenário do bar.

## Passo 4 — Subir o sistema

```powershell
cd C:\area-verde\backend
docker compose -f docker-compose.prod.yml up --build -d
```

Isso builda as imagens, sobe Postgres + API + frontend, e aplica as
migrations automaticamente (`RUN_MIGRATIONS=true`).

## Passo 5 — Validar

```powershell
docker compose -f docker-compose.prod.yml ps
curl http://localhost/health
```

Abra `http://localhost` no navegador do próprio notebook — deve carregar a
tela de acesso do Area Verde. Em outro dispositivo na mesma rede Wi-Fi do
bar, troque `localhost` pelo IP do notebook (`ipconfig` no PowerShell mostra
o IP da rede local).

## Passo 6 — Iniciar sozinho após reiniciar o notebook

Com "Start Docker Desktop when you log in" habilitado (Passo 1), o Docker
Desktop já sobe automaticamente e, por padrão, reinicia os containers que
estavam rodando antes de desligar. Para garantir isso mesmo se essa opção
falhar, crie uma tarefa no Agendador de Tarefas do Windows:

1. Abra o **Agendador de Tarefas** → **Criar Tarefa Básica**.
2. Gatilho: **Ao fazer logon**.
3. Ação: **Iniciar um programa**.
   - Programa: `powershell.exe`
   - Argumentos: `-Command "cd C:\area-verde\backend; docker compose -f docker-compose.prod.yml up -d"`
4. Em "Condições", desmarque "Iniciar a tarefa somente se o computador
   estiver com energia CA" se o notebook ficar sempre na tomada (recomendado
   para um servidor de bar).

## Passo 7 — Acesso remoto seguro (Tailscale + SSH)

### 7.1 Instalar o Tailscale

No notebook do bar:

1. Baixe e instale o [Tailscale para Windows](https://tailscale.com/download/windows).
2. Faça login com uma conta (a sua, ou crie uma conta só para o bar).
3. O Tailscale vai atribuir um IP privado ao notebook, algo como
   `100.x.y.z` — anote-o (`tailscale ip` no PowerShell mostra).

No seu computador/celular:

1. Instale o Tailscale também e faça login com a **mesma conta**.
2. Os dois dispositivos agora enxergam um ao outro por esse IP privado,
   mesmo em redes diferentes — sem nenhuma porta aberta publicamente.

### 7.2 Habilitar SSH no Windows

O Windows 10/11 já vem com um servidor OpenSSH pronto para ativar:

```powershell
# Como Administrador
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
```

Restrinja o firewall do Windows para aceitar SSH **só** vindo da rede do
Tailscale (100.64.0.0/10), não da rede local do bar:

```powershell
Remove-NetFirewallRule -Name OpenSSH-Server-In-TCP -ErrorAction SilentlyContinue
New-NetFirewallRule -Name "SSH-Tailscale-Only" -DisplayName "SSH (somente Tailscale)" `
  -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow `
  -RemoteAddress 100.64.0.0/10
```

### 7.3 Testar o acesso remoto

Do seu computador, com o Tailscale conectado:

```bash
ssh usuario-do-notebook@100.x.y.z
```

Se conectar, o acesso remoto está funcionando — de qualquer lugar com
internet, sem VPN corporativa, sem porta exposta no roteador do bar.

## Passo 8 — Fluxo de atualização remota

Sempre que você corrigir algo e mergear na `develop`, para colocar no ar no
notebook do bar:

```bash
ssh usuario-do-notebook@100.x.y.z
cd C:\area-verde\backend
git pull origin develop
cd ..\area-verde-frontend
git pull origin develop
cd ..\backend
docker compose -f docker-compose.prod.yml up --build -d
```

O `up --build -d` só reconstrói o que mudou e reinicia os containers
afetados — o Postgres e os dados continuam intactos (ficam no volume
`area_verde_onprem_postgres_data`, fora dos containers).

## Passo 9 — Backup automático

Os scripts `scripts/backup-postgres.ps1` e `scripts/restore-postgres.ps1`
deste repositório cuidam do backup/restauração do Postgres.

### Agendar o backup diário

1. Abra o **Agendador de Tarefas** → **Criar Tarefa Básica**.
2. Gatilho: **Diariamente**, num horário fora do expediente do bar.
3. Ação: **Iniciar um programa**.
   - Programa: `powershell.exe`
   - Argumentos:
     `-ExecutionPolicy Bypass -File "C:\area-verde\backend\scripts\backup-postgres.ps1"`
     (adicione `-VpsHost "usuario@sua-vps.com"` no final se quiser enviar
     uma cópia para a VPS também).

Por padrão os backups ficam em `C:\area-verde\area-verde-backups\`
(fora dos repositórios git) com 14 dias de retenção local.

### Testar a restauração

Faça esse teste pelo menos uma vez, antes de depender do sistema em
produção — um backup que nunca foi restaurado é só uma esperança:

```powershell
cd C:\area-verde\backend
.\scripts\restore-postgres.ps1 -ZipFile ..\area-verde-backups\area-verde_2026-08-23_09-00.sql.zip
```

## Checklist de release

- [ ] Docker Desktop instalado e "start on login" habilitado.
- [ ] Repositórios clonados em `C:\area-verde\backend` e `C:\area-verde\area-verde-frontend`.
- [ ] `.env` configurado com senha forte.
- [ ] `docker compose -f docker-compose.prod.yml up --build -d` rodando sem erro.
- [ ] `http://localhost/health` responde `{"status":"UP"}`.
- [ ] Acesso pelo navegador de outro dispositivo na rede do bar confirmado.
- [ ] Tarefa de auto-start no logon criada e testada (reiniciar o notebook e conferir).
- [ ] Tailscale instalado no notebook e no seu dispositivo, IP anotado.
- [ ] SSH habilitado e restrito à rede do Tailscale; acesso remoto testado.
- [ ] Tarefa de backup diário criada.
- [ ] Um restore de teste executado com sucesso.
- [ ] Senha de acesso ao sistema trocada da padrão do MVP.

## Solução de problemas

**Container `db` fica saindo/reiniciando (`docker compose ... logs db` mostra
"Database is uninitialized and superuser password is not specified")**
O `.env` não foi criado ou está sem `POSTGRES_PASSWORD`. Repita o Passo 3 — a
própria imagem do Postgres recusa iniciar sem senha, então `api` e
`frontend` também nunca ficam saudáveis nesse caso.

**Frontend abre mas não carrega dados**
Confira se a API subiu: `docker compose -f docker-compose.prod.yml logs api`.
Geralmente é migration pendente ou banco ainda inicializando — espere o
healthcheck do `db` ficar `healthy` (`docker compose -f docker-compose.prod.yml ps`).

**Não consigo acessar via SSH pelo Tailscale**
Confirme que os dois dispositivos aparecem conectados em
`tailscale status`, e que o serviço `sshd` está com `Status: Running`
(`Get-Service sshd`).

**Preciso apagar tudo e recomeçar do zero (perde os dados)**

```powershell
docker compose -f docker-compose.prod.yml down -v
```
