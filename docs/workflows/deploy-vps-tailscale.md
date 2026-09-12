# Deploy em VPS com Tailscale

Guia para colocar o Area Verde rodando numa VPS Linux, acessível apenas pelo
notebook do bar e pelos celulares de quem precisar — sem expor o sistema na
internet pública. Alternativa ao
[deploy on-premise no notebook Windows](./deploy-onpremise-windows.md) para
quando a máquina do bar não suporta virtualização (Docker Desktop no Windows
exige VT-x/AMD-V; Docker num servidor Linux não precisa disso).

## Arquitetura da solução

```text
                        Tailscale (rede privada, MagicDNS)
                                     │
        ┌────────────────────────────┼────────────────────────────┐
        │                            │                            │
┌───────▼────────┐          ┌────────▼─────────┐          ┌───────▼────────┐
│ Notebook do bar │          │       VPS         │          │ Celulares de   │
│ (só navegador)  │◄────────►│  Docker Compose   │◄────────►│ quem precisar  │
└─────────────────┘          │  ├─ frontend :80  │          └────────────────┘
                              │  │  (só na iface  │
                              │  │   Tailscale)   │
                              │  ├─ api (interno) │
                              │  └─ db (interno)  │
                              └───────────────────┘
```

Pontos-chave:

- O frontend só escuta na interface do Tailscale (`BIND_HOST` no `.env`),
  nunca em `0.0.0.0`. **Importante**: o Docker manipula o `iptables`
  diretamente e ignora regras do `ufw` para portas que ele mesmo publica —
  ou seja, "bloquear no firewall" não é suficiente por si só. Amarrar a
  publicação da porta ao IP do Tailscale é o que garante que não existe
  nenhuma rota de rede alcançável a partir da internet pública.
- API e banco não publicam porta nenhuma no host, só o frontend (nginx) fala
  com a API dentro da rede Docker interna.
- Quem acessa (notebook do bar, celulares autorizados) precisa ter o
  Tailscale instalado e logado na mesma conta/rede ("tailnet"). Sem isso, o
  IP nem responde.
- Com o MagicDNS do Tailscale ligado, o acesso é por nome
  (`http://area-verde`), não por IP — o IP interno pode mudar, o nome não.

## Pré-requisitos

- VPS Linux (Ubuntu 22.04+ é o que este guia assume; adapte os comandos de
  pacote se for outra distro), 1 vCPU / 2 GB RAM já é suficiente para o
  volume de um bar.
- Acesso root/sudo via SSH à VPS.
- Uma conta no [Tailscale](https://tailscale.com) (grátis até 100 dispositivos
  no plano pessoal — mais que suficiente aqui).

## Passo 1 — Instalar Docker na VPS

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

Saia e entre de novo no SSH para o grupo `docker` valer (evita precisar de
`sudo` em todo comando docker). Confirme com:

```bash
docker compose version
```

## Passo 2 — Instalar o Tailscale na VPS

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --hostname=area-verde
```

O comando abre um link — acesse-o no navegador do seu computador e autorize
o dispositivo na sua conta Tailscale. `--hostname=area-verde` já deixa o
nome amigável certo para o MagicDNS (em vez do hostname padrão da VPS).

Ligue o MagicDNS uma vez, pelo [admin console do Tailscale](https://login.tailscale.com/admin/dns)
→ "Enable MagicDNS". A partir daí, `http://area-verde` funciona em qualquer
dispositivo da sua tailnet.

Anote o IP Tailscale da VPS (vai precisar no Passo 4):

```bash
tailscale ip -4
```

## Passo 3 — Trazer o código para a VPS

```bash
sudo mkdir -p /opt/area-verde && sudo chown "$USER" /opt/area-verde
cd /opt/area-verde
git clone https://github.com/OtavioProcopio/area-verde.git backend
git clone https://github.com/OtavioProcopio/area-verde-frontend.git area-verde-frontend
```

A pasta do frontend precisa se chamar exatamente `area-verde-frontend` (é o
nome que `docker-compose.prod.yml` usa em `context: ../area-verde-frontend/app`).

Para usar a última release estável do backend:

```bash
cd /opt/area-verde/backend
git checkout v0.1.0
```

## Passo 4 — Configurar o `.env`

```bash
cd /opt/area-verde/backend
cp .env.prod.example .env
nano .env
```

Defina, no mínimo:

- `POSTGRES_PASSWORD`: uma senha forte de verdade (sem ela o Postgres recusa
  iniciar).
- `BIND_HOST`: o IP Tailscale anotado no Passo 2 (ex.: `100.87.23.4`). **Não
  use `0.0.0.0` numa VPS** — veja o aviso na Arquitetura acima.

## Passo 5 — Subir o sistema

```bash
cd /opt/area-verde/backend
docker compose -f docker-compose.prod.yml up --build -d
```

Builda as imagens, sobe Postgres + API + frontend, e aplica as migrations
automaticamente (`RUN_MIGRATIONS=true`).

## Passo 6 — Validar

```bash
docker compose -f docker-compose.prod.yml ps
curl http://$(tailscale ip -4)/health
```

Deve responder `{"status":"UP"}`. **Atenção**: como o frontend está amarrado
ao IP do Tailscale (não a `127.0.0.1` nem `0.0.0.0`), `curl http://localhost/health`
não vai funcionar a partir da própria VPS — use o IP do Tailscale mesmo, ou
acesse de outro dispositivo já conectado à tailnet.

Do notebook do bar (com Tailscale instalado, ver Passo 7): abra
`http://area-verde` no navegador. Deve aparecer a tela de acesso do Area
Verde.

## Passo 7 — Conectar o notebook do bar e os celulares

Em cada dispositivo que vai acessar o sistema:

1. Instale o Tailscale ([Windows](https://tailscale.com/download/windows),
   [Android](https://play.google.com/store/apps/details?id=com.tailscale.ipn),
   [iOS](https://apps.apple.com/app/tailscale/id1470499037)).
2. Faça login com a mesma conta/rede usada na VPS.
3. Autorize o dispositivo pelo [admin console](https://login.tailscale.com/admin/machines),
   se sua conta exigir aprovação manual.
4. Acesse `http://area-verde` no navegador — pronto.

No notebook Windows, para nunca precisar reabrir o Tailscale: ele já roda
como serviço e inicia com o Windows por padrão. Nos celulares, para evitar
que o Android mate a conexão em segundo plano (mais comum em Xiaomi/Samsung
com economia de bateria agressiva): desative a otimização de bateria para o
app Tailscale e ative "Always-on VPN" nas configurações de VPN do Android.

## Passo 8 — Garantir que sobe sozinho após reiniciar a VPS

```bash
sudo systemctl enable docker
sudo systemctl enable tailscaled
```

Os containers já têm `restart: unless-stopped`, então voltam a subir
automaticamente assim que o Docker inicia — não precisa recriar nada
manualmente após um reboot da VPS.

## Passo 9 — Backup automático

Os scripts `scripts/backup-postgres.sh` e `scripts/restore-postgres.sh`
cuidam do backup/restauração do Postgres (equivalentes Linux dos `.ps1`
usados no deploy on-premise).

### Agendar o backup diário via cron

```bash
crontab -e
```

Adicione (backup todo dia às 3h da manhã, fora do horário do bar):

```cron
0 3 * * * /opt/area-verde/backend/scripts/backup-postgres.sh >> /var/log/area-verde-backup.log 2>&1
```

Para também enviar uma cópia para outra máquina (chave SSH já configurada):

```bash
./scripts/backup-postgres.sh --remote usuario@outra-maquina.com
```

Por padrão os backups ficam em `/opt/area-verde/area-verde-backups/` (fora
dos repositórios git) com 14 dias de retenção local.

### Testar a restauração

Faça isso pelo menos uma vez antes de depender do sistema em produção:

```bash
cd /opt/area-verde/backend
./scripts/restore-postgres.sh ../area-verde-backups/area-verde_2026-09-12_03-00.sql.gz
```

## Passo 10 — Fluxo de atualização

```bash
cd /opt/area-verde/backend && git pull origin main
cd ../area-verde-frontend && git pull origin develop
cd ../backend
docker compose -f docker-compose.prod.yml up --build -d
```

## Checklist de release

- [ ] Docker instalado na VPS (`docker compose version` funciona).
- [ ] Tailscale instalado na VPS, com hostname amigável e MagicDNS ligado.
- [ ] Repositórios clonados em `/opt/area-verde/backend` e
      `/opt/area-verde/area-verde-frontend`.
- [ ] `.env` configurado com senha forte e `BIND_HOST` = IP Tailscale da VPS
      (nunca `0.0.0.0`).
- [ ] `docker compose -f docker-compose.prod.yml up --build -d` rodando sem erro.
- [ ] `curl http://<ip-tailscale>/health` responde `{"status":"UP"}`.
- [ ] `docker enable` + `tailscaled enable` para sobreviver a reboot da VPS.
- [ ] Tailscale instalado e autorizado no notebook do bar e nos celulares
      que vão acessar; acesso via `http://area-verde` confirmado.
- [ ] Cron de backup diário configurado.
- [ ] Um restore de teste executado com sucesso.
- [ ] Senha de acesso ao sistema trocada da padrão do MVP.

## Solução de problemas

**`curl http://localhost/health` não responde na própria VPS**
Esperado: o frontend está amarrado ao IP do Tailscale, não a `127.0.0.1`.
Use `curl http://$(tailscale ip -4)/health`.

**Container `db` fica reiniciando ("superuser password is not specified")**
O `.env` não foi criado ou está sem `POSTGRES_PASSWORD`. Repita o Passo 4.

**Não abre `http://area-verde` de um celular/notebook**
Confirme que o dispositivo está conectado à mesma tailnet
(`tailscale status` mostra todos os dispositivos) e que o MagicDNS está
ligado no admin console. Como teste, tente pelo IP direto
(`http://<ip-tailscale-da-vps>`) para isolar se o problema é MagicDNS ou
conectividade.

**Preciso apagar tudo e recomeçar do zero (perde os dados)**

```bash
docker compose -f docker-compose.prod.yml down -v
```
